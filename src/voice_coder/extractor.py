"""术语提取模块"""

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from voice_coder.config import CorpusConfig


# 正则表达式模式
PATTERNS = {
    # PascalCase / CamelCase: MyClass, HelloWorld, myVariable
    "pascal_camel": re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'),
    # lowerCamelCase: myVariable
    "lower_camel": re.compile(r'\b[a-z]+[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'),
    # snake_case: my_function, hello_world
    "snake_case": re.compile(r'\b[a-z]+(?:_[a-z]+)+\b'),
    # UPPER_SNAKE_CASE: MAX_SIZE, API_KEY
    "upper_snake": re.compile(r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)*\b'),
}


@dataclass
class ExtractedTerm:
    """提取的术语"""
    text: str
    count: int
    weight: float
    role: str  # pascal_camel, snake_case, upper_snake, etc.


@dataclass
class ExtractionResult:
    """提取结果"""
    terms: list[ExtractedTerm]
    total_files: int
    total_terms: int
    unique_terms: int


class TermExtractor:
    """
    术语提取器

    从代码文件中提取标识符并计算热词权重
    """

    # 权重计算参数
    BASE_WEIGHTS = {
        1: 5.0,
        2: 6.0,
        3: 7.0,
        5: 8.0,
        10: 9.0,
    }

    ROLE_BONUS = {
        "pascal_camel": 1.0,  # 类名
        "upper_snake": 0.5,   # 常量
        "snake_case": 0.8,    # 函数名
        "lower_camel": 0.8,   # 变量/函数名
    }

    MAX_WEIGHT = 10.0
    MIN_LENGTH = 3
    MAX_LENGTH = 30

    def __init__(self, config: CorpusConfig):
        """
        初始化提取器

        Args:
            config: 语料库配置
        """
        self.config = config

    def scan(self) -> ExtractionResult:
        """
        扫描语料库并提取术语

        Returns:
            提取结果
        """
        all_terms: Counter = Counter()
        term_roles: dict[str, set[str]] = {}
        file_count = 0

        for file_path in self._iter_files():
            file_count += 1
            try:
                content = self._read_file(file_path)
                for role, terms in self._extract_terms(content).items():
                    for term in terms:
                        if self.MIN_LENGTH <= len(term) <= self.MAX_LENGTH:
                            all_terms[term] += 1
                            if term not in term_roles:
                                term_roles[term] = set()
                            term_roles[term].add(role)
            except Exception:
                continue

        # 计算权重并生成结果
        extracted = []
        for term, count in all_terms.most_common():
            weight = self._calculate_weight(count, term_roles.get(term, set()))
            extracted.append(ExtractedTerm(
                text=term,
                count=count,
                weight=weight,
                role=",".join(term_roles.get(term, set())),
            ))

        return ExtractionResult(
            terms=extracted,
            total_files=file_count,
            total_terms=sum(all_terms.values()),
            unique_terms=len(all_terms),
        )

    def _iter_files(self) -> Iterator[Path]:
        """迭代语料库中的所有文件"""
        for base_path in self.config.paths:
            if not base_path.exists():
                continue

            for ext in self.config.extensions:
                for file_path in base_path.rglob(f"*{ext}"):
                    # 检查是否在排除目录中
                    if any(excluded in file_path.parts for excluded in self.config.exclude):
                        continue
                    yield file_path

    def _read_file(self, file_path: Path) -> str:
        """读取文件内容，尝试多种编码"""
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]

        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        return ""

    def _extract_terms(self, content: str) -> dict[str, list[str]]:
        """从内容中提取术语"""
        results: dict[str, list[str]] = {}

        for role, pattern in PATTERNS.items():
            matches = pattern.findall(content)
            results[role] = matches

        return results

    def _calculate_weight(self, count: int, roles: set[str]) -> float:
        """
        计算热词权重

        混合模式：频率 + 角色加成
        """
        # 基础权重（基于频率）
        base_weight = 5.0
        for threshold, weight in sorted(self.BASE_WEIGHTS.items(), reverse=True):
            if count >= threshold:
                base_weight = weight
                break

        # 角色加成
        role_bonus = 0.0
        for role in roles:
            role_bonus += self.ROLE_BONUS.get(role, 0.0)

        # 取最大角色加成（避免重复累加）
        role_bonus = min(role_bonus, 1.0)

        # 最终权重
        weight = base_weight + role_bonus

        return min(weight, self.MAX_WEIGHT)


def extract_hotwords(config: CorpusConfig) -> dict[str, float]:
    """
    从语料库提取热词

    Args:
        config: 语料库配置

    Returns:
        热词字典 {词汇: 权重}
    """
    extractor = TermExtractor(config)
    result = extractor.scan()

    return {term.text: term.weight for term in result.terms}


def save_hotwords(hotwords: dict[str, float], output_path: Path) -> None:
    """
    保存热词到文件

    Args:
        hotwords: 热词字典
        output_path: 输出文件路径（YAML 格式）
    """
    import yaml

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump({"hotwords": hotwords}, f, allow_unicode=True, default_flow_style=False)


def load_hotwords(hotwords_path: Path) -> dict[str, float]:
    """
    从文件加载热词

    Args:
        hotwords_path: 热词文件路径

    Returns:
        热词字典
    """
    import yaml

    if not hotwords_path.exists():
        return {}

    with open(hotwords_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data.get("hotwords", {})


class IncrementalExtractor:
    """
    增量术语提取器

    支持初始全量扫描和增量更新，用于文件监控场景
    """

    def __init__(self, config: CorpusConfig):
        """
        初始化增量提取器

        Args:
            config: 语料库配置
        """
        self.config = config
        self._term_counter: Counter = Counter()
        self._term_roles: dict[str, set[str]] = {}
        self._file_terms: dict[Path, dict[str, set[str]]] = {}

    def initial_scan(self) -> dict[str, float]:
        """
        初始全量扫描

        Returns:
            初始热词字典
        """
        self._term_counter.clear()
        self._term_roles.clear()
        self._file_terms.clear()

        for file_path in self._iter_files():
            self._process_file(file_path)

        return self._build_hotwords()

    def update_files(self, file_paths: set[Path]) -> dict[str, float]:
        """
        增量更新文件

        Args:
            file_paths: 变化的文件路径集合

        Returns:
            更新后的热词字典
        """
        for file_path in file_paths:
            # 检查文件是否在监控范围内
            if not self._should_watch(file_path):
                continue

            # 移除该文件的旧术语
            if file_path in self._file_terms:
                self._remove_file_terms(file_path)

            # 如果文件存在，提取新术语
            if file_path.exists():
                self._process_file(file_path)

        return self._build_hotwords()

    def _should_watch(self, file_path: Path) -> bool:
        """检查文件是否应该被监控"""
        # 检查扩展名
        if file_path.suffix not in self.config.extensions:
            return False

        # 检查是否在排除目录中
        if any(excluded in file_path.parts for excluded in self.config.exclude):
            return False

        # 检查是否在监控路径内
        for base_path in self.config.paths:
            try:
                file_path.relative_to(base_path)
                return True
            except ValueError:
                continue

        return False

    def _process_file(self, file_path: Path) -> None:
        """处理单个文件，提取术语"""
        try:
            content = self._read_file(file_path)
            terms_by_role: dict[str, set[str]] = {}

            for role, pattern in PATTERNS.items():
                matches = set(pattern.findall(content))
                # 过滤长度
                matches = {m for m in matches if 3 <= len(m) <= 30}
                if matches:
                    terms_by_role[role] = matches

            # 记录文件的术语
            self._file_terms[file_path] = terms_by_role

            # 更新全局计数
            for role, terms in terms_by_role.items():
                for term in terms:
                    self._term_counter[term] += 1
                    if term not in self._term_roles:
                        self._term_roles[term] = set()
                    self._term_roles[term].add(role)

        except Exception:
            pass

    def _remove_file_terms(self, file_path: Path) -> None:
        """移除文件的术语"""
        if file_path not in self._file_terms:
            return

        old_terms = self._file_terms[file_path]
        for role, terms in old_terms.items():
            for term in terms:
                self._term_counter[term] -= 1
                if self._term_counter[term] <= 0:
                    del self._term_counter[term]
                    self._term_roles.pop(term, None)

        del self._file_terms[file_path]

    def _read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return ""

    def _iter_files(self) -> Iterator[Path]:
        """迭代语料库中的所有文件"""
        for base_path in self.config.paths:
            if not base_path.exists():
                continue
            for ext in self.config.extensions:
                for file_path in base_path.rglob(f"*{ext}"):
                    if any(excluded in file_path.parts for excluded in self.config.exclude):
                        continue
                    yield file_path

    def _build_hotwords(self) -> dict[str, float]:
        """构建热词字典"""
        hotwords = {}
        for term, count in self._term_counter.items():
            if count > 0:
                weight = self._calculate_weight(count, self._term_roles.get(term, set()))
                hotwords[term] = weight
        return hotwords

    def _calculate_weight(self, count: int, roles: set[str]) -> float:
        """计算热词权重"""
        BASE_WEIGHTS = {1: 5.0, 2: 6.0, 3: 7.0, 5: 8.0, 10: 9.0}
        ROLE_BONUS = {"pascal_camel": 1.0, "upper_snake": 0.5, "snake_case": 0.8, "lower_camel": 0.8}

        base_weight = 5.0
        for threshold, weight in sorted(BASE_WEIGHTS.items(), reverse=True):
            if count >= threshold:
                base_weight = weight
                break

        role_bonus = min(sum(ROLE_BONUS.get(r, 0.0) for r in roles), 1.0)
        return min(base_weight + role_bonus, 10.0)

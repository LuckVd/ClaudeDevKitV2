"""术语提取模块测试"""

import tempfile
from pathlib import Path

import pytest

from voice_coder.config import CorpusConfig
from voice_coder.extractor import (
    ExtractionResult,
    TermExtractor,
    extract_hotwords,
    load_hotwords,
    save_hotwords,
)


class TestTermExtractor:
    """测试术语提取器"""

    def test_extract_camel_case(self, tmp_path: Path):
        """测试 CamelCase 提取"""
        # 创建测试文件
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class MyClass:
    def myMethod(self):
        HelloWorld = 1
        return HelloWorld
""")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = TermExtractor(config)
        result = extractor.scan()

        # 验证提取结果
        assert "MyClass" in [t.text for t in result.terms]
        assert "HelloWorld" in [t.text for t in result.terms]

    def test_extract_snake_case(self, tmp_path: Path):
        """测试 snake_case 提取"""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def my_function():
    hello_world = 1
    return hello_world
""")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = TermExtractor(config)
        result = extractor.scan()

        assert "my_function" in [t.text for t in result.terms]
        assert "hello_world" in [t.text for t in result.terms]

    def test_extract_upper_snake(self, tmp_path: Path):
        """测试 UPPER_SNAKE 提取"""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
MAX_SIZE = 100
API_KEY = "secret"
DEFAULT_TIMEOUT = 30
""")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = TermExtractor(config)
        result = extractor.scan()

        assert "MAX_SIZE" in [t.text for t in result.terms]
        assert "API_KEY" in [t.text for t in result.terms]

    def test_exclude_directories(self, tmp_path: Path):
        """测试排除目录"""
        # 创建文件在 node_modules 中
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        excluded_file = node_modules / "test.js"
        excluded_file.write_text("const MyComponent = 1;")

        # 创建正常文件
        normal_file = tmp_path / "test.js"
        normal_file.write_text("const NormalComponent = 2;")

        config = CorpusConfig(
            paths=[tmp_path],
            extensions=[".js"],
            exclude=["node_modules"],
        )
        extractor = TermExtractor(config)
        result = extractor.scan()

        # node_modules 中的文件应该被排除
        assert "MyComponent" not in [t.text for t in result.terms]
        assert "NormalComponent" in [t.text for t in result.terms]

    def test_weight_calculation(self, tmp_path: Path):
        """测试权重计算"""
        # 创建包含多次出现的术语
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class ImportantClass:
    pass

ImportantClass()
ImportantClass()
ImportantClass()
ImportantClass()
""")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        extractor = TermExtractor(config)
        result = extractor.scan()

        # 查找 ImportantClass 的权重
        for term in result.terms:
            if term.text == "ImportantClass":
                # PascalCase 角色加成 + 出现多次
                assert term.weight >= 7.0  # 基础权重 + 角色加成
                break

    def test_multiple_extensions(self, tmp_path: Path):
        """测试多种文件类型"""
        py_file = tmp_path / "test.py"
        py_file.write_text("class PythonClass: pass")

        js_file = tmp_path / "test.js"
        js_file.write_text("const JavaScriptVar = 1;")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py", ".js"])
        extractor = TermExtractor(config)
        result = extractor.scan()

        assert "PythonClass" in [t.text for t in result.terms]
        assert "JavaScriptVar" in [t.text for t in result.terms]


class TestExtractHotwords:
    """测试热词提取函数"""

    def test_extract_hotwords_basic(self, tmp_path: Path):
        """测试基本热词提取"""
        test_file = tmp_path / "test.py"
        test_file.write_text("class MyClass: pass")

        config = CorpusConfig(paths=[tmp_path], extensions=[".py"])
        hotwords = extract_hotwords(config)

        assert "MyClass" in hotwords
        assert hotwords["MyClass"] > 0


class TestSaveLoadHotwords:
    """测试热词保存和加载"""

    def test_save_and_load(self, tmp_path: Path):
        """测试保存和加载热词"""
        hotwords = {
            "MyClass": 10.0,
            "my_function": 8.5,
            "MAX_SIZE": 7.0,
        }

        output_file = tmp_path / "hotwords.yaml"
        save_hotwords(hotwords, output_file)

        # 验证文件存在
        assert output_file.exists()

        # 加载并验证
        loaded = load_hotwords(output_file)
        assert loaded["MyClass"] == 10.0
        assert loaded["my_function"] == 8.5
        assert loaded["MAX_SIZE"] == 7.0

    def test_load_nonexistent_file(self, tmp_path: Path):
        """测试加载不存在的文件"""
        result = load_hotwords(tmp_path / "nonexistent.yaml")
        assert result == {}

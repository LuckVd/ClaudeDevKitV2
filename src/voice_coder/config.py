"""配置管理模块"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AudioConfig:
    """音频配置"""
    sample_rate: int = 16000
    channels: int = 1
    frames_per_buffer: int = 4096


@dataclass
class Config:
    """主配置"""
    model_path: Path
    hotwords: dict[str, float] = field(default_factory=dict)
    audio: AudioConfig = field(default_factory=AudioConfig)


def expand_path(path: str | Path) -> Path:
    """展开路径中的 ~ 和环境变量"""
    return Path(path).expanduser().resolve()


def load_config(config_path: str | Path) -> Config:
    """
    从 YAML 文件加载配置

    Args:
        config_path: 配置文件路径

    Returns:
        Config 对象

    Raises:
        FileNotFoundError: 配置文件不存在
        KeyError: 缺少必填配置项
    """
    path = expand_path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # 解析模型路径（必填）
    if "model" not in data or "path" not in data["model"]:
        raise KeyError("缺少必填配置项: model.path")

    model_path = expand_path(data["model"]["path"])

    # 解析热词
    hotwords: dict[str, float] = {}
    if "hotwords" in data:
        for word, weight in data["hotwords"].items():
            hotwords[word] = float(weight)

    # 解析音频配置
    audio_data = data.get("audio", {})
    audio = AudioConfig(
        sample_rate=audio_data.get("sample_rate", 16000),
        channels=audio_data.get("channels", 1),
        frames_per_buffer=audio_data.get("frames_per_buffer", 4096),
    )

    return Config(
        model_path=model_path,
        hotwords=hotwords,
        audio=audio,
    )


def get_default_config_path() -> Path:
    """获取默认配置文件路径"""
    return Path.home() / ".config" / "voice-coder" / "config.yaml"

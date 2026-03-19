"""配置模块测试"""

import tempfile
from pathlib import Path

import pytest
import yaml

from voice_coder.config import (
    AudioConfig,
    Config,
    expand_path,
    get_default_config_path,
    load_config,
)


class TestExpandPath:
    """测试路径展开功能"""

    def test_expand_home(self):
        """测试 ~ 展开"""
        result = expand_path("~/test")
        assert str(result).startswith(str(Path.home()))

    def test_no_expand_needed(self):
        """测试无需展开的路径"""
        result = expand_path("/tmp/test")
        assert result == Path("/tmp/test")


class TestLoadConfig:
    """测试配置加载"""

    def test_load_minimal_config(self, tmp_path: Path):
        """测试最小配置"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
model:
  path: /path/to/model
""")

        config = load_config(config_file)

        assert config.model_path == Path("/path/to/model")
        assert config.hotwords == {}
        assert config.audio.sample_rate == 16000
        assert config.audio.channels == 1
        assert config.audio.frames_per_buffer == 4096

    def test_load_full_config(self, tmp_path: Path):
        """测试完整配置"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
model:
  path: ~/models/vosk-model-small-cn-0.3

hotwords:
  函数: 10.0
  变量: 9.0
  循环: 8.5

audio:
  sample_rate: 16000
  channels: 1
  frames_per_buffer: 8192
""")

        config = load_config(config_file)

        assert "函数" in config.model_path.name or "vosk" in str(config.model_path)
        assert config.hotwords == {"函数": 10.0, "变量": 9.0, "循环": 8.5}
        assert config.audio.frames_per_buffer == 8192

    def test_file_not_found(self):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_missing_model_path(self, tmp_path: Path):
        """测试缺少模型路径"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("audio:\n  sample_rate: 16000\n")

        with pytest.raises(KeyError, match="model.path"):
            load_config(config_file)

    def test_empty_file(self, tmp_path: Path):
        """测试空文件"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(KeyError):
            load_config(config_file)


class TestGetDefaultConfigPath:
    """测试默认配置路径"""

    def test_default_path(self):
        """测试默认路径格式"""
        path = get_default_config_path()
        assert ".config/voice-coder/config.yaml" in str(path)

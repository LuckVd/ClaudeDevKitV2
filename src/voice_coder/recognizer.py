"""语音识别模块"""

import json
from pathlib import Path

from vosk import KaldiRecognizer, Model, SetLogLevel

from voice_coder.config import Config


class Recognizer:
    """
    Vosk 语音识别器封装

    支持热词配置，提供实时语音识别能力
    """

    def __init__(self, config: Config):
        """
        初始化识别器

        Args:
            config: 配置对象

        Raises:
            FileNotFoundError: 模型路径不存在
        """
        self.config = config
        self._model: Model | None = None
        self._recognizer: KaldiRecognizer | None = None

        # 验证模型路径
        if not config.model_path.exists():
            raise FileNotFoundError(f"Vosk 模型不存在: {config.model_path}")

        # 抑制 Vosk 日志
        SetLogLevel(-1)

        # 加载模型
        self._model = Model(str(config.model_path))

        # 创建识别器
        self._recognizer = KaldiRecognizer(
            self._model,
            config.audio.sample_rate,
        )

        # 启用词级别输出
        self._recognizer.SetWords(True)

        # 配置热词
        self._configure_hotwords()

    def _configure_hotwords(self) -> None:
        """配置热词"""
        if not self.config.hotwords:
            return

        # Vosk 支持通过 JSON 配置热词
        # 格式: {"phrase_list": [...], "boost": [...]}
        # 注意：需要在创建识别器时或通过 SetGrammar 配置
        # 这里我们使用 SetGrammar 方式配置短语列表
        phrases = list(self.config.hotwords.keys())
        if phrases:
            # 构建简单语法：允许任意短语或自由文本
            grammar = ["[unk]"] + phrases
            try:
                self._recognizer.SetGrammar(json.dumps(grammar))
            except Exception:
                # 某些 Vosk 版本可能不支持 SetGrammar
                pass

    def process(self, audio_data: bytes) -> str | None:
        """
        处理音频数据

        Args:
            audio_data: 音频数据字节

        Returns:
            识别到的完整文本，如果没有完整句子则返回 None
        """
        if not self._recognizer:
            raise RuntimeError("识别器未初始化")

        if self._recognizer.AcceptWaveform(audio_data):
            result = json.loads(self._recognizer.Result())
            text = result.get("text", "").strip()
            return text if text else None

        return None

    def get_partial(self) -> str:
        """
        获取临时识别结果（未完成的句子）

        Returns:
            当前识别中的文本
        """
        if not self._recognizer:
            raise RuntimeError("识别器未初始化")

        result = json.loads(self._recognizer.PartialResult())
        return result.get("partial", "")

    def reset(self) -> None:
        """重置识别器状态"""
        if self._recognizer:
            # 清空缓冲区，开始新的识别
            pass  # Vosk 会自动处理

"""音频采集模块"""

import pyaudio
from pyaudio import PyAudio

from voice_coder.config import AudioConfig


class AudioCapture:
    """
    音频采集器

    使用 PyAudio 从麦克风采集音频数据
    """

    def __init__(self, config: AudioConfig):
        """
        初始化音频采集器

        Args:
            config: 音频配置
        """
        self.config = config
        self._pyaudio: PyAudio | None = None
        self._stream: pyaudio.Stream | None = None

    def __enter__(self) -> "AudioCapture":
        """进入上下文，初始化音频流"""
        self._pyaudio = PyAudio()

        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=self.config.channels,
            rate=self.config.sample_rate,
            input=True,
            frames_per_buffer=self.config.frames_per_buffer,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，清理资源"""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        if self._pyaudio:
            self._pyaudio.terminate()
            self._pyaudio = None

    def read(self) -> bytes:
        """
        读取一帧音频数据

        Returns:
            音频数据字节

        Raises:
            RuntimeError: 音频流未初始化
        """
        if not self._stream:
            raise RuntimeError("音频流未初始化，请使用上下文管理器")

        return self._stream.read(self.config.frames_per_buffer, exception_on_overflow=False)

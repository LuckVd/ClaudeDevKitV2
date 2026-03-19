"""键盘输出模块"""

import subprocess
import shutil
from typing import Optional


class KeyboardEmitter:
    """
    键盘模拟输出器

    使用 ydotool 模拟键盘输入
    """

    def __init__(self):
        """初始化键盘输出器"""
        self._ydotool_path: Optional[str] = None

    def _find_ydotool(self) -> str:
        """
        查找 ydotool 可执行文件

        Returns:
            ydotool 路径

        Raises:
            FileNotFoundError: ydotool 未安装
        """
        if self._ydotool_path:
            return self._ydotool_path

        path = shutil.which("ydotool")
        if not path:
            raise FileNotFoundError(
                "ydotool 未安装。请运行: sudo apt install ydotool"
            )

        self._ydotool_path = path
        return path

    def type_text(self, text: str) -> None:
        """
        模拟键盘输入文本

        Args:
            text: 要输入的文本

        Raises:
            RuntimeError: ydotool 执行失败
        """
        if not text:
            return

        ydotool = self._find_ydotool()

        try:
            # 使用 ydotool type 命令输入文本
            result = subprocess.run(
                [ydotool, "type", "--key-delay", "0", text],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ydotool 执行失败: {e.stderr}") from e

    def type_key(self, key: str) -> None:
        """
        模拟按键

        Args:
            key: 按键名称（如 "Return", "space", "BackSpace"）

        Raises:
            RuntimeError: ydotool 执行失败
        """
        ydotool = self._find_ydotool()

        try:
            subprocess.run(
                [ydotool, "key", key],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ydotool 执行失败: {e.stderr}") from e

"""CLI 控制模块"""

import signal
import sys
from pathlib import Path

import click

from voice_coder import __version__
from voice_coder.audio import AudioCapture
from voice_coder.config import get_default_config_path, load_config
from voice_coder.emitter import KeyboardEmitter
from voice_coder.recognizer import Recognizer


# 全局状态，用于信号处理
_running = False


def signal_handler(signum, frame):
    """处理终止信号"""
    global _running
    _running = False
    click.echo("\n正在停止...")


@click.group()
@click.version_option(version=__version__)
def main():
    """VoiceCoder - 项目感知型语音输入工具"""
    pass


@main.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="配置文件路径（默认: ~/.config/voice-coder/config.yaml）",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="显示详细输出",
)
def start(config_path: str | None, verbose: bool):
    """
    启动语音识别

    从麦克风采集音频，识别后自动输入到当前焦点窗口。
    按 Ctrl+C 停止。
    """
    global _running

    # 确定配置文件路径
    if config_path:
        cfg_path = Path(config_path)
    else:
        cfg_path = get_default_config_path()

    # 加载配置
    try:
        config = load_config(cfg_path)
    except FileNotFoundError as e:
        click.echo(f"错误: {e}", err=True)
        click.echo(f"请创建配置文件: {get_default_config_path()}", err=True)
        sys.exit(1)
    except KeyError as e:
        click.echo(f"配置错误: {e}", err=True)
        sys.exit(1)

    if verbose:
        click.echo(f"模型路径: {config.model_path}")
        click.echo(f"热词数量: {len(config.hotwords)}")
        click.echo(f"采样率: {config.audio.sample_rate}")

    # 初始化识别器
    try:
        recognizer = Recognizer(config)
    except FileNotFoundError as e:
        click.echo(f"错误: {e}", err=True)
        click.echo("请运行下载脚本获取 Vosk 模型:", err=True)
        click.echo("  ./scripts/download_model.sh ~/.local/share/voice-coder/models", err=True)
        sys.exit(1)

    # 初始化键盘输出器
    emitter = KeyboardEmitter()

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    click.echo("语音识别已启动，按 Ctrl+C 停止...")
    click.echo("对着麦克风说话，识别结果将自动输入到当前窗口。")

    _running = True

    try:
        with AudioCapture(config.audio) as capture:
            while _running:
                # 读取音频数据
                audio_data = capture.read()

                # 处理识别
                text = recognizer.process(audio_data)

                if text:
                    if verbose:
                        click.echo(f"识别: {text}")

                    # 输出到当前窗口
                    emitter.type_text(text)

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)

    click.echo("语音识别已停止。")


@main.command()
def stop():
    """
    停止语音识别

    发送终止信号给正在运行的 voice-coder 进程。
    """
    import os
    import signal as sig

    # 查找 voice-coder 进程
    try:
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "voice-coder start"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            click.echo("没有找到正在运行的 voice-coder 进程")
            return

        pids = result.stdout.strip().split("\n")
        pids = [p for p in pids if p and p != str(os.getpid())]

        if not pids:
            click.echo("没有找到正在运行的 voice-coder 进程")
            return

        for pid in pids:
            os.kill(int(pid), sig.SIGTERM)
            click.echo(f"已发送停止信号给进程 {pid}")

    except Exception as e:
        click.echo(f"停止失败: {e}", err=True)


if __name__ == "__main__":
    main()

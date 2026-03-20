"""CLI 控制模块"""

import signal
import sys
from pathlib import Path

import click

from voice_coder import __version__
from voice_coder.audio import AudioCapture
from voice_coder.config import CorpusConfig, get_default_config_path, load_config
from voice_coder.emitter import KeyboardEmitter
from voice_coder.extractor import extract_hotwords, save_hotwords
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


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(),
    default=None,
    help="热词输出文件路径（默认: ~/.config/voice-coder/hotwords.yaml）",
)
@click.option(
    "-e",
    "--extensions",
    multiple=True,
    default=[".py", ".js", ".ts", ".md"],
    help="要扫描的文件扩展名（可多次指定）",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="显示详细输出",
)
def scan(path: str, output_path: str | None, extensions: tuple[str, ...], verbose: bool):
    """
    扫描项目目录提取术语

    从指定目录扫描代码文件，提取标识符作为热词。
    结果保存到热词文件，供 start 命令使用。

    示例:
      voice-coder scan ~/projects/my-project
      voice-coder scan . -o ./hotwords.yaml
    """
    scan_path = Path(path).resolve()

    # 确定输出路径
    if output_path:
        out_path = Path(output_path)
    else:
        out_path = Path.home() / ".config" / "voice-coder" / "hotwords.yaml"

    if verbose:
        click.echo(f"扫描目录: {scan_path}")
        click.echo(f"文件类型: {', '.join(extensions)}")
        click.echo(f"输出文件: {out_path}")

    # 创建语料库配置
    corpus_config = CorpusConfig(
        paths=[scan_path],
        extensions=list(extensions),
    )

    # 提取热词
    click.echo("正在扫描...")
    hotwords = extract_hotwords(corpus_config)

    if not hotwords:
        click.echo("未提取到任何术语")
        return

    # 保存热词
    save_hotwords(hotwords, out_path)

    # 统计信息
    click.echo(f"\n✓ 扫描完成")
    click.echo(f"  提取术语: {len(hotwords)} 个")
    click.echo(f"  输出文件: {out_path}")

    if verbose:
        # 显示权重分布
        weights = sorted(set(hotwords.values()), reverse=True)
        click.echo(f"\n权重分布:")
        for w in weights[:5]:
            count = sum(1 for v in hotwords.values() if v == w)
            click.echo(f"  权重 {w:.1f}: {count} 个术语")


if __name__ == "__main__":
    main()

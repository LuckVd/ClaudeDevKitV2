# VoiceCoder

项目感知型语音输入工具，能够识别项目专属术语并自动学习新词。

## 功能特性

- 🎤 实时语音识别（Vosk 中文模型）
- 📝 动态热词机制（提升项目术语识别率）
- 🔍 项目语料库扫描（自动提取关键词）
- ⌨️ 模拟键盘输入（Linux 桌面）
- 🖥️ CLI 控制接口

## 系统要求

- Linux 桌面环境
- Python 3.10+
- PulseAudio 或 PipeWire
- ydotool（用于键盘模拟）

## 快速开始

### 1. 安装依赖

```bash
# 系统依赖
sudo apt install python3-pyaudio ydotool

# Python 依赖
pip install -e .
```

### 2. 下载语音模型

```bash
./scripts/download_model.sh ~/.local/share/voice-coder/models
```

### 3. 创建配置文件

```bash
mkdir -p ~/.config/voice-coder
cat > ~/.config/voice-coder/config.yaml << 'EOF'
model:
  path: ~/.local/share/voice-coder/models/vosk-model-small-cn-0.3

hotwords:
  函数: 10.0
  变量: 9.0
  循环: 9.0

audio:
  sample_rate: 16000
  channels: 1
  frames_per_buffer: 4096
EOF
```

### 4. 启动语音识别

```bash
voice-coder start
```

对着麦克风说话，识别结果将自动输入到当前焦点窗口。

## CLI 命令

```bash
voice-coder start          # 启动语音识别
voice-coder stop           # 停止语音识别
voice-coder --help         # 显示帮助
```

## 配置说明

配置文件路径：`~/.config/voice-coder/config.yaml`

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `model.path` | Vosk 模型路径 | 必填 |
| `hotwords` | 热词及权重 | 可选 |
| `audio.sample_rate` | 采样率 | 16000 |
| `audio.channels` | 声道数 | 1 |
| `audio.frames_per_buffer` | 缓冲区大小 | 4096 |

## 开发

```bash
# 安装开发依赖
pip install -e “.[dev]”

# 运行测试
pytest

# 代码覆盖率
pytest --cov=voice_coder
```

## 许可证

MIT License

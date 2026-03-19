#!/bin/bash
#
# Vosk 中文语音模型下载脚本
#
# 用法:
#   ./scripts/download_model.sh [目标路径]
#
# 示例:
#   ./scripts/download_model.sh ~/.local/share/voice-coder/models
#

set -e

# 默认模型
MODEL_NAME="vosk-model-small-cn-0.3"
MODEL_URL="https://alphacephei.com/vosk/models/${MODEL_NAME}.zip"

# 目标路径
TARGET_DIR="${1:-$HOME/.local/share/voice-coder/models}"

# 创建目标目录
mkdir -p "$TARGET_DIR"

echo "=== Vosk 中文模型下载脚本 ==="
echo ""
echo "模型: $MODEL_NAME"
echo "目标: $TARGET_DIR"
echo ""

# 检查是否已下载
if [ -d "$TARGET_DIR/$MODEL_NAME" ]; then
    echo "模型已存在: $TARGET_DIR/$MODEL_NAME"
    read -p "是否重新下载？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消下载"
        exit 0
    fi
    rm -rf "$TARGET_DIR/$MODEL_NAME"
fi

# 下载
echo "正在下载..."
cd "$TARGET_DIR"

if command -v wget &> /dev/null; then
    wget -q --show-progress "$MODEL_URL" -O "${MODEL_NAME}.zip"
elif command -v curl &> /dev/null; then
    curl -L --progress-bar "$MODEL_URL" -o "${MODEL_NAME}.zip"
else
    echo "错误: 需要 wget 或 curl"
    exit 1
fi

# 解压
echo "正在解压..."
unzip -q "${MODEL_NAME}.zip"

# 清理
rm "${MODEL_NAME}.zip"

echo ""
echo "✓ 下载完成!"
echo ""
echo "模型路径: $TARGET_DIR/$MODEL_NAME"
echo ""
echo "配置文件示例:"
echo ""
cat << EOF
model:
  path: $TARGET_DIR/$MODEL_NAME

hotwords:
  函数: 10.0
  变量: 9.0
  循环: 9.0

audio:
  sample_rate: 16000
  channels: 1
  frames_per_buffer: 4096
EOF
echo ""

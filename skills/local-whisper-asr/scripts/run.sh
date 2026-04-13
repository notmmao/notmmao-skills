#!/bin/bash
set -e

# 缓存目录
CACHE_DIR="$HOME/.cache/local-whisper-asr"
mkdir -p "$CACHE_DIR"

# 默认参数
MODEL="small"
LANGUAGE="zh"
OUTPUT_DIR="$CACHE_DIR"
FORMATS="txt,srt,vtt,json"

# 参数解析
while [[ $# -gt 0 ]]; do
  case $1 in
    --input|-i)
      INPUT="$2"
      shift 2
      ;;
    --model|-m)
      MODEL="$2"
      shift 2
      ;;
    --language|-l)
      LANGUAGE="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --formats|-f)
      FORMATS="$2"
      shift 2
      ;;
    *)
      echo "未知参数: $1"
      exit 1
      ;;
  esac
done

# 检查必填参数
if [[ -z "$INPUT" ]]; then
  echo "错误：必须指定输入资源 --input <文件路径/URL>"
  exit 1
fi

# 依赖检查
check_dependency() {
  if ! command -v "$1" &> /dev/null; then
    echo "错误：依赖 $1 未安装，请先安装：$2"
    exit 1
  fi
}

check_dependency "whisper" "pip install openai-whisper"
check_dependency "ffmpeg" "sudo apt install ffmpeg / brew install ffmpeg"
check_dependency "wget" "sudo apt install wget / brew install wget"
check_dependency "md5sum" "sudo apt install coreutils / brew install coreutils"

# 处理输入
echo "🔍 处理输入资源: $INPUT"
if [[ "$INPUT" =~ ^https?:// ]]; then
  # URL输入，下载到缓存
  INPUT_MD5=$(echo -n "$INPUT" | md5sum | awk '{print $1}')
  INPUT_FILE="$CACHE_DIR/$INPUT_MD5.input"
  if [[ -f "$INPUT_FILE" ]]; then
    echo "✅ 资源已存在缓存，跳过下载"
  else
    echo "📥 下载资源到本地缓存..."
    wget -q -O "$INPUT_FILE" "$INPUT"
  fi
else
  # 本地文件输入
  if [[ ! -f "$INPUT" ]]; then
    echo "错误：本地文件不存在: $INPUT"
    exit 1
  fi
  INPUT_MD5=$(md5sum "$INPUT" | awk '{print $1}')
  INPUT_FILE="$INPUT"
fi

# 检查缓存
CACHE_KEY="${INPUT_MD5}_${MODEL}_${LANGUAGE}"
CACHE_PATH="$CACHE_DIR/$CACHE_KEY"
if [[ -f "$CACHE_PATH.txt" ]]; then
  echo "✅ 该资源已转写过，直接返回缓存结果"
  # 复制到输出目录
  for fmt in $(echo "$FORMATS" | tr ',' ' '); do
    cp "$CACHE_PATH.$fmt" "$OUTPUT_DIR/"
  done
  echo "🎉 转写完成，结果已保存到: $OUTPUT_DIR"
  echo "📄 纯文本结果预览:"
  head -20 "$CACHE_PATH.txt"
  exit 0
fi

# 执行转写
echo "🎤 开始语音转写，模型: $MODEL，语言: $LANGUAGE..."
whisper "$INPUT_FILE" \
  --model "$MODEL" \
  --language "$LANGUAGE" \
  --output_dir "$CACHE_DIR" \
  --output_format all

# 重命名缓存文件
for fmt in txt srt vtt json; do
  base_name=$(basename "$INPUT_FILE")
  mv "$CACHE_DIR/${base_name%.*}.$fmt" "$CACHE_PATH.$fmt"
done

# 复制到输出目录
for fmt in $(echo "$FORMATS" | tr ',' ' '); do
  cp "$CACHE_PATH.$fmt" "$OUTPUT_DIR/"
done

echo "🎉 转写完成，结果已保存到: $OUTPUT_DIR"
echo "📄 纯文本结果预览:"
head -20 "$CACHE_PATH.txt"

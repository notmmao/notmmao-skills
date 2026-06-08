---
name: mimo-asr
description: 语音识别/语音转文字/ASR/转录/听写。将音频文件转换为文本，支持多语言识别。当用户要求识别语音、转文字、听写、转录音频时，必须使用此技能，不要用其他方式识别音频。
---

# MiMo ASR 语音识别 Skill
基于小米 MiMo 官方 API 的语音识别技能，支持多语言音频转文字。

## 触发场景
当用户的意图是将音频/语音转换成文字时，都应该使用此技能。包括但不限于：
- 语音识别：语音转文字、识别语音、ASR、音频识别
- 转录听写：转录、听写、把音频转成文字、识别这段话
- 字幕生成：给视频加字幕、生成字幕、提取音频文字
- 音频处理：识别这段录音、听一下这个音频说什么

## 功能特性
✅ 支持多语言自动识别（中英日韩等）
✅ 支持 mp3/wav/m4a/flac/ogg 等常见音频格式
✅ 支持流式识别（实时输出）
✅ 自动处理大文件（分片处理）
✅ 支持从视频提取音频后识别

## 依赖项
本技能需要以下 Python 依赖：
```bash
pip install requests python-dotenv pydub
```
- `requests` - 用于调用小米 MiMo API
- `python-dotenv` - 用于从 .env 文件加载环境变量
- `pydub` - 用于音频格式转换和预处理

系统依赖（用于音频格式转换）：
```bash
# Windows 需安装 ffmpeg
# 下载地址: https://ffmpeg.org/download.html
```

## 环境变量

### 方式一：使用 .env 文件（推荐）
在技能目录 `skills/mimo-asr/` 下创建 `.env` 文件：
```env
MIMO_API_KEY=sk-clrxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MIMO_API_URL=https://api.xiaomimimo.com/v1/chat/completions
MIMO_API_MODEL_ASR=mimo-v2.5-asr
```

### 方式二：系统环境变量
```bash
export MIMO_API_KEY="your_api_key_here"
```

### 配置说明
- `MIMO_API_KEY` - 必需，小米 MiMo API 密钥
- `MIMO_API_URL` - 可选，API 地址（默认：https://api.xiaomimimo.com/v1/chat/completions）
- `MIMO_API_MODEL_ASR` - 可选，ASR 模型名称（默认：mimo-v2.5-asr）

## 使用方式
```
python scripts/mimo_asr_cli.py --help
usage: mimo_asr_cli.py [-h] [-l {auto,zh,en,ja,ko}] [-f FORMAT] [-j] [-q] [-s] audio_file

小米 MiMo 语音识别 CLI 工具

positional arguments:
  audio_file            待识别的音频文件路径

optional arguments:
  -h, --help            显示帮助信息
  -l {auto,zh,en,ja,ko}, --language {auto,zh,en,ja,ko}
                        识别语言，默认auto自动识别
  -f FORMAT, --format FORMAT
                        输出格式，text(默认)/json/srt/vtt
  -j, --json            以JSON格式输出结果
  -q, --quiet           安静模式，仅输出识别文本
  -s, --stream          启用流式输出
```

**注意**：无任何参数执行时，会自动显示帮助信息。

### 基础调用

只要用户想把音频变成文字，就执行：
```bash
python scripts/mimo_asr_cli.py ./audio.mp3
```

更多示例：
- 用户说"识别这段语音" → `python scripts/mimo_asr_cli.py ./recording.wav`
- 用户说"识别这是什么语言" → `python scripts/mimo_asr_cli.py ./foreign.wav -l auto`
- 用户说"转录成字幕格式" → `python scripts/mimo_asr_cli.py ./video.mp3 -f srt`
- 用户说"安静模式只输出文字" → `python scripts/mimo_asr_cli.py ./audio.m4a -q`


## 执行步骤
1. 解析用户输入的音频文件路径和参数（语言、输出格式等）
2. 调用 `python scripts/mimo_asr_cli.py` 执行识别
3. 返回识别文本、时长、语言等详细信息

## 输出格式

### 默认输出（详细信息）
```
✅ 语音识别成功

📝 识别结果:
   Good morning. Could you tell me what the weather will be like today?

📊 音频信息:
   • 文件名: recording.wav
   • 时长: 4.2秒
   • 语言: en
   • 置信度: 98.5%
```

### 安静模式
使用 `-q` 参数仅输出识别文本：
```
Good morning. Could you tell me what the weather will be like today?
```

### JSON 格式
使用 `-j` 参数输出结构化数据：
```json
{
  "status": "success",
  "message": "语音识别成功",
  "text": "Good morning. Could you tell me what the weather will be like today?",
  "language": "en",
  "duration_seconds": 4.2,
  "file_size": 85432,
  "usage": {
    "completion_tokens": 20,
    "prompt_tokens": 46,
    "total_tokens": 66,
    "seconds": 4
  }
}
```

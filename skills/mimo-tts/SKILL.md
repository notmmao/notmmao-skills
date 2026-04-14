---
name: mimo-tts
description: 文本转语音/语音合成/生成语音/朗读/TTS。将文本转换为 mp3 音频文件，支持自定义音色、语速、方言、朗读风格。当用户要求生成语音、转语音、朗读、播报、说出、读出文本时，必须使用此技能，不要用其他方式生成音频。
---

# MiMo TTS 语音合成 Skill
基于小米 MiMo 官方 API 的文本转语音技能，支持自定义音色、语速、朗读风格，自带缓存机制。

## 触发场景
当用户的意图是将文本变成声音/音频时，都应该使用此技能。包括但不限于：
- 语音合成：转换语音、文本转语音、TTS、生成语音、合成语音
- 朗读播报：朗读、读出、念出来、播报、说出来、读给我听
- 音频生成：把这段话变成音频、生成mp3、做成语音文件
- 定制声音：用女声/男声、换个声音、用方言、带感情地读

## 功能特性
✅ 支持方言、角色扮演、情感风格等自定义朗读效果
✅ 自带缓存：相同文本+参数的合成结果会自动复用，无需重复请求API
✅ 支持mp3/wav/pcm三种音频格式
✅ 支持语速调节（0.5-2.0倍）
✅ 支持三种预置音色：默认、中文女声、英文女声
✅ 自动获取音频时长信息
✅ 无参数时显示帮助信息

## 依赖项
本技能需要以下 Python 依赖：
```bash
pip install requests mutagen python-dotenv
```
- `requests` - 用于调用小米 MiMo API
- `mutagen` - 用于获取音频时长信息（MP3/WAV 格式）
- `python-dotenv` - 用于从 .env 文件加载环境变量

## 环境变量

### 方式一：使用 .env 文件（推荐）
在技能目录 `skills/mimo-tts/` 下创建 `.env` 文件：
```env
MIMO_API_KEY=sk-clrxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MIMO_API_URL=https://api.xiaomimimo.com/v1/chat/completions
MIMO_API_MODEL_TTS=mimo-v2-tts
```

### 方式二：系统环境变量
```bash
export MIMO_API_KEY="your_api_key_here"
```

### 配置说明
- `MIMO_API_KEY` - 必需，小米 MiMo API 密钥
- `MIMO_API_URL` - 可选，API 地址（默认：https://api.xiaomimimo.com/v1/chat/completions）
- `MIMO_API_MODEL_TTS` - 可选，TTS 模型名称（默认：mimo-v2-tts）

## 使用方式
```
python scripts/mimo_tts_cli.py --help
usage: mimo_tts_cli.py [-h] [-o OUTPUT] [-v {mimo_default,default_zh,default_en}] [-f {mp3,wav,pcm}]
                       [-s SPEED] [-t STYLE] [-F FILE] [-j] [-q]
                       [text]

小米 MiMo 语音合成 CLI 工具

positional arguments:
  text                  待合成的文本内容

optional arguments:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        输出音频文件路径（可选，默认使用缓存）
  -v {mimo_default,default_zh,default_en}, --voice {mimo_default,default_zh,default_en}
                        音色类型，默认mimo_default
  -f {mp3,wav,pcm}, --format {mp3,wav,pcm}
                        音频格式，默认mp3
  -s SPEED, --speed SPEED
                        语速倍率 0.5-2.0，默认1.0
  -t STYLE, --style STYLE
                        朗读风格描述，如"欢快的语气"、"温柔的声音"
  -F FILE, --file FILE  从文件读取文本（优先级高于 text 参数，节省 token）
  -j, --json            以JSON格式输出结果
  -q, --quiet           安静模式，仅输出文件路径
```

**注意**：无任何参数执行时，会自动显示帮助信息。

### 基础调用

只要用户想把文本变成语音，就执行：
```bash
python scripts/mimo_tts_cli.py "你好，我是小米MiMo语音助手"
```

更多示例：
- 用户说"念一下这段话" → `python scripts/mimo_tts_cli.py "这段话的内容"`
- 用户说"生成一个语音文件" → `python scripts/mimo_tts_cli.py "要合成的文本" -o ./output.mp3`
- 用户说"用女声读出来" → `python scripts/mimo_tts_cli.py "文本" -v default_zh`
- 用户说"把这个文件读出来" → `python scripts/mimo_tts_cli.py --file ./story.txt`（直接传文件路径，无需读取内容）


## 执行步骤
1. 解析用户输入的文本和参数（音色、语速、风格、输出路径等）
2. 如果文本在文件中，优先使用 `--file` 参数传入文件路径（节省 token）
3. 调用 `python scripts/mimo_tts_cli.py` 执行合成：工具会自动检查缓存，相同参数无需重复请求API
4. 返回音频文件路径、大小、时长、格式等详细信息

## 输出格式

### 默认输出（详细信息）
```
✅ 语音合成成功

📋 音频信息:
   • 文件名: 你好世界.mp3
   • 文件路径: .cache/mimo_tts/你好世界.mp3
   • 格式: MP3
   • 大小: 12.34 KB
   • 时长: 3.2秒

🎛️ 合成参数:
   • 音色: mimo_default
   • 语速: 1.0x
```

### 安静模式
使用 `-q` 参数仅输出文件路径：
```
.cache\mimo_tts\你好世界.mp3
```

### JSON 格式
使用 `-j` 参数输出结构化数据：
```json
{
  "status": "success",
  "message": "语音合成成功",
  "cached": false,
  "output_path": ".cache\\mimo_tts\\a1b2c3d4.mp3",
  "friendly_path": ".cache\\mimo_tts\\你好世界.mp3",
  "friendly_filename": "你好世界.mp3",
  "file_size": 12648,
  "format": "mp3",
  "voice": "mimo_default",
  "speed": 1.0,
  "style": "",
  "duration_seconds": 3.2
}
```

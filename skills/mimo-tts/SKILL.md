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

## 使用方式
```
python scripts/mimo_tts_cli.py --help
usage: mimo_tts_cli.py [-h] [-o OUTPUT] [-v {mimo_default,default_zh,default_en}] [-f {mp3,wav,pcm}] [-s SPEED]
                       [-t STYLE] [-F FILE] [-j]
                       [text]

小米 MiMo 语音合成 CLI 工具

positional arguments:
  text                  待合成的文本内容

optional arguments:
  -h, --help            show this help message and exit
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
```

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
4. 返回音频文件绝对路径、大小、是否来自缓存等信息

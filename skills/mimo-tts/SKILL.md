---
name: mimo-tts
description: 基于小米 MiMo 官方 API 的文本转语音技能，支持自定义音色、语速、朗读风格，自带缓存机制。
---

# MiMo TTS 语音合成 Skill
基于小米 MiMo 官方 API 的文本转语音技能，支持自定义音色、语速、朗读风格，自带缓存机制。

## 触发场景
当用户说以下内容时触发此 Skill：
- 转换语音...
- 定制语音包...
- 生成语音...
- 文本转语音...
- 用 MiMo 转语音...
- 朗读这段内容...

## 功能特性
✅ 支持方言、角色扮演、情感风格等自定义朗读效果
✅ 自带缓存：相同文本+参数的合成结果会自动复用，无需重复请求API
✅ 支持mp3/wav/pcm三种音频格式
✅ 支持语速调节（0.5-2.0倍）
✅ 支持三种预置音色：默认、中文女声、英文女声

## 使用方式
### 基础调用
```
转换语音 [文本内容]
```
示例：`转换语音 你好，我是小米MiMo语音助手`

### 带参数调用
#### 自定义音色
```
转换语音 [文本] 音色=default_zh
```
可选音色：`mimo_default`(默认)、`default_zh`(中文女声)、`default_en`(英文女声)

#### 自定义语速
```
转换语音 [文本] 语速=1.5
```
语速范围：0.5-2.0，默认1.0

#### 自定义朗读风格
```
转换语音 [文本] 风格=欢快的语气
转换语音 [文本] 风格=温柔的女声
转换语音 [文本] 风格=东北方言
```
支持自然语言描述任意风格、方言、角色扮演效果。

#### 指定输出路径
```
转换语音 [文本] 输出=./hello.mp3
```

#### 组合参数
```
转换语音 今天天气真好，适合出去走走 音色=default_zh 语速=1.2 风格=欢快的语气 输出=./weather.mp3
```

## 实现逻辑
### 调用入口
```python
# 加载环境变量
import os
from dotenv import load_dotenv
load_dotenv("/home/ota/.openclaw/.env")

# 解析用户参数后调用CLI
import subprocess
import json

def run_tts(text, voice="mimo_default", speed=1.0, style="", output_path=""):
    cmd = [
        "/home/ota/.openclaw/skills/mimo-tts/scripts/mimo_tts_cli.py",
        text,
        "-v", voice,
        "-s", str(speed),
        "-t", style,
        "-j"
    ]
    if output_path:
        cmd.extend(["-o", output_path])
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ)
    return json.loads(result.stdout) if result.returncode == 0 else json.loads(result.stderr)
```

### 执行步骤
1. 解析用户输入的文本和参数（音色、语速、风格、输出路径等）
2. 自动加载 `/home/ota/.openclaw/.env` 中的 `MIMO_API_KEY` 环境变量
3. 调用 `mimo_tts_cli.py` 执行合成：工具会自动检查缓存，相同参数无需重复请求API
4. 返回音频文件绝对路径、大小、是否来自缓存等信息
5. 可直接调用 `wecom-send-media` 技能将音频文件发送给用户

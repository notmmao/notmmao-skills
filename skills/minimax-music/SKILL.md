---
name: minimax-music
description: 使用 MiniMax API 生成音乐。当用户需要生成音乐、创作歌曲、从歌词生成音频，或者使用 MiniMax 音乐生成服务时使用此技能。即使没有明确提到 MiniMax，只要涉及音乐生成、AI 音乐创作等需求都应触发。
---

# MiniMax 音乐生成

使用 MiniMax Music Generation API 将歌词转换为音乐。

## 前置要求

- 在 `~/.openclaw/.env` 文件中配置 `MINIMAX_API_KEY` 环境变量：
```env
MINIMAX_API_KEY=你的MiniMax API密钥
```

- 依赖已预装在虚拟环境中，无需额外安装

## 使用方法

通过命令行参数生成音乐：

```bash
# 基本用法 - 使用默认风格
python scripts/generate_music.py --lyrics "你的歌词内容"

# 自定义风格和输出文件名
python scripts/generate_music.py \
  --lyrics "[verse]\n主歌内容\n[chorus]\n副歌内容" \
  --prompt "流行,欢快,阳光,海滩" \
  --output my_song.mp3

# 从文件读取歌词
python scripts/generate_music.py \
  --lyrics-file lyrics.txt \
  --prompt "摇滚,激情,热血" \
  --output rock_song.mp3
```

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--lyrics` | 是* | 直接指定歌词内容 |
| `--lyrics-file` | 是* | 从文件读取歌词（与 --lyrics 二选一） |
| `--prompt` | 否 | 风格提示词，默认："独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆" |
| `--output` | 否 | 输出文件名，默认：自动生成时间戳名称 |
| `--model` | 否 | 模型版本，默认："music-2.5+" |
| `--format` | 否 | 音频格式，默认："mp3" |

*至少需要提供 `--lyrics` 或 `--lyrics-file` 其中之一

## 输出

生成的音乐文件默认保存在 `output/music/` 目录下。

## API 限制

- API 端点：`https://api.minimaxi.com/v1/music_generation`
- 支持的格式：mp3
- 采样率：44100 Hz
- 比特率：256000

## 错误处理

- 未设置 `MINIMAX_API_KEY`：脚本会报错并提示如何设置
- API 请求失败：显示错误信息和 trace_id 用于调试

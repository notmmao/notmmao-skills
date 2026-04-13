---
name: local-whisper-asr
description: 基于本地whisper命令的离线语音转文字技能，无需调用云端API，支持常见音视频格式输入，输出多格式转写结果，适用于需要本地处理敏感音频、离线使用场景。触发场景：用户要求本地转写音频、离线语音识别、不使用云端ASR服务的转写需求。
tags: ["ASR", "语音识别", "离线", "whisper", "音频处理"]
author: "OpenClaw"
category: "工具"
---

# 本地Whisper语音转文字技能

## 功能概述
完全基于本地部署的whisper命令行工具实现离线语音转文字，支持MP3、WAV、MP4、FLV等几乎所有常见音视频格式输入，无需联网，不会上传任何音频数据到第三方服务，适用于敏感内容处理、无网环境使用等场景。

## 依赖要求
- 本地已安装whisper命令行工具（`pip install openai-whisper`）
- 已下载对应模型文件（默认优先使用small模型，自动下载到本地缓存）
- 支持ffmpeg用于音视频格式解码

## 执行工作流

### 步骤1：依赖检查
自动检测本地whisper、ffmpeg命令是否可用，若未安装则提示安装命令。

### 步骤2：输入处理
- **本地文件输入**：直接读取本地音视频文件
- **URL输入**：自动下载音视频文件到本地缓存目录（`~/.cache/local-whisper-asr`）
- 自动校验文件完整性，若文件已存在于缓存且校验一致则直接跳过下载

### 步骤3：语音转写
- 默认优先使用small模型，可根据用户需求切换为tiny/base/medium/large模型
- 默认优先识别简体中文，可指定其他语言或自动检测
- 支持长音频自动分段处理，无需用户手动切分

### 步骤4：结果输出
- 转写完成后自动输出txt（纯文本）、srt（字幕）、vtt（web字幕）、json（结构化数据）四种格式
- 结果默认保存到缓存目录，可根据用户需求导出到指定路径
- 自动保留历史转写结果，同一个输入文件/URL可直接从缓存读取结果，无需重复转写

## 参数说明
| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| input | 本地文件路径 / URL | 必填 | 待转写的音视频资源 |
| model | tiny/base/small/medium/large | small | 使用的whisper模型 |
| language | zh/en/ja/ko/auto | zh | 识别语言，默认简体中文 |
| output | 本地目录路径 | ~/.cache/local-whisper-asr | 结果输出目录 |
| formats | txt/srt/vtt/json | 全部 | 指定输出格式，多个用逗号分隔 |

## 使用示例
### 示例1：本地音频转写
输入：`转写本地文件 ~/Downloads/meeting.mp3`
输出：自动生成meeting.txt、meeting.srt等四种格式文件，保存到缓存目录

### 示例2：URL视频转写
输入：`转写这个视频的音频 https://example.com/video.mp4`
输出：自动下载视频提取音频转写，返回所有格式结果

### 示例3：指定模型和语言
输入：`用large模型转写这个英文音频 input.wav language=en`
输出：使用large模型识别英文内容

## 缓存规则
- 所有临时文件、转写结果统一保存到 `~/.cache/local-whisper-asr` 目录
- 同一个输入文件/URL根据MD5值生成缓存键，已转写过的资源直接返回缓存结果，避免重复计算
- 缓存可手动清理：`rm -rf ~/.cache/local-whisper-asr/*`

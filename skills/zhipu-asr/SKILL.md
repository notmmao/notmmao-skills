---
name: zhipu-asr
description: 基于智谱 GLM-ASR-2512 模型的语音转文本技能，支持音频文件转录、流式输出、热词增强。
metadata: {"openclaw":{"emoji":"🎙️","requires":{"env":["ZHIPU_API_TOKEN"]}}}
---

# 智谱 ASR 语音转文本 Skill
基于智谱 [GLM-ASR-2512](https://docs.bigmodel.cn/api-reference/%E6%A8%A1%E5%9E%8B-api/%E8%AF%AD%E9%9F%B3%E8%BD%AC%E6%96%87%E6%9C%AC) 模型的语音转文本技能，支持多语言识别，适合短音频（≤30秒、≤25MB）的转录场景。

## 触发场景
当用户说以下内容时触发此 Skill：
- 语音转文字 / 语音转文本
- ASR / 语音识别
- 把这段音频转成文字
- 转录音频
- 音频转录

## 功能特性
✅ 支持 `.wav` / `.mp3` 格式音频转录  
✅ 支持流式实时输出（`--stream`）  
✅ 支持热词增强识别（`--hotwords`）  
✅ 支持长文本上下文提示（`--prompt`）  
✅ 支持 Base64 编码上传（`--base64`）  
✅ 兼容多种环境变量命名：`ZHIPU_API_KEY`、`ZHIPU_API_TOKEN`、`BIGMODEL_API_KEY`

## 前置配置
```env
ZHIPU_API_KEY=你的智谱API密钥
```
或沿用已有的 `ZHIPU_API_TOKEN`。

## 使用方式
### 1. 基础转录
```
转录 audio.mp3
```

### 2. 流式实时输出
```
转录 audio.mp3 --stream
```

### 3. 热词增强
```
转录 audio.mp3 --hotwords 智谱 大模型 GLM
```

### 4. 长文本上下文
```
转录 audio.mp3 --prompt "前文提到人工智能的发展趋势"
```

## 执行
调用 `scripts/zhipu-asr.py`：
```bash
python scripts/zhipu-asr.py <音频/视频文件> [--prompt "上下文"] [--hotwords 词1 词2 ...] [--raw]
```

| 参数 | 作用 |
|------|------|
| `--prompt` | 长文本上下文提示，提升连贯性 |
| `--hotwords` | 热词列表，空格分隔 |
| `--raw` | 输出原始 JSON |
| `--keep-segments` | 保留分段文件（调试） |

zhipu-asr.py 自动处理：
- 视频文件 → 先提取音频（ffmpeg）
- 长音频（>30s）→ 自动分段转录 + 拼接去重
- 短音频（≤30s）→ 直接转录

## 实现逻辑
1. 接收用户音频文件路径及可选参数
2. 从环境变量加载智谱 API Key
3. 调用 `/paas/v4/audio/transcriptions` 接口
4. 返回转录文本结果

## API 限制
- 音频格式：`.wav`、`.mp3`
- 文件大小：≤ 25 MB
- 音频时长：≤ 30 秒
- 模型：`glm-asr-2512`

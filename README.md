# notmmao-skills
我的个人通用AI Agent技能仓库，收集我开发和修改的实用技能，均适配国内环境，开箱即用，支持OpenClaw、Claude Desktop、Cursor、Obsidian Skills等所有支持Open Skills协议的运行环境，不绑定特定平台。

## ✨ 特性
- 🔌 通用标准，兼容多种AI Agent运行环境
- 🇨🇳 全部适配国内使用环境，无需翻墙
- 🔒 无硬编码密钥，所有敏感配置从环境变量读取
- ⚡ 均自带缓存机制，避免重复请求浪费资源
- 📦 开箱即用，无需额外复杂配置

## 📦 技能列表
### 音视频处理类
| 技能名 | 功能描述 |
|--------|----------|
| `yt-audio-download` | 基于yt-dlp的通用视频平台音频下载工具，支持B站、抖音、YouTube等主流平台，自动转换为192kbps MP3，内置去重缓存 |
| `local-whisper-asr` | 完全离线的Whisper语音转写技能，支持几乎所有音视频格式，无需联网，输出txt/srt/vtt/json四种格式结果 |
| `audio-transcribe-summary` | 音视频处理全流程技能：自动下载/提取音频 → 离线转写 → 结构化总结 → 自动导出Markdown/PDF，支持会议记录、课程整理、视频内容提取等场景 |

### AI生成类
| 技能名 | 功能描述 |
|--------|----------|
| `minimax-music` | MiniMax AI音乐生成技能，支持歌词生成音乐、风格自定义、旋律提取改编，生成高质量MP3格式音乐 |
| `mimo-tts` | 小米MiMo语音合成技能，支持自定义音色、语速、朗读风格、方言，自带缓存，支持mp3/wav/pcm三种格式输出 |
| `volc-image-gen` | 火山引擎豆包AI绘画技能，支持文生图、图生图、多参考图融合，支持2K/4K超清分辨率，电影级画质 |

### 搜索工具类
| 技能名 | 功能描述 |
|--------|----------|
| `zhipu-searcher` | 智谱AI网络搜索技能，支持自定义搜索条件、时间过滤、域名过滤，实时获取公开网络信息 |

### 开发工具类
| 技能名 | 功能描述 |
|--------|----------|
| `rest-tester` | 生成符合REST Client规范的.http测试脚本，支持变量系统、多种认证方式、链式请求，用于API接口测试 |
| `codebase-visualizer` | 生成代码库交互式可视化HTML树状图，可折叠目录、显示文件大小，用于探索新项目结构 |

## 🚀 安装

### 全量安装
```bash
npx skills add https://github.com/notmmao/notmmao-skills
```

### 单独安装
复制对应的命令即可安装单个技能：

```bash
# 音视频处理类
npx skills add https://github.com/notmmao/notmmao-skills --skill yt-audio-download
npx skills add https://github.com/notmmao/notmmao-skills --skill local-whisper-asr
npx skills add https://github.com/notmmao/notmmao-skills --skill audio-transcribe-summary

# AI生成类
npx skills add https://github.com/notmmao/notmmao-skills --skill minimax-music
npx skills add https://github.com/notmmao/notmmao-skills --skill mimo-tts
npx skills add https://github.com/notmmao/notmmao-skills --skill volc-image-gen

# 搜索工具类
npx skills add https://github.com/notmmao/notmmao-skills --skill zhipu-searcher

# 开发工具类
npx skills add https://github.com/notmmao/notmmao-skills --skill rest-tester
npx skills add https://github.com/notmmao/notmmao-skills --skill codebase-visualizer
```

### 升级已安装的技能
```bash
npx skills upgrade https://github.com/notmmao/notmmao-skills
```

## 🔧 配置

### 方式1：环境变量文件（OpenClaw等）
将以下内容保存到 `~/.openclaw/.env`：

```env
# minimax-music 所需
MINIMAX_API_KEY=你的MiniMax API密钥

# mimo-tts 所需
MIMO_API_KEY=你的小米MiMo API密钥
MIMO_API_URL=可选，自定义API端点

# volc-image-gen 所需
ARK_API_KEY=你的火山引擎API密钥
ARK_API_MODEL=可选，自定义模型版本

# zhipu-searcher 所需
ZHIPU_API_TOKEN=你的智谱AI API Token
```

### 方式2：Claude Desktop配置（Claude Code/Cursor等）
编辑 `~/.claude/settings.json` 或项目的 `.claude/settings.local.json`，添加 `env` 字段：

```json
{
  "env": {
    "MINIMAX_API_KEY": "你的MiniMax API密钥",
    "MIMO_API_KEY": "你的小米MiMo API密钥",
    "MIMO_API_URL": "可选，自定义API端点",
    "ARK_API_KEY": "你的火山引擎API密钥",
    "ARK_API_MODEL": "可选，自定义模型版本",
    "ZHIPU_API_TOKEN": "你的智谱AI API Token"
  }
}
```

## 📝 使用
安装完成后，即可通过自然语言触发对应技能，例如：
- `帮我下载这个B站视频的音频：https://b23.tv/xxxxxx`
- `用欢快的女声朗读这段内容：你好，我是你的AI助手`
- `生成一张星际穿越风格的4K图片：黑洞旁的复古列车`
- `总结这个视频的内容：https://www.douyin.com/video/xxxxxx`

每个技能目录下的`SKILL.md`文件包含详细的使用说明和参数配置。

## 🤝 贡献
欢迎提交Issue和PR，新增技能或者改进现有功能：
1. Fork本仓库
2. 在`skills/`目录下新增你的技能，确保包含完整的`SKILL.md`说明和开源协议
3. 提交PR即可

## 📄 许可证
所有技能均采用 [MIT License](./LICENSE) 开源，可自由使用、修改、分发。

---
name: conversation-viewer
description: 查看、导出和分析 Claude Code 会话历史。当用户想要查看之前的对话记录、导出会话为 HTML、分析 Claude Code conversation history、或者需要访问 ~/.claude/projects 中的 JSONL 会话数据时，必须使用此技能。即使没有明确提到 "Claude Code"，只要涉及查看/导出 AI 对话历史、会话记录、conversation history 就应该触发。
---

# Conversation Viewer

帮助你查看、导出和分析 Claude Code 的会话历史记录。

## 背景

Claude Code 将所有会话数据存储在 `~/.claude/projects/<项目名>/` 目录下，每个会话是一个 JSONL 文件。这些文件包含完整的对话历史：用户输入、AI 回复、工具调用、思考过程等。

本技能提供了一个脚本 `./scripts/claude_code_viewer.py`，可以：
- 列出所有可用的项目和会话
- 将会话导出为人类可读的 HTML 格式
- 支持按类型筛选、折叠/展开消息
- 批量导出多个会话

## 使用方法

### 1. 查看所有项目

```bash
python scripts/claude_code_viewer.py --list-projects
```

输出示例：
```
可用的项目 (共 24 个):
  - D--work-code-AI-myclaw (28 sessions)
  - D--work-HIL-code-gp-gp-tm (67 sessions)
  ...
```

### 2. 查看项目的会话列表

```bash
# 查看当前项目的会话
python scripts/claude_code_viewer.py --list

# 查看指定项目的会话
python scripts/claude_code_viewer.py --project D--work-code-AI-myclaw --list
```

### 3. 导出会话

```bash
# 导出当前项目最新的会话
python scripts/claude_code_viewer.py

# 导出指定的会话（使用 UUID 或部分 UUID）
python scripts/claude_code_viewer.py a9a9af55-e689-4abe-987f-dbb852dab6b7
python scripts/claude_code_viewer.py a9a9af55

# 导出到指定目录
python scripts/claude_code_viewer.py -o ./exports

# 导出后不自动打开浏览器
python scripts/claude_code_viewer.py --no-open
```

### 4. 批量导出

```bash
# 导出最近的 5 个会话
python scripts/claude_code_viewer.py --batch 5

# 导出到指定目录
python scripts/claude_code_viewer.py --batch 5 -o ./exports
```

## HTML 输出特性

导出的 HTML 文件具有以下特性：

- **消息类型标识**: 👤 用户、🤖 AI、← 工具结果
- **类型标签**: 显示每条消息的内容类型（text/thinking/tool_use/tool_result）
- **智能折叠**:
  - 用户消息：默认展开
  - AI 回复用户（有 text）：默认展开
  - AI 内部思考（只有 thinking）：默认折叠
  - 工具调用/结果：默认折叠
- **可点击折叠**: 点击消息头可展开/收起内容
- **序号**: 每条消息都有序号，方便引用
- **时间戳**: 显示消息时间
- **工具调用信息**: 显示工具名称、参数、call_id

## 文件位置

- **脚本**: `./scripts/claude_code_viewer.py`
- **Claude Code 数据**: `~/.claude/projects/`
- **项目命名规则**: 路径中的特殊字符被替换为 `-`
  - Windows: `D:\work\code` → `D-work-code`
  - Unix: `/home/user/project` → `home-user-project`

## 常见使用场景

1. **回顾之前的对话** - 导出会话为 HTML，在浏览器中查看
2. **分析工具调用** - 查看完整的工具调用链路
3. **调试 AI 行为** - 查看思考过程和决策逻辑
4. **备份重要会话** - 批量导出关键对话
5. **分享对话记录** - 导出为 HTML 格式分享给他人

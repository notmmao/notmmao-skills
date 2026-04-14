#!/usr/bin/env python3
"""
Claude Code Conversation Viewer

读取 ~/.claude/projects/ 下的 JSONL 文件，渲染为 HTML。
独立测试脚本，非 myclaw 项目一部分。
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import webbrowser


# HTML 模板（内嵌，保持脚本独立性）
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Code 会话 - {session_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #1a1a2e;
            color: #eee;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            text-align: center;
            margin-bottom: 10px;
            color: #4fc3f7;
        }}

        .meta {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 14px;
        }}

        .message {{
            margin-bottom: 20px;
            border-radius: 8px;
            overflow: hidden;
        }}

        .message.user {{
            background: #1e3a5f;
            border-left: 4px solid #4fc3f7;
        }}

        .message.assistant {{
            background: #1a1a2e;
            border-left: 4px solid #66bb6a;
        }}

        .message.thinking {{
            background: #2d1f3d;
            border-left: 4px solid #ab47bc;
            opacity: 0.7;
        }}

        .message-header {{
            padding: 8px 15px;
            font-weight: bold;
            font-size: 13px;
            opacity: 0.8;
        }}

        .msg-index {{
            display: inline-block;
            background: rgba(255,255,255,0.1);
            padding: 1px 8px;
            border-radius: 10px;
            font-size: 11px;
            margin-right: 8px;
            font-weight: normal;
        }}

        .timestamp {{
            color: #888;
            font-size: 11px;
            margin-left: 8px;
        }}

        .type-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.08);
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 8px;
            color: #aaa;
            font-family: 'Consolas', 'Monaco', monospace;
        }}

        .message-content {{
            padding: 15px;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        .collapsible-header {{
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
        }}

        .collapsible-header:hover {{
            opacity: 1;
        }}

        .collapsible-header::after {{
            content: '▼';
            font-size: 12px;
            transition: transform 0.2s;
        }}

        .collapsed .collapsible-header::after {{
            transform: rotate(-90deg);
        }}

        .collapsed .message-content {{
            display: none;
        }}

        .thinking-block {{
            background: rgba(171, 71, 188, 0.1);
            border-left: 2px solid #ab47bc;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
            font-size: 14px;
        }}

        .tool-use {{
            background: #2d1f3d;
            border-left: 2px solid #ffb74d;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .tool-name {{
            color: #ffb74d;
            font-weight: bold;
        }}

        .stats {{
            text-align: center;
            color: #888;
            margin-top: 30px;
            padding: 20px;
            background: #16213e;
            border-radius: 8px;
        }}

        .emoji {{
            font-size: 16px;
        }}

        code {{
            background: #0f0f1a;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Claude Code 会话记录</h1>
        <div class="meta">Session: {session_id} | {timestamp} | 共 {total_messages} 条消息</div>

        {messages}

        <div class="stats">
            会话结束 | Claude Code v{version}
        </div>
    </div>

    <script>
        document.querySelectorAll('.collapsible-header').forEach(header => {{
            header.addEventListener('click', function() {{
                this.parentElement.classList.toggle('collapsed');
            }});
        }});
    </script>
</body>
</html>
"""


def parse_jsonl(file_path: Path):
    """解析 Claude Code JSONL 文件"""
    entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def format_message_content(content):
    """格式化消息内容（处理数组和特殊类型）"""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                item_type = item.get("type", "")
                if item_type == "thinking":
                    thinking = item.get("thinking", "")
                    parts.append(f'<div class="thinking-block">💭 {thinking}</div>')
                elif item_type == "text":
                    parts.append(item.get("text", ""))
                elif item_type == "tool_use":
                    tool_name = item.get("name", "")
                    input_data = item.get("input", {})
                    parts.append(f'<div class="tool-use">🔧 <span class="tool-name">{tool_name}</span>: {json.dumps(input_data, ensure_ascii=False)}</div>')
                else:
                    parts.append(json.dumps(item, ensure_ascii=False))
            else:
                parts.append(str(item))
        return "".join(parts)

    return json.dumps(content, ensure_ascii=False)


def render_html(entries, output_path: Path = None):
    """渲染为 HTML"""
    messages_html = []
    seq = 0

    # 提取元数据
    session_id = entries[0].get("sessionId", "unknown") if entries else "unknown"
    timestamp = entries[0].get("timestamp", "") if entries else ""
    version = entries[0].get("version", "unknown") if entries else "unknown"

    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass

    for entry in entries:
        entry_type = entry.get("type", "")
        message = entry.get("message", {})

        if entry_type == "file-history-snapshot":
            continue  # 跳过快照

        seq += 1
        ts = entry.get("timestamp", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                ts_short = dt.strftime('%H:%M:%S')
            except:
                ts_short = ts[:8]
        else:
            ts_short = ""

        if entry_type == "user":
            content = message.get("content", "")

            # 检查是否是 tool_result（content 是数组且包含 tool_result）
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and first_item.get("type") == "tool_result":
                    # 这是工具返回结果，不是用户消息
                    tool_use_id = first_item.get("tool_use_id", "unknown")
                    result_content = first_item.get("content", "")
                    is_error = first_item.get("is_error", False)

                    escaped = format_message_content(result_content)
                    escaped = escaped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                    bg_color = "#3d1f2d" if is_error else "#2d2d44"
                    border_color = "#ff5252" if is_error else "#ffb74d"
                    emoji = "❌" if is_error else "←"

                    messages_html.append(f'''
                    <div class="message tool collapsed" style="background: {bg_color}; border-left-color: {border_color};">
                        <div class="message-header collapsible-header">
                            <span class="msg-index">#{seq}</span> {emoji} 工具返回结果
                            <span class="type-badge">tool_result</span>
                            <span style="font-size: 11px; font-family: monospace;">id: {tool_use_id[:12]}...</span>
                            <span class="timestamp">{ts_short}</span>
                        </div>
                        <div class="message-content"><code>{escaped}</code></div>
                    </div>''')
                    continue

            # 正常用户消息
            escaped = format_message_content(content)
            escaped = escaped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # 检测 content 类型
            if isinstance(content, str):
                content_type = "text"
            elif isinstance(content, list) and len(content) > 0:
                types = set()
                for item in content:
                    if isinstance(item, dict):
                        t = item.get("type", "")
                        if t:
                            types.add(t)
                content_type = ",".join(sorted(types)) if types else "mixed"
            else:
                content_type = "unknown"

            messages_html.append(f'''
            <div class="message user">
                <div class="message-header collapsible-header">
                    <span class="msg-index">#{seq}</span> 👤 用户
                    <span class="type-badge">{content_type}</span>
                    <span class="timestamp">{ts_short}</span>
                </div>
                <div class="message-content">{escaped}</div>
            </div>''')

        elif entry_type == "tool_result":
            # 工具返回结果
            tool_use_id = message.get("tool_use_id", "unknown")
            content = message.get("content", "")
            is_error = message.get("is_error", False)

            escaped = format_message_content(content)
            escaped = escaped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            bg_color = "#3d1f2d" if is_error else "#2d2d44"
            border_color = "#ff5252" if is_error else "#ffb74d"
            emoji = "❌" if is_error else "←"

            messages_html.append(f'''
            <div class="message tool collapsed" style="background: {bg_color}; border-left-color: {border_color};">
                <div class="message-header collapsible-header">
                    <span class="msg-index">#{seq}</span> {emoji} 工具返回结果
                    <span style="font-size: 11px; font-family: monospace;">id: {tool_use_id[:12]}...</span>
                    <span class="timestamp">{ts_short}</span>
                </div>
                <div class="message-content"><code>{escaped}</code></div>
            </div>''')

        elif entry_type == "assistant":
            content = message.get("content", [])

            # 收集所有类型
            types = set()
            for item in content:
                if isinstance(item, dict):
                    t = item.get("type", "")
                    if t:
                        types.add(t)
            content_type = ",".join(sorted(types)) if types else "unknown"

            # 检查是否有 text 类型（回复用户）
            has_user_reply = any(
                isinstance(item, dict) and item.get("type") == "text"
                for item in content
                if isinstance(item, dict)
            )

            # 只有 thinking/tool_use → 折叠；有 text → 展开
            collapsed_class = "" if has_user_reply else " collapsed"

            formatted = format_message_content(content)
            messages_html.append(f'''
            <div class="message assistant{collapsed_class}">
                <div class="message-header collapsible-header">
                    <span class="msg-index">#{seq}</span> 🤖 AI ({message.get("model", "claude")})
                    <span class="type-badge">{content_type}</span>
                    <span class="timestamp">{ts_short}</span>
                </div>
                <div class="message-content">{formatted}</div>
            </div>''')

    html = HTML_TEMPLATE.format(
        session_id=session_id[:8],
        timestamp=timestamp,
        total_messages=seq,
        version=version,
        messages=''.join(messages_html)
    )

    if output_path:
        output_path.write_text(html, encoding='utf-8', newline='\n')
        return output_path
    return html


def list_sessions(project_dir: Path, limit: int = 20):
    """列出一个项目的所有 sessions，按时间倒序"""
    jsonl_files = list(project_dir.glob("*.jsonl"))
    if not jsonl_files:
        return []

    # 按修改时间排序
    sessions = []
    for jsonl_file in sorted(jsonl_files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        session_id = jsonl_file.stem  # 文件名不含扩展名
        mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime)
        size_mb = jsonl_file.stat().st_size / (1024 * 1024)

        # 读取第一条获取时间戳
        timestamp = "unknown"
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line:
                    entry = json.loads(first_line)
                    ts = entry.get("timestamp", "")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                            timestamp = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
        except:
            pass

        sessions.append({
            "session_id": session_id,
            "file": jsonl_file,
            "timestamp": timestamp,
            "mtime": mtime,
            "size_mb": size_mb
        })

    return sessions


def find_session_by_id(project_dir: Path, session_id: str) -> Path:
    """根据 session id (UUID) 查找文件"""
    # 支持完整 UUID 或部分 UUID（前8位）
    jsonl_file = project_dir / f"{session_id}.jsonl"
    if jsonl_file.exists():
        return jsonl_file

    # 尝试部分匹配
    for f in project_dir.glob("*.jsonl"):
        if f.stem.startswith(session_id):
            return f

    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Code 会话查看器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出当前项目的所有 sessions
  python claude_code_viewer.py --list

  # 导出最新的 session
  python claude_code_viewer.py

  # 导出指定的 session (UUID)
  python claude_code_viewer.py a9a9af55-e689-4abe-987f-dbb852dab6b7

  # 导出到指定目录
  python claude_code_viewer.py -o ./exports

  # 批量导出最近的 5 个 sessions
  python claude_code_viewer.py --batch 5

  # 指定项目目录（非当前项目）
  python claude_code_viewer.py --project ~/.claude/projects/D--work-code-AI-myclaw
        """
    )
    parser.add_argument("session", nargs="?", help="Session ID (UUID) 或 JSONL 文件路径")
    parser.add_argument("-l", "--list", action="store_true", help="列出所有可用的 sessions")
    parser.add_argument("--list-projects", action="store_true", help="列出所有可用的项目")
    parser.add_argument("-o", "--output", type=str, help="输出目录（默认：当前目录）")
    parser.add_argument("-b", "--batch", type=int, metavar="N", help="批量导出最近 N 个 sessions")
    parser.add_argument("-p", "--project", type=str, help="项目名称或路径（默认自动检测当前项目）")
    parser.add_argument("--no-open", action="store_true", help="导出后不自动打开浏览器")
    parser.add_argument("--limit", type=int, default=20, help="列出 sessions 时的数量限制（默认：20）")

    args = parser.parse_args()

    import os
    claude_dir = Path(os.path.expanduser("~/.claude/projects"))

    # 列出所有项目（优先处理，不需要项目目录）
    if args.list_projects:
        if not claude_dir.exists():
            print(f"Claude Code 项目目录不存在: {claude_dir}")
            return

        projects = sorted([d for d in claude_dir.iterdir() if d.is_dir()])
        if not projects:
            print(f"未找到任何项目")
            return

        print(f"\n可用的项目 (共 {len(projects)} 个):\n")
        for p in projects:
            # 统计 session 数量
            jsonl_count = len(list(p.glob("*.jsonl")))
            print(f"  - {p.name} ({jsonl_count} sessions)")
        print(f"\n使用方法: python claude_code_viewer.py --project <项目名>")
        return

    # 确定项目目录
    if args.project:
        project_dir = Path(args.project)
        if not project_dir.is_absolute():
            project_dir = claude_dir / args.project
    else:
        # 自动检测当前项目
        cwd = Path.cwd()

        # 将当前路径转换为 Claude Code 的项目路径格式
        # Claude Code 将路径中的特殊字符替换：
        # Windows: D:\work\code → D--work-code (盘符后用 --, 其他用 -)
        # Unix: /home/user → home-user
        def normalize_path(p: Path) -> str:
            """转换路径为 Claude Code 项目名格式"""
            parts = []
            for part in p.parts:
                if part:
                    # 将特殊字符替换为 -
                    normalized = part.replace(":", "").replace("\\", "-").replace("/", "-").replace(" ", "-")
                    parts.append(normalized)
            return "-".join(parts)

        project_name = normalize_path(cwd)
        project_dir = claude_dir / project_name

    if not project_dir.exists():
        print(f"错误: 项目目录不存在: {project_dir}")
        print(f"提示: 使用 --list-projects 查看所有可用项目")
        print(f"      或使用 --project <项目名> 指定项目")
        return

    # 列出所有项目
    if args.list_projects:
        claude_dir = Path(os.path.expanduser("~/.claude/projects"))
        if not claude_dir.exists():
            print(f"Claude Code 项目目录不存在: {claude_dir}")
            return

        projects = sorted([d for d in claude_dir.iterdir() if d.is_dir()])
        if not projects:
            print(f"未找到任何项目")
            return

        print(f"\n可用的项目 (共 {len(projects)} 个):\n")
        for p in projects:
            # 统计 session 数量
            jsonl_count = len(list(p.glob("*.jsonl")))
            print(f"  - {p.name} ({jsonl_count} sessions)")
        print(f"\n使用方法: python claude_code_viewer.py --project <项目名>")
        return

    # 列出 sessions
    if args.list:
        sessions = list_sessions(project_dir, limit=args.limit)
        if not sessions:
            print(f"未找到 sessions: {project_dir}")
            return

        print(f"\n可用的 Sessions (共 {len(sessions)} 个):\n")
        for i, s in enumerate(sessions, 1):
            print(f"  {i:2d}. {s['session_id'][:8]}... | {s['timestamp']} | {s['size_mb']:.2f}MB | {s['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n使用方法: python claude_code_viewer.py <session_id>")
        return

    # 确定输出目录
    output_dir = Path(args.output) if args.output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 批量导出
    if args.batch:
        sessions = list_sessions(project_dir, limit=args.batch)
        if not sessions:
            print(f"未找到 sessions: {project_dir}")
            return

        print(f"批量导出 {len(sessions)} 个 sessions 到: {output_dir}\n")
        for i, s in enumerate(sessions, 1):
            jsonl_file = s["file"]
            output_file = output_dir / f"claude_session_{s['session_id'][:8]}.html"

            print(f"[{i}/{len(sessions)}] {s['session_id'][:8]}...", end=" ", flush=True)
            try:
                entries = parse_jsonl(jsonl_file)
                render_html(entries, output_file)
                print(f"✓ {len(entries)} 条记录")
            except Exception as e:
                print(f"✗ 错误: {e}")

        print(f"\n完成！共导出 {len(sessions)} 个 sessions")
        if not args.no_open:
            webbrowser.open(f"file://{output_dir.absolute()}")
        return

    # 确定要导出的 session
    if args.session:
        # 用户指定了 session ID 或文件路径
        input_path = Path(args.session)
        if input_path.exists():
            # 直接是文件路径
            jsonl_file = input_path
        else:
            # 当作 session ID 查找
            jsonl_file = find_session_by_id(project_dir, args.session)
            if not jsonl_file:
                print(f"错误: 未找到 session: {args.session}")
                print(f"提示: 使用 --list 查看可用的 sessions")
                return
    else:
        # 默认：读取最新的 session
        jsonl_files = list(project_dir.glob("*.jsonl"))
        if not jsonl_files:
            print(f"未找到 JSONL 文件: {project_dir}")
            return
        jsonl_file = max(jsonl_files, key=lambda p: p.stat().st_mtime)

    # 单个 session 导出
    print(f"读取: {jsonl_file}")
    entries = parse_jsonl(jsonl_file)
    print(f"读取到 {len(entries)} 条记录")

    # 输出 HTML
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = jsonl_file.stem[:8]
    output_file = output_dir / f"claude_session_{session_id}_{timestamp}.html"

    render_html(entries, output_file)
    print(f"已导出到: {output_file}")

    # 自动打开
    if not args.no_open:
        webbrowser.open(f"file://{output_file.absolute()}")


if __name__ == "__main__":
    main()

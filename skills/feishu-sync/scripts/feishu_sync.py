#!/usr/bin/env python3
"""
飞书文档同步脚本 - 一键同步 Wiki 文档

功能：
    输入 URL 和输出目录，自动生成：
    1. xx_骨架.md - fetch 原始版本（带 sheet 标记）
    2. xx.md - 完整可读版本（表格已展开）

使用方法：
    python feishu_sync.py <url> <output_dir> [name]

示例：
    python feishu_sync.py https://q1q11nqsd12.feishu.cn/wiki/JP9TwETkWijyCAkaLe8c3JMonAb "接口文档/服务器API/2026-04-17" "文档名称"
"""

import re
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def extract_token(url: str) -> str | None:
    """从飞书 Wiki URL 中提取文档 token"""
    # 支持多种 URL 格式
    patterns = [
        r'/wiki/([a-zA-Z0-9]+)',      # /wiki/XXX
        r'/docs/([a-zA-Z0-9]+)',       # /docs/XXX
        r'/docx/([a-zA-Z0-9]+)',       # /docx/XXX
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_doc_content(token: str) -> str | None:
    """调用 lark-cli 获取文档内容"""
    cmd = ["lark-cli", "docs", "+fetch", "--doc", token, "--format", "pretty"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取文档失败: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print(f"❌ 获取文档超时")
        return None


def col_to_letter(col: int) -> str:
    """列号转字母 (1=A, 2=B, 26=Z, 27=AA)"""
    result = ""
    while col > 0:
        col -= 1
        result = chr(65 + col % 26) + result
        col //= 26
    return result


def extract_sheet_token_parts(sheet_tag: str) -> tuple[str, str] | None:
    """从 <sheet token="XXX_YYY"/> 中提取 spreadsheet token 和 range"""
    match = re.search(r'<sheet\s+token="([^_]+)_([^"]+)"\s*/?>', sheet_tag)
    if match:
        return match.group(1), match.group(2)
    return None


def fetch_sheet_data(spreadsheet_token: str, range: str) -> list[list[str]] | None:
    """调用 lark-cli 获取表格数据"""
    cmd = ["lark-cli", "sheets", "+read", "--spreadsheet-token", spreadsheet_token, "--range", range]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        data = json.loads(result.stdout)

        if not data.get("ok"):
            print(f"⚠️  API返回错误: {data}")
            return None

        values = data.get("data", {}).get("valueRange", {}).get("values", [])
        return values

    except subprocess.CalledProcessError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except json.JSONDecodeError:
        return None


def fetch_spreadsheet_info(spreadsheet_token: str) -> dict[str, tuple[int, int]] | None:
    """获取 spreadsheet 的 sheet 尺寸信息，返回 {sheet_id: (rows, cols)}"""
    cmd = ["lark-cli", "sheets", "+info", "--spreadsheet-token", spreadsheet_token]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        data = json.loads(result.stdout)
        if not data.get("ok"):
            return None
        sheets = data.get("data", {}).get("sheets", {}).get("sheets", [])
        info = {}
        for sheet in sheets:
            grid = sheet.get("grid_properties", {})
            sheet_id = sheet.get("sheet_id", "")
            rows = grid.get("row_count", 0)
            cols = grid.get("column_count", 0)
            info[sheet_id] = (rows, cols)
        return info
    except Exception:
        return None


def trim_empty_columns(values: list[list[str]]) -> list[list[str]]:
    """移除尾部全为空/None的列"""
    if not values:
        return values
    max_cols = max(len(row) for row in values)
    last_meaningful = 0
    for col_idx in range(max_cols):
        for row in values:
            if col_idx < len(row):
                val = str(row[col_idx]).strip()
                if val and val != "None":
                    last_meaningful = col_idx + 1
                    break
    if last_meaningful == 0:
        last_meaningful = 1
    return [row[:last_meaningful] for row in values]


def clean_cell_value(val) -> str:
    """清理飞书富文本/链接结构，提取纯文本"""
    if isinstance(val, list):
        texts = [seg.get("text", "") for seg in val if isinstance(seg, dict)]
        return "".join(texts)
    if isinstance(val, str):
        stripped = val.strip()
        if stripped.startswith("[{") and ("segmentStyle" in stripped or "cellPosition" in stripped):
            try:
                parsed = json.loads(stripped)
                texts = [seg.get("text", "") for seg in parsed if isinstance(seg, dict)]
                return "".join(texts)
            except (json.JSONDecodeError, ValueError):
                pass
    return str(val) if val is not None else ""


def values_to_markdown(values: list[list[str]]) -> str:
    """将二维数组转换为 Markdown 表格"""
    if not values:
        return "（表格数据为空）"

    # 先清理所有单元格的富文本
    cleaned = [[clean_cell_value(cell) for cell in row] for row in values]

    col_widths = []
    for col_idx in range(len(cleaned[0])):
        max_width = max(
            len(cleaned[row_idx][col_idx]) if col_idx < len(cleaned[row_idx]) else 0
            for row_idx in range(len(cleaned))
        )
        col_widths.append(max_width)

    lines = []

    # 表头
    header_cells = [cleaned[0][i].ljust(col_widths[i]) for i in range(len(cleaned[0]))]
    lines.append("| " + " | ".join(header_cells) + " |")

    # 分隔线
    sep_cells = ["-" * (col_widths[i] + 2) for i in range(len(cleaned[0]))]
    lines.append("|" + "|".join(sep_cells) + "|")

    # 数据行
    for row in cleaned[1:]:
        cells = [row[i].ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i])
                 for i in range(len(cleaned[0]))]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def convert_tables(content: str) -> tuple[str, int, int]:
    """处理文档中的表格标记，返回转换后的内容和统计"""
    sheet_pattern = re.compile(r'<sheet\s+token="[^"]+"\s*/?>')
    matches = list(sheet_pattern.finditer(content))

    if not matches:
        return content, 0, 0

    print(f"📊 找到 {len(matches)} 个内嵌表格")

    # 收集所有唯一的 spreadsheet token，批量获取 sheet 尺寸
    spreadsheet_tokens = set()
    for match in matches:
        token_parts = extract_sheet_token_parts(match.group(0))
        if token_parts:
            spreadsheet_tokens.add(token_parts[0])

    sheet_info_cache: dict[str, dict[str, tuple[int, int]]] = {}
    for token in spreadsheet_tokens:
        info = fetch_spreadsheet_info(token)
        if info:
            sheet_info_cache[token] = info
            print(f"  📋 已获取 {token[:12]}... 的 {len(info)} 个 sheet 尺寸")

    success_count = 0
    fail_count = 0
    converted_content = content

    # 从后往前替换
    for match in reversed(matches):
        sheet_tag = match.group(0)
        token_parts = extract_sheet_token_parts(sheet_tag)

        if not token_parts:
            fail_count += 1
            continue

        spreadsheet_token, sheet_id = token_parts
        print(f"  🔄 处理表格: {spreadsheet_token[:12]}... (sheet: {sheet_id})")

        # 用 sheet 尺寸构建标准 range 格式: sheetId!A1:D7
        cache = sheet_info_cache.get(spreadsheet_token, {})
        dimensions = cache.get(sheet_id)
        if dimensions:
            rows, cols = dimensions
            last_col = col_to_letter(cols)
            range_str = f"{sheet_id}!A1:{last_col}{rows}"
        else:
            range_str = sheet_id  # fallback

        values = fetch_sheet_data(spreadsheet_token, range_str)

        if values is None:
            fail_count += 1
            converted_content = (converted_content[:match.start()] +
                               f"\n⚠️ 表格加载失败: `{spreadsheet_token}` (sheet: {sheet_id})\n" +
                               converted_content[match.end():])
            continue

        values = trim_empty_columns(values)
        markdown_table = values_to_markdown(values)
        converted_content = (converted_content[:match.start()] +
                           "\n" + markdown_table + "\n" +
                           converted_content[match.end():])
        success_count += 1
        print(f"  ✅ {len(values)} 行 x {len(values[0])} 列")

    return converted_content, success_count, fail_count


def main():
    if len(sys.argv) < 3:
        print("使用方法: python feishu_sync.py <url> <output_dir> [name]")
        print("\n示例:")
        print('  python feishu_sync.py https://q1q11nqsd12.feishu.cn/wiki/JP9TwETkWijyCAkaLe8c3JMonAb "接口文档/服务器API/2026-04-17"')
        print('  python feishu_sync.py https://q1q11nqsd12.feishu.cn/wiki/JP9TwETkWijyCAkaLe8c3JMonAb "接口文档/服务器API/2026-04-17" "文档名称"')
        sys.exit(1)

    url = sys.argv[1]
    output_dir = Path(sys.argv[2])
    custom_name = sys.argv[3] if len(sys.argv) > 3 else None

    # 提取 token
    print(f"🔍 解析 URL: {url}")
    doc_token = extract_token(url)

    if not doc_token:
        print("❌ 无法从 URL 中提取文档 token")
        sys.exit(1)

    print(f"✅ 文档 token: {doc_token}")

    # 获取文档内容
    print(f"📥 获取文档内容...")
    skeleton_content = fetch_doc_content(doc_token)

    if not skeleton_content:
        sys.exit(1)

    # 确定文件名
    if custom_name:
        base_name = custom_name
    else:
        # 从文档内容中提取标题（取第一行 # 后的内容）
        title_match = re.search(r'^#\s+(.+)$', skeleton_content, re.MULTILINE)
        base_name = title_match.group(1).strip() if title_match else f"文档_{doc_token[:8]}"

    # 清理文件名中的非法字符
    base_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存骨架文档
    skeleton_path = output_dir / f"{base_name}_骨架.md"
    skeleton_path.write_text(skeleton_content, encoding="utf-8")
    print(f"📄 骨架文档: {skeleton_path}")

    # 转换表格
    print(f"🔄 转换表格...")
    converted_content, success, fail = convert_tables(skeleton_content)

    # 保存完整版
    full_path = output_dir / f"{base_name}.md"
    full_path.write_text(converted_content, encoding="utf-8")
    print(f"📄 完整文档: {full_path}")

    # 统计
    print(f"\n{'='*50}")
    print(f"✅ 同步完成!")
    print(f"  📁 输出目录: {output_dir}")
    print(f"  📄 骨架文档: {skeleton_path.name}")
    print(f"  📄 完整文档: {full_path.name}")
    if success > 0 or fail > 0:
        print(f"  📊 表格: 成功 {success}, 失败 {fail}")

    # 记录到 LOG.md（如果存在）
    log_path = Path("LOG.md")
    if log_path.exists():
        today = datetime.now().strftime("%Y-%m-%d")
        log_entry = f"\n{today} - [同步] 飞书文档: {base_name} → {output_dir}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)


if __name__ == "__main__":
    main()

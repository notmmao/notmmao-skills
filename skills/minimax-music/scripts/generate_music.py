#!/usr/bin/env python3
"""
MiniMax Music Generation CLI
使用 MiniMax API 将歌词转换为音乐
"""

import os
import sys
import argparse
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

import requests

# 加载统一环境变量
load_dotenv(os.path.expanduser("~/.openclaw/.env"))

# 默认配置
DEFAULT_MODEL = "music-2.6"
DEFAULT_PROMPT = "独立民谣,忧郁,内省,渴望,独自漫步,咖啡馆"
DEFAULT_FORMAT = "mp3"
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_BITRATE = 256000

API_URL = "https://api.minimaxi.com/v1/music_generation"
OUTPUT_DIR = Path(os.path.expanduser("~/.cache/minimax-music/"))


def get_api_key() -> str:
    """从环境变量获取 API Key"""
    api_key = os.environ.get("MINIMAX_API_KEY")
    if not api_key:
        print("错误: 未找到 MINIMAX_API_KEY", file=sys.stderr)
        print("\n请在 ~/.openclaw/.env 文件中添加配置:", file=sys.stderr)
        print("  MINIMAX_API_KEY=你的MiniMax API密钥", file=sys.stderr)
        sys.exit(1)
    return api_key


def read_lyrics_from_file(filepath: str) -> str:
    """从文件读取歌词"""
    path = Path(filepath)
    if not path.exists():
        print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    return content.strip()


def generate_music(
    lyrics: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    audio_format: str = DEFAULT_FORMAT,
    cover_audio_path: Optional[str] = None,
    api_key: Optional[str] = None
) -> dict:
    """调用 MiniMax API 生成音乐"""

    if api_key is None:
        api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "audio_setting": {
            "sample_rate": DEFAULT_SAMPLE_RATE,
            "bitrate": DEFAULT_BITRATE,
            "format": audio_format
        }
    }

    # Cover 模式：上传音频提取旋律骨架
    if cover_audio_path:
        with open(cover_audio_path, "rb") as f:
            audio_bytes = f.read()
        payload["cover_audio"] = audio_bytes.hex()
        if lyrics:
            payload["lyrics"] = lyrics
    else:
        # 普通生成模式必须传歌词
        if not lyrics:
            print("错误: 普通生成模式必须提供歌词", file=sys.stderr)
            sys.exit(1)
        payload["lyrics"] = lyrics

    print(f"正在调用 MiniMax API...")
    print(f"  模型: {model}")
    print(f"  风格: {prompt}")
    print(f"  格式: {audio_format}")

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


def save_audio(audio_hex: str, output_path: Path) -> None:
    """将十六进制音频数据保存为文件"""
    # 创建输出目录
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 解码十六进制数据
    audio_data = bytes.fromhex(audio_hex)

    # 写入文件
    output_path.write_bytes(audio_data)


def generate_output_filename(prompt: str, audio_format: str) -> str:
    """生成输出文件名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 从 prompt 中提取简短描述
    style_short = prompt.split(",")[0][:10] if prompt else "music"
    return f"{timestamp}_{style_short}.{audio_format}"


def main():
    parser = argparse.ArgumentParser(
        description="使用 MiniMax API 生成音乐",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认风格
  %(prog)s --lyrics "你的歌词内容"

  # 自定义风格
  %(prog)s --lyrics "歌词" --prompt "流行,欢快"

  # 从文件读取歌词
  %(prog)s --lyrics-file lyrics.txt --output my_song.mp3
        """
    )

    # 歌词输入（二选一，Cover模式下可选）
    lyrics_group = parser.add_mutually_exclusive_group(required=False)
    lyrics_group.add_argument(
        "--lyrics",
        "-l",
        help="直接指定歌词内容"
    )
    lyrics_group.add_argument(
        "--lyrics-file",
        "-f",
        help="从文件读取歌词"
    )

    # Cover 模式参数
    parser.add_argument(
        "--cover",
        "-c",
        help="Cover模式：指定要改编的音频文件路径，提取其旋律骨架"
    )

    # 可选参数
    parser.add_argument(
        "--prompt",
        "-p",
        default=DEFAULT_PROMPT,
        help=f"风格提示词 (默认: '{DEFAULT_PROMPT}')"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件名 (默认: 自动生成时间戳名称)"
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"模型版本 (默认: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "wav", "flac"],
        default=DEFAULT_FORMAT,
        help=f"音频格式 (默认: {DEFAULT_FORMAT})"
    )

    args = parser.parse_args()

    # 获取歌词
    lyrics = ""
    if args.lyrics:
        lyrics = args.lyrics
    elif args.lyrics_file:
        lyrics = read_lyrics_from_file(args.lyrics_file)

    # 生成输出路径
    if args.output:
        output_path = OUTPUT_DIR / args.output
    else:
        filename = generate_output_filename(args.prompt, args.format)
        output_path = OUTPUT_DIR / filename

    # 调用 API 生成音乐
    try:
        result = generate_music(
            lyrics=lyrics,
            prompt=args.prompt,
            model=args.model,
            audio_format=args.format,
            cover_audio_path=args.cover
        )
    except requests.exceptions.HTTPError as e:
        print(f"\nAPI 请求失败: {e}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}", file=sys.stderr)
        except:
            pass
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\n网络请求失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 检查响应
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"\nAPI 返回错误:", file=sys.stderr)
        print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    # 保存音频
    audio_hex = result["data"]["audio"]
    save_audio(audio_hex, output_path)

    # 显示结果信息
    extra_info = result.get("extra_info", {})
    duration_ms = extra_info.get("music_duration", 0)
    duration_sec = duration_ms / 1000 if duration_ms else 0

    print(f"\n[OK] 音乐生成成功!")
    print(f"  保存位置: {output_path.absolute()}")
    print(f"  时长: {duration_sec:.1f} 秒")
    print(f"  格式: {args.format.upper()}")
    print(f"  采样率: {extra_info.get('music_sample_rate')} Hz")
    print(f"  文件大小: {extra_info.get('music_size', 0) / 1024:.1f} KB")

    if result.get("trace_id"):
        print(f"  Trace ID: {result['trace_id']}")


if __name__ == "__main__":
    main()

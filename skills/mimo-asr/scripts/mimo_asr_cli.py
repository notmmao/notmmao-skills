# -*- coding: utf-8 -*-
"""小米 MiMo 语音识别 CLI 工具
支持基于小米 MiMo 官方 API 的语音转文字功能
"""
import os
import sys
import json
import base64
import argparse
from typing import Literal, Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（优先从脚本目录查找，其次从项目根目录）
_script_dir = Path(__file__).parent.parent
_project_root = _script_dir.parent.parent  # skills/mimo-asr 的父级父级
_env_paths = [
    _script_dir / ".env",
    _project_root / ".env",
    Path.cwd() / ".env",
    Path.home() / ".env",
]
load_dotenv(_env_paths[0])  # 优先加载技能目录的 .env
for env_path in _env_paths[1:]:
    if env_path.exists():
        load_dotenv(env_path, override=True)


# API 配置
_API_KEY = os.getenv("MIMO_API_KEY")
_API_URL = os.getenv("MIMO_API_URL", "https://api.xiaomimimo.com/v1/chat/completions")
_MIMO_MODEL = os.getenv("MIMO_API_MODEL_ASR", "mimo-v2.5-asr")

# 类型定义
LANGUAGE = Literal["auto", "zh", "en", "ja", "ko"]
OUTPUT_FORMAT = Literal["text", "json", "srt", "vtt"]

# 支持的音频格式
SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm", ".mp4", ".avi", ".mkv"}

# 最大文件大小 (25MB)
MAX_FILE_SIZE = 25 * 1024 * 1024


def _ensure_configured() -> str:
    """确保已配置 API Key"""
    if not _API_KEY:
        raise ValueError("未配置 MIMO_API_KEY 环境变量，请先设置")
    return _API_KEY


def _get_mime_type(file_path: str) -> str:
    """根据文件扩展名获取 MIME 类型"""
    ext = Path(file_path).suffix.lower()
    mime_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
        ".webm": "audio/webm",
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
    }
    return mime_map.get(ext, "audio/mpeg")


def _audio_to_base64(file_path: str) -> str:
    """将音频文件转换为 base64 编码"""
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode("utf-8")


def _get_audio_duration(file_path: str) -> float:
    """获取音频时长（秒）"""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0
    except Exception:
        pass
    return 0.0


def _format_duration(seconds: float) -> str:
    """格式化时长显示"""
    if seconds <= 0:
        return "未知"
    mins = int(seconds // 60)
    secs = seconds % 60
    if mins > 0:
        return f"{mins}分{secs:.1f}秒"
    return f"{secs:.1f}秒"


def mimo_speech_recognition(
    audio_path: str,
    language: LANGUAGE = "auto",
    stream: bool = False,
) -> dict:
    """语音识别核心功能"""
    # 参数校验
    if not audio_path or not os.path.exists(audio_path):
        raise ValueError(f"音频文件不存在: {audio_path}")

    # 检查文件格式
    ext = Path(audio_path).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的音频格式: {ext}，支持: {', '.join(SUPPORTED_FORMATS)}")

    # 检查文件大小
    file_size = os.path.getsize(audio_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持 {MAX_FILE_SIZE / 1024 / 1024:.0f}MB")

    # 获取音频时长
    duration = _get_audio_duration(audio_path)

    # 转换为 base64
    audio_b64 = _audio_to_base64(audio_path)
    mime_type = _get_mime_type(audio_path)

    # 构建请求
    api_key = _ensure_configured()
    payload = {
        "model": _MIMO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": f"data:{mime_type};base64,{audio_b64}"
                        }
                    }
                ]
            }
        ],
        "asr_options": {
            "language": language
        }
    }

    headers = {"api-key": api_key, "Content-Type": "application/json"}

    if stream:
        # 流式请求
        return _stream_request(payload, headers, duration, audio_path)
    else:
        # 普通请求
        return _normal_request(payload, headers, duration, audio_path)


def _normal_request(payload: dict, headers: dict, duration: float, audio_path: str) -> dict:
    """普通识别请求"""
    import requests

    response = requests.post(_API_URL, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code} {response.text}")

    result = response.json()
    if result.get("error"):
        raise Exception(f"API返回错误: {result['error']}")

    # 提取识别结果
    text = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})

    return {
        "status": "success",
        "message": "语音识别成功",
        "text": text,
        "language": result.get("model", "unknown"),
        "duration_seconds": duration,
        "file_path": audio_path,
        "file_size": os.path.getsize(audio_path),
        "usage": usage
    }


def _stream_request(payload: dict, headers: dict, duration: float, audio_path: str) -> dict:
    """流式识别请求"""
    import requests

    payload["stream"] = True

    response = requests.post(_API_URL, headers=headers, json=payload, stream=True, timeout=120)

    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code} {response.text}")

    full_text = []
    usage = {}

    for line in response.iter_lines():
        if not line:
            continue
        if line.startswith(b"data: "):
            line = line[6:]
        if line.strip() == b"[DONE]":
            break
        try:
            chunk = json.loads(line)
            choices = chunk.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                full_text.append(content)
                # 实时输出
                sys.stdout.write(content)
                sys.stdout.flush()
            # 收集 usage 信息
            if "usage" in chunk:
                usage = chunk["usage"]
        except (json.JSONDecodeError, IndexError, KeyError):
            continue

    print()  # 换行

    return {
        "status": "success",
        "message": "语音识别成功",
        "text": "".join(full_text),
        "language": "auto",
        "duration_seconds": duration,
        "file_path": audio_path,
        "file_size": os.path.getsize(audio_path),
        "usage": usage
    }


def main():
    parser = argparse.ArgumentParser(description="小米 MiMo 语音识别 CLI 工具")
    parser.add_argument("audio_file", nargs="?", help="待识别的音频文件路径")
    parser.add_argument("-l", "--language", default="auto", choices=["auto", "zh", "en", "ja", "ko"], help="识别语言，默认auto自动识别")
    parser.add_argument("-f", "--format", default="text", choices=["text", "json"], help="输出格式")
    parser.add_argument("-j", "--json", action="store_true", help="以JSON格式输出结果")
    parser.add_argument("-q", "--quiet", action="store_true", help="安静模式，仅输出识别文本")
    parser.add_argument("-s", "--stream", action="store_true", help="启用流式输出")

    args = parser.parse_args()

    # 检测是否有输入
    has_stdin = not sys.stdin.isatty()

    # 无输入时打印帮助
    if not args.audio_file and not has_stdin:
        parser.print_help()
        sys.exit(0)

    # 从 stdin 读取
    if not args.audio_file:
        args.audio_file = sys.stdin.read().strip()

    if not args.audio_file:
        print("❌ 错误: 未提供音频文件", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    try:
        result = mimo_speech_recognition(
            audio_path=args.audio_file,
            language=args.language,
            stream=args.stream
        )

        # 格式化输出
        if args.json or args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.quiet:
            # 安静模式：仅输出识别文本
            print(result['text'])
        else:
            # 默认输出：完整信息
            print(f"✅ {result['message']}")
            print()
            print("📝 识别结果:")
            print(f"   {result['text']}")
            print()
            print("📊 音频信息:")
            print(f"   • 文件名: {Path(result['file_path']).name}")
            print(f"   • 时长: {_format_duration(result['duration_seconds'])}")
            print(f"   • 大小: {result['file_size'] / 1024:.2f} KB")
            print(f"   • 语言: {result['language']}")
            if result.get('usage'):
                usage = result['usage']
                print(f"   • Token用量: {usage.get('total_tokens', 'N/A')}")

    except Exception as e:
        error_result = {"status": "error", "message": str(e)}
        if args.json or args.format == "json":
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

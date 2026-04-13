#!/home/ota/.openclaw/claw_venv/bin/python
# -*- coding: utf-8 -*-
"""小米 MiMo 语音合成 CLI 工具
支持基于小米 MiMo 官方 API 的文本转语音功能，自带缓存机制
"""
import os
import sys
import json
import hashlib
import requests
import base64
import argparse
from typing import Literal, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("/home/ota/.openclaw/.env")

# API 配置
_API_KEY = os.getenv("MIMO_API_KEY")
_API_URL = os.getenv("MIMO_API_URL", "https://api.xiaomimimo.com/v1/chat/completions")
_MIMO_MODEL = os.getenv("MIMO_API_MODEL_TTS", "mimo-v2-tts")

# 类型定义
AUDIO_FORMAT = Literal["mp3", "wav", "pcm"]
VOICE_TYPE = Literal["mimo_default", "default_zh", "default_en"]

# 缓存目录（统一管理）
CACHE_DIR = os.path.expanduser("~/.cache/mimo_tts")
os.makedirs(CACHE_DIR, exist_ok=True)


def _ensure_configured() -> str:
    """确保已配置 API Key"""
    if not _API_KEY:
        raise ValueError("未配置 MIMO_API_KEY 环境变量，请先设置")
    return _API_KEY


def mimo_text_to_speech(
    text: str,
    output_path: str = "",
    voice: VOICE_TYPE = "mimo_default",
    audio_format: AUDIO_FORMAT = "mp3",
    speed: float = 1.0,
    style: str = "",
) -> dict:
    """文本转语音核心功能"""
    # 参数校验
    if not text or not text.strip():
        raise ValueError("文本内容不能为空")
    if len(text) > 10000:
        raise ValueError("文本长度不能超过 10000 字符")
    if speed < 0.5 or speed > 2.0:
        raise ValueError("语速必须在 0.5-2.0 范围内")

    # 缓存逻辑
    if not output_path:
        # 生成缓存key
        cache_key = f"{text.strip()}|{voice}|{audio_format}|{speed}|{style.strip()}"
        text_hash = hashlib.md5(cache_key.encode("utf-8")).hexdigest()
        if style.strip():
            # 格式: {md5}_{style}.mp3
            processed_style = style.strip().replace(' ', '_').replace('/', '_').replace('\\', '_')[:20]
            output_path = os.path.join(CACHE_DIR, f"{text_hash}_{processed_style}.{audio_format}")
        else:
            # 无风格时: {md5}.mp3
            output_path = os.path.join(CACHE_DIR, f"{text_hash}.{audio_format}")
        
        # 检查缓存
        if os.path.exists(output_path):
            result = {
                "status": "success",
                "message": "使用缓存文件",
                "cached": True,
                "output_path": output_path,
                "abs_path": os.path.abspath(output_path),
                "file_size": os.path.getsize(output_path),
                "format": audio_format,
                "voice": voice,
                "speed": speed,
                "style": style
            }
            # 生成友好命名副本
            import re
            import shutil
            # 简化文本：取前10个字符，替换特殊字符
            simplified_text = re.sub(r'[^\w\u4e00-\u9fa5]', '_', text.strip()[:10])
            # 处理风格
            processed_style = re.sub(r'[^\w\u4e00-\u9fa5]', '_', style.strip()[:10]) if style.strip() else ""
            # 生成友好文件名
            if processed_style:
                friendly_filename = f"{simplified_text}_{processed_style}.{audio_format}"
            else:
                friendly_filename = f"{simplified_text}.{audio_format}"
            friendly_path = os.path.join(CACHE_DIR, friendly_filename)
            # 拷贝文件
            shutil.copy2(output_path, friendly_path)
            result["friendly_path"] = os.path.abspath(friendly_path)
            result["friendly_filename"] = friendly_filename
            return result

    # 调用API
    api_key = _ensure_configured()
    payload = {
        "model": _MIMO_MODEL,
        "messages": [
            {"role": "user", "content": "请朗读以下内容"},
            {"role": "assistant", "content": f"<style>{style}</style>{text}"}
        ],
        "audio": {
            "format": audio_format,
            "voice": voice,
        },
    }
    if speed != 1.0:
        payload["audio"]["speed"] = speed

    headers = {"api-key": api_key, "Content-Type": "application/json"}
    response = requests.post(_API_URL, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code} {response.text}")
    
    result = response.json()
    if result.get("error"):
        raise Exception(f"API返回错误: {result['error']}")
    
    # 解析音频数据
    audio_b64 = result["choices"][0]["message"]["audio"]["data"]
    audio_bytes = base64.b64decode(audio_b64)

    # 保存文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)

    result = {
        "status": "success",
        "message": "语音合成成功",
        "cached": False,
        "output_path": output_path,
        "abs_path": os.path.abspath(output_path),
        "file_size": len(audio_bytes),
        "format": audio_format,
        "voice": voice,
        "speed": speed,
        "style": style
    }

    # 生成友好命名副本
    import re
    import shutil
    # 简化文本：取前10个字符，替换特殊字符
    simplified_text = re.sub(r'[^\w\u4e00-\u9fa5]', '_', text.strip()[:10])
    # 处理风格
    processed_style = re.sub(r'[^\w\u4e00-\u9fa5]', '_', style.strip()[:10]) if style.strip() else ""
    # 生成友好文件名
    if processed_style:
        friendly_filename = f"{simplified_text}_{processed_style}.{audio_format}"
    else:
        friendly_filename = f"{simplified_text}.{audio_format}"
    friendly_path = os.path.join(CACHE_DIR, friendly_filename)
    # 拷贝文件
    shutil.copy2(output_path, friendly_path)
    result["friendly_path"] = os.path.abspath(friendly_path)
    result["friendly_filename"] = friendly_filename

    return result


def main():
    parser = argparse.ArgumentParser(description="小米 MiMo 语音合成 CLI 工具")
    parser.add_argument("text", nargs="?", help="待合成的文本内容")
    parser.add_argument("-o", "--output", help="输出音频文件路径（可选，默认使用缓存）")
    parser.add_argument("-v", "--voice", default="mimo_default", choices=["mimo_default", "default_zh", "default_en"], help="音色类型，默认mimo_default")
    parser.add_argument("-f", "--format", default="mp3", choices=["mp3", "wav", "pcm"], help="音频格式，默认mp3")
    parser.add_argument("-s", "--speed", type=float, default=1.0, help="语速倍率 0.5-2.0，默认1.0")
    parser.add_argument("-t", "--style", default="", help="朗读风格描述，如\"欢快的语气\"、\"温柔的声音\"")
    parser.add_argument("-j", "--json", action="store_true", help="以JSON格式输出结果")

    args = parser.parse_args()

    # 从标准输入读取文本（如果没有提供text参数）
    if not args.text:
        args.text = sys.stdin.read().strip()

    try:
        result = mimo_text_to_speech(
            text=args.text,
            output_path=args.output,
            voice=args.voice,
            audio_format=args.format,
            speed=args.speed,
            style=args.style
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"✅ {result['message']}")
            print(f"📁 缓存路径: {result['abs_path']}")
            print(f"📄 友好命名: {result['friendly_filename']}")
            print(f"📁 副本路径: {result['friendly_path']}")
            print(f"📦 文件大小: {result['file_size'] / 1024:.2f} KB")
            if result['cached']:
                print("💾 来自缓存")
    except Exception as e:
        error_result = {"status": "error", "message": str(e)}
        if args.json:
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

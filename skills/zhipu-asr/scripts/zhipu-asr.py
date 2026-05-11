#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱 GLM-ASR-2512 语音转文本（长音频分段版）
API: https://open.bigmodel.cn/api/paas/v4/audio/transcriptions
限制: ≤30秒/段, ≤25MB, 支持自动分段拼接
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

API_BASE = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"
MODEL = "glm-asr-2512"
MAX_DURATION = 30  # API 限制 30 秒


def get_api_key() -> str:
    for name in ("ZHIPU_API_KEY", "ZHIPU_API_TOKEN", "BIGMODEL_API_KEY"):
        key = os.environ.get(name)
        if key:
            return key
    return None


def extract_audio(video_path: str, output_dir: str) -> str:
    """从视频提取音频为 mp3"""
    base = Path(video_path).stem
    out = os.path.join(output_dir, f"{base}.mp3")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ar", "16000", "-ac", "1", "-b:a", "32k",
        out,
    ]
    subprocess.run(cmd, capture_output=True)
    return out


def get_audio_duration(path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def split_audio(input_path: str, output_dir: str, segment: int = MAX_DURATION) -> list:
    """按 segment 秒分段切音频，返回片段路径列表"""
    duration = get_audio_duration(input_path)
    segments = []
    # 使用 ffmpeg segment 重新编码为 mp3
    pattern = os.path.join(output_dir, "seg_%03d.mp3")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-f", "segment",
        "-segment_time", str(segment),
        "-vn",  # 去掉视频
        "-ar", "16000", "-ac", "1", "-b:a", "32k",  # 统一编码为 mp3
        "-reset_timestamps", "1",
        pattern,
    ]
    subprocess.run(cmd, capture_output=True)
    # 收集生成的片段并按顺序排列
    for f in sorted(os.listdir(output_dir)):
        if f.startswith("seg_") and f.endswith(".mp3"):
            segments.append(os.path.join(output_dir, f))
    return segments


def transcribe_segment(audio_path: str, api_key: str, prompt: str = None, hotwords: list = None) -> str:
    """转录单个音频片段"""
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": MODEL, "stream": "false"}
    if prompt:
        data["prompt"] = prompt
    if hotwords:
        data["hotwords"] = json.dumps(hotwords)

    mime = "audio/mpeg" if audio_path.lower().endswith(".mp3") else "audio/wav"
    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, mime)}
        resp = requests.post(API_BASE, headers=headers, data=data, files=files, timeout=120)

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

    body = resp.json()
    return body.get("text", "")


def transcribe_long(
    audio_path: str,
    api_key: str,
    prompt: str = None,
    hotwords: list = None,
    keep_segments: bool = False,
) -> str:
    """长音频分段转录并拼接"""
    duration = get_audio_duration(audio_path)
    if duration <= MAX_DURATION:
        return transcribe_segment(audio_path, api_key, prompt, hotwords)

    print(f"⏳ 音频时长 {duration:.1f}s > {MAX_DURATION}s，将自动分段转录...")

    with tempfile.TemporaryDirectory() as tmpdir:
        if keep_segments:
            # 不自动删除，调试用
            tmpdir = tempfile.mkdtemp()

        segments = split_audio(audio_path, tmpdir)
        total = len(segments)
        full_text = ""
        prev_text = ""

        for i, seg in enumerate(segments, 1):
            # 用前一段结尾作为下一段的 prompt 上下文，提升连贯性
            ctx_prompt = prev_text[-500:] if len(prev_text) > 500 else prev_text
            try:
                text = transcribe_segment(seg, api_key, prompt=ctx_prompt or prompt, hotwords=hotwords)
            except RuntimeError as e:
                print(f"\n❌ 第 {i}/{total} 段失败: {e}", file=sys.stderr)
                continue

            # 简单去重：如果当前段开头和上一段结尾有重叠，去掉重复部分
            if full_text and text:
                overlap = 0
                for length in range(min(20, len(text)), 0, -1):
                    if full_text.endswith(text[:length]):
                        overlap = length
                        break
                if overlap:
                    text = text[overlap:]

            full_text += text
            prev_text = text
            print(f"  ✅ 第 {i}/{total} 段完成 ({len(text)} 字)", end="\r" if i < total else "\n", flush=True)

        return full_text


def main():
    parser = argparse.ArgumentParser(description="智谱 GLM-ASR-2512 语音转文本（支持长音频）")
    parser.add_argument("audio", help="音频/视频文件路径")
    parser.add_argument("--key", "-k", help="API Key")
    parser.add_argument("--prompt", "-p", help="上下文提示")
    parser.add_argument("--hotwords", "-w", nargs="+", help="热词列表")
    parser.add_argument("--raw", "-r", action="store_true", help="输出原始 JSON")
    parser.add_argument("--keep-segments", action="store_true", help="保留分段文件（调试用）")
    args = parser.parse_args()

    api_key = args.key or get_api_key()
    if not api_key:
        print("❌ 未找到 API Key，请设置环境变量 ZHIPU_API_KEY", file=sys.stderr)
        sys.exit(1)

    # 如果是视频文件，先提取音频
    audio_path = args.audio
    video_exts = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv")
    if audio_path.lower().endswith(video_exts):
        print("🎬 检测到视频文件，正在提取音频...")
        audio_path = extract_audio(audio_path, tempfile.gettempdir())
        print(f"   音频提取完成: {audio_path}")

    text = transcribe_long(
        audio_path=audio_path,
        api_key=api_key,
        prompt=args.prompt,
        hotwords=args.hotwords,
        keep_segments=args.keep_segments,
    )

    if args.raw:
        print(json.dumps({"text": text}, ensure_ascii=False))
    else:
        print("\n📝 完整转录结果:")
        print(text)


if __name__ == "__main__":
    main()

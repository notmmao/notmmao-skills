#!/usr/bin/env python3
import os
import yt_dlp
import json
import hashlib
import argparse
import imageio_ffmpeg
from loguru import logger

# 配置常量
SAVE_DIR = os.path.expanduser("~/.cache/yt-audio-download")
DOWNLOAD_RECORD = os.path.join(SAVE_DIR, ".downloaded.json")
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
SAVE_PATH_TPL = os.path.join(SAVE_DIR, "%(title)s.%(ext)s")

# 初始化目录和下载记录
os.makedirs(SAVE_DIR, exist_ok=True)
if not os.path.exists(DOWNLOAD_RECORD):
    with open(DOWNLOAD_RECORD, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


def get_url_hash(url: str) -> str:
    """生成URL的MD5哈希作为唯一标识"""
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def is_downloaded(url: str) -> tuple[bool, str]:
    """检查URL是否已经下载过，返回(是否已下载, 本地文件路径)"""
    url_hash = get_url_hash(url)
    with open(DOWNLOAD_RECORD, "r", encoding="utf-8") as f:
        records = json.load(f)
    if url_hash in records:
        return True, records[url_hash]
    return False, ""


def save_download_record(url: str, file_path: str):
    """保存下载记录"""
    url_hash = get_url_hash(url)
    with open(DOWNLOAD_RECORD, "r", encoding="utf-8") as f:
        records = json.load(f)
    records[url_hash] = file_path
    with open(DOWNLOAD_RECORD, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def download_audio(url: str) -> str | None:
    """下载指定URL的音频，返回本地文件路径，下载失败返回None"""
    # 检查重复下载
    downloaded, file_path = is_downloaded(url)
    if downloaded:
        logger.info(f"该URL已下载过，文件路径: {file_path}")
        return file_path

    # yt-dlp下载配置
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': SAVE_PATH_TPL,
        'ffmpeg_location': FFMPEG_PATH,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"开始下载: {url}")
            info = ydl.extract_info(url, download=True)
            file_path = info["requested_downloads"][0]["filepath"]
            logger.success(f"下载完成: {file_path}")
            # 保存下载记录
            save_download_record(url, file_path)
            return file_path
    except yt_dlp.DownloadError as e:
        logger.error(f"下载失败: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description="YT-DLP 音频下载工具")
    parser.add_argument("url", help="要下载音频的视频URL")
    args = parser.parse_args()

    download_audio(args.url)


if __name__ == "__main__":
    main()
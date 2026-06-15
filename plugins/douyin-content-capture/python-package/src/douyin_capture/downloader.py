from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import requests

from .resolver import SHARE_PAGE_UA


def download_file(
    url: str,
    dest: Path,
    *,
    chunk_size: int = 1024 * 256,
    headers: dict[str, str] | None = None,
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req_headers = {
        "User-Agent": SHARE_PAGE_UA,
        "Referer": "https://www.iesdouyin.com/",
    }
    if headers:
        req_headers.update(headers)
    with requests.get(url, headers=req_headers, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with dest.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
    return dest


def download_video_with_ytdlp(source_url: str, dest: Path) -> Path:
    """Fallback for Douyin CDN signatures that reject direct requests."""
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        raise RuntimeError("直连下载失败，且未找到 yt-dlp。请先安装：brew install yt-dlp")

    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        yt_dlp,
        "--no-warnings",
        "--no-playlist",
        "--force-overwrites",
        "--merge-output-format",
        "mp4",
        "-o",
        str(dest),
        source_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        message = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"yt-dlp 下载失败: {message}") from None
    if not dest.exists() or dest.stat().st_size == 0:
        raise RuntimeError("yt-dlp 执行完成，但未生成有效视频文件")
    return dest

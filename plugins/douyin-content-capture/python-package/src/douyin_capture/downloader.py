from __future__ import annotations

from pathlib import Path

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

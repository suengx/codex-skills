from __future__ import annotations

import re
from pathlib import Path

DEFAULT_OUTPUT_ROOT = Path.home() / "Downloads" / "douyin-capture"
TRANSCRIPT_PREVIEW_MAX_CHARS = 200


def _is_cjk(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def sanitize_filename(name: str, max_len: int = 28) -> str:
    compact = re.sub(r"\s+", " ", name.strip())
    pieces: list[str] = []
    last_was_sep = False

    for char in compact:
        keep_char = char.isalnum() or _is_cjk(char)
        if keep_char:
            pieces.append(char.lower() if char.isascii() else char)
            last_was_sep = False
            continue
        if not last_was_sep:
            pieces.append("-")
            last_was_sep = True

    cleaned = "".join(pieces).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    if not cleaned:
        cleaned = "capture"
    if len(cleaned) > max_len:
        shortened = cleaned[:max_len].rstrip("-")
        if "-" in shortened:
            shortened = shortened.rsplit("-", 1)[0]
        cleaned = shortened or cleaned[:max_len].rstrip("-")
    return cleaned or "capture"


def build_output_dir(base: Path, aweme_id: str, title: str) -> Path:
    slug = sanitize_filename(title)
    folder_name = aweme_id if slug == "capture" else f"{aweme_id}-{slug}"
    return base / folder_name


def build_transcript_preview(text: str, max_chars: int = TRANSCRIPT_PREVIEW_MAX_CHARS) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."

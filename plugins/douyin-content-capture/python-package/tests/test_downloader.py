from pathlib import Path

import pytest

from douyin_capture import downloader


def test_ytdlp_fallback_reports_missing_binary(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(downloader.shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="yt-dlp"):
        downloader.download_video_with_ytdlp(
            "https://v.douyin.com/example/",
            tmp_path / "video.mp4",
        )

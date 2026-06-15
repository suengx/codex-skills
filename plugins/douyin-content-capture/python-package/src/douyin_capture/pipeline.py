from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .downloader import download_file, download_video_with_ytdlp
from .report import render_capture_report
from .resolver import DouyinContentMeta, resolve_douyin_share
from .utils import DEFAULT_OUTPUT_ROOT, build_output_dir, build_transcript_preview

SHANGHAI = ZoneInfo("Asia/Shanghai")
DEFAULT_OUTPUT = DEFAULT_OUTPUT_ROOT


@dataclass(frozen=True)
class Settings:
    output_dir: Path = DEFAULT_OUTPUT
    whisper_model: str = "small"
    whisper_device: str = "auto"
    whisper_compute_type: str = "default"
    audio_format: str = "wav"
    audio_sample_rate: int = 16000
    skip_transcribe: bool = False


def _now_shanghai() -> str:
    return datetime.now(SHANGHAI).isoformat()


def _log_progress(percent: int, message: str) -> None:
    percent = max(0, min(100, percent))
    print(f"[douyin-capture] {percent}% {message}", file=sys.stderr, flush=True)


def _to_simplified_if_available(text: str) -> str:
    try:
        from .transcriber import to_simplified_chinese
    except Exception:
        return text
    return to_simplified_chinese(text)


def resolve_content_meta(share_text: str) -> DouyinContentMeta:
    return resolve_douyin_share(share_text)


def _write_transcript_files(
    out_dir: Path,
    meta: DouyinContentMeta,
    body_text: str,
    *,
    segments: list[dict] | None = None,
    whisper_model: str | None = None,
    extra_files: dict[str, str] | None = None,
) -> None:
    transcript_path = out_dir / "transcript.md"
    transcript_json_path = out_dir / "transcript_segments.json"
    meta_path = out_dir / "meta.json"
    report_path = out_dir / "index.html"

    type_label = "图文" if meta.content_type == "image" else "视频"
    transcript_markdown = "\n".join(
        [
            "# 抖音内容转写记录",
            "",
            f"- 类型: {type_label}",
            f"- 标题: {_to_simplified_if_available(meta.title)}",
            f"- 作者: {_to_simplified_if_available(meta.author or '未知')}",
            f"- 作品ID: {meta.aweme_id}",
            f"- 来源: {meta.source_url}",
            f"- 处理时间: {_now_shanghai()}",
            "",
            "## 文案",
            "",
            body_text,
            "",
        ]
    )
    transcript_path.write_text(transcript_markdown, encoding="utf-8")
    transcript_json_path.write_text(
        json.dumps(
            {
                "meta": asdict(meta),
                "segments": segments or [],
                "full_text": body_text,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    files = {
        "html": report_path.name,
        "transcript": transcript_path.name,
        "transcript_segments": transcript_json_path.name,
        **(extra_files or {}),
        "meta": meta_path.name,
    }
    meta_payload = {
        **asdict(meta),
        "processed_at": _now_shanghai(),
        "whisper_model": whisper_model,
        "files": files,
    }
    meta_path.write_text(
        json.dumps(
            meta_payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    render_capture_report(
        out_dir,
        meta=meta_payload,
        files=files,
        transcript_preview=build_transcript_preview(body_text),
        transcript_markdown=transcript_markdown,
        transcript_body=body_text,
    )


def _process_image_note(meta: DouyinContentMeta, out_dir: Path) -> None:
    _log_progress(30, "检测到图文内容，开始下载图片")
    images_dir = out_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    urls_path = out_dir / "image_urls.txt"
    urls_path.write_text("\n".join(meta.image_urls) + "\n", encoding="utf-8")

    for i, url in enumerate(meta.image_urls, start=1):
        total = max(len(meta.image_urls), 1)
        percent = 30 + int((i - 1) * 50 / total)
        _log_progress(percent, f"下载图片 {i}/{total}")
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".webp" in url.lower():
            ext = ".webp"
        dest = images_dir / f"{i:02d}{ext}"
        if not dest.exists():
            download_file(url, dest)

    body = _to_simplified_if_available(meta.title)
    _log_progress(90, "写入结果文件")
    _write_transcript_files(
        out_dir,
        meta,
        body,
        extra_files={
            "images_dir": images_dir.name,
            "image_urls": urls_path.name,
        },
    )
    _log_progress(100, "完成")


def _process_video(meta: DouyinContentMeta, out_dir: Path, cfg: Settings) -> None:
    video_path = out_dir / "video.mp4"
    audio_path = out_dir / f"audio.{cfg.audio_format}"
    download_url_path = out_dir / "download_url.txt"

    download_url_path.write_text(meta.download_url + "\n", encoding="utf-8")

    if not video_path.exists():
        _log_progress(35, "开始下载无水印视频")
        try:
            download_file(meta.download_url, video_path)
        except Exception as direct_error:
            if video_path.exists():
                video_path.unlink()
            _log_progress(45, "直连下载失败，改用 yt-dlp 下载视频")
            try:
                download_video_with_ytdlp(meta.source_url, video_path)
            except Exception as fallback_error:
                raise RuntimeError(
                    f"视频下载失败。直连错误: {direct_error}; yt-dlp 错误: {fallback_error}"
                ) from fallback_error

    if cfg.skip_transcribe:
        _log_progress(90, "已按要求跳过转写，写入结果文件")
        _write_transcript_files(
            out_dir,
            meta,
            "",
            extra_files={
                "video": video_path.name,
                "download_url": download_url_path.name,
            },
        )
        _log_progress(100, "完成")
        return

    if not audio_path.exists():
        _log_progress(55, "开始提取音频")
        from .audio_extractor import extract_audio

        extract_audio(
            video_path,
            audio_path,
            sample_rate=cfg.audio_sample_rate,
            audio_format=cfg.audio_format,
        )

    _log_progress(70, f"开始转写音频（模型: {cfg.whisper_model}）")
    from .transcriber import transcribe_audio

    result = transcribe_audio(
        audio_path,
        model_size=cfg.whisper_model,
        device=cfg.whisper_device,
        compute_type=cfg.whisper_compute_type,
    )
    _log_progress(90, "转写完成，正在写入结果文件")

    _write_transcript_files(
        out_dir,
        meta,
        result.text,
        segments=result.segments,
        whisper_model=cfg.whisper_model,
        extra_files={
            "video": video_path.name,
            "audio": audio_path.name,
            "download_url": download_url_path.name,
        },
    )
    _log_progress(100, "完成")


def process_douyin_share(share_text: str, settings: Settings | None = None) -> Path:
    cfg = settings or Settings()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    _log_progress(10, "开始解析抖音分享链接")
    meta = resolve_content_meta(share_text)
    out_dir = build_output_dir(cfg.output_dir, meta.aweme_id, meta.title)
    out_dir.mkdir(parents=True, exist_ok=True)

    if meta.content_type == "image":
        _process_image_note(meta, out_dir)
    else:
        _process_video(meta, out_dir, cfg)

    return out_dir

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .doctor import run_doctor
from .utils import DEFAULT_OUTPUT_ROOT, TRANSCRIPT_PREVIEW_MAX_CHARS, build_transcript_preview

WHISPER_MODELS = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
DEFAULT_OUTPUT = DEFAULT_OUTPUT_ROOT


def _load_pipeline() -> Any:
    from .pipeline import Settings, process_douyin_share, resolve_content_meta

    return Settings, process_douyin_share, resolve_content_meta


def _to_simplified_if_available(text: str) -> str:
    try:
        from .transcriber import to_simplified_chinese
    except Exception:
        return text
    return to_simplified_chinese(text)


def _read_transcript_body(out_dir: Path) -> str:
    candidate_paths = [out_dir / "transcript.md", out_dir / "transcript.txt"]
    for path in candidate_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("## 文案", "--- 文案 ---"):
            if marker in text:
                return text.split(marker, 1)[1].strip()
        return text.strip()
    return ""


def _build_artifact_paths(out_dir: Path, files: dict[str, str]) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    for key, value in files.items():
        artifacts[key] = str((out_dir / value).resolve())
    artifacts["out_dir"] = str(out_dir.resolve())
    return artifacts


def _build_entrypoints(artifacts: dict[str, str]) -> dict[str, str]:
    return {
        "browser_html": artifacts.get("html", ""),
        "open_folder": artifacts.get("out_dir", ""),
    }


def _meta_to_json(meta: Any) -> dict[str, Any]:
    data = asdict(meta)
    data["title"] = _to_simplified_if_available(data["title"])
    data["author"] = _to_simplified_if_available(data.get("author") or "")
    return data


def cmd_doctor(args: argparse.Namespace) -> int:
    result = run_doctor()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result["ok"] else "FAIL"
        print(f"doctor: {status}")
        for err in result["errors"]:
            print(f"  - {err}")
    return 0 if result["ok"] else 1


def cmd_info(args: argparse.Namespace) -> int:
    try:
        _settings, _process_douyin_share, resolve_content_meta = _load_pipeline()
        meta = resolve_content_meta(args.url)
        payload = {"ok": True, **_meta_to_json(meta)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"类型: {meta.content_type}")
            print(f"标题: {_to_simplified_if_available(meta.title)}")
            print(f"作者: {_to_simplified_if_available(meta.author)}")
            print(f"作品ID: {meta.aweme_id}")
            if meta.download_url:
                print(f"下载地址: {meta.download_url}")
        return 0
    except Exception as exc:
        payload = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"错误: {exc}")
        return 1


def cmd_extract(args: argparse.Namespace) -> int:
    model = args.model if args.model in WHISPER_MODELS else "small"
    Settings, process_douyin_share, _resolve_content_meta = _load_pipeline()
    settings = Settings(
        output_dir=args.output,
        whisper_model=model,
        skip_transcribe=args.skip_transcribe,
    )
    try:
        out_dir = process_douyin_share(args.url, settings=settings)
        meta_path = out_dir / "meta.json"
        meta: dict[str, Any] = {}
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

        transcript = _read_transcript_body(out_dir)
        files = meta.get("files", {})
        artifacts = _build_artifact_paths(out_dir, files)
        entrypoints = _build_entrypoints(artifacts)
        transcript_preview = build_transcript_preview(transcript)

        payload = {
            "ok": True,
            "output_root": str(settings.output_dir.resolve()),
            "out_dir": str(out_dir.resolve()),
            "out_dir_name": out_dir.name,
            "aweme_id": meta.get("aweme_id", ""),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "content_type": meta.get("content_type", "video"),
            "transcript": transcript,
            "transcript_preview": transcript_preview,
            "transcript_preview_max_chars": TRANSCRIPT_PREVIEW_MAX_CHARS,
            "files": files,
            "artifacts": artifacts,
            "entrypoints": entrypoints,
            "skip_transcribe": args.skip_transcribe,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"完成: {out_dir.resolve()}")
            if transcript_preview:
                print(f"文案预览: {transcript_preview}")
        return 0
    except Exception as exc:
        payload = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"错误: {exc}")
        return 1


def _add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="输出 JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Douyin share link capture CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="检查运行环境")
    _add_json_flag(doctor_parser)

    info_parser = sub.add_parser("info", help="仅解析元数据")
    _add_json_flag(info_parser)
    info_parser.add_argument("url", help="抖音分享链接或整段分享文案")

    extract_parser = sub.add_parser("extract", help="完整提取（下载 + 可选转写）")
    _add_json_flag(extract_parser)
    extract_parser.add_argument("url", help="抖音分享链接或整段分享文案")
    extract_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"输出目录（默认: {DEFAULT_OUTPUT}）",
    )
    extract_parser.add_argument(
        "--model",
        default="small",
        choices=WHISPER_MODELS,
        help="Whisper 模型（默认: small）",
    )
    extract_parser.add_argument(
        "--skip-transcribe",
        action="store_true",
        help="仅下载，不转写（视频）",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "doctor":
        return cmd_doctor(args)
    if args.command == "info":
        return cmd_info(args)
    if args.command == "extract":
        return cmd_extract(args)
    parser.print_help()
    return 1


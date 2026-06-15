from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
CANDIDATE_PYTHONS = (
    "python3.13",
    "python3.12",
    "python3.11",
    "python3.10",
    "python3",
    "python",
)


def check_python() -> dict:
    version = sys.version_info
    ok = version >= MIN_PYTHON
    return {
        "ok": ok,
        "version": f"{version.major}.{version.minor}.{version.micro}",
        "executable": sys.executable,
    }


def check_ffmpeg() -> dict:
    path = shutil.which("ffmpeg")
    return {"ok": path is not None, "path": path}


def check_package(name: str) -> dict:
    spec = importlib.util.find_spec(name)
    return {"ok": spec is not None, "installed": spec is not None}


def discover_python_interpreters() -> list[dict]:
    discovered: list[dict] = []
    seen: set[str] = set()

    candidates = [sys.executable, *CANDIDATE_PYTHONS]
    for candidate in candidates:
        path = shutil.which(candidate) if Path(candidate).name == candidate else candidate
        if not path or path in seen:
            continue
        seen.add(path)
        try:
            proc = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            continue

        version_text = (proc.stdout or proc.stderr).strip()
        version_match = version_text.replace("Python ", "", 1)
        parts = version_match.split(".")
        version_tuple = tuple(int(part) for part in parts[:3] if part.isdigit())
        discovered.append(
            {
                "path": path,
                "version": version_match or "unknown",
                "ok": version_tuple >= MIN_PYTHON,
            }
        )

    return discovered


def run_doctor() -> dict:
    python = check_python()
    interpreters = discover_python_interpreters()
    ffmpeg = check_ffmpeg()
    packages = {
        "requests": check_package("requests"),
        "faster_whisper": check_package("faster_whisper"),
        "zhconv": check_package("zhconv"),
    }

    errors: list[str] = []
    if not python["ok"]:
        errors.append("需要 Python 3.10 或更高版本")
    if not packages["requests"]["ok"]:
        errors.append("缺少 requests：请安装 douyin-capture 包依赖")
    if not ffmpeg["ok"]:
        errors.append("缺少 ffmpeg（视频转写需要）：brew install ffmpeg 或 apt install ffmpeg")
    if not packages["zhconv"]["ok"]:
        errors.append("缺少 zhconv：请安装 douyin-capture 包依赖")
    if not packages["faster_whisper"]["ok"]:
        errors.append("缺少 faster-whisper：请安装 douyin-capture 包依赖")

    scripts_dir = Path(__file__).resolve().parent
    ok = python["ok"] and packages["requests"]["ok"]
    recommended_python = next((item for item in interpreters if item["ok"]), None)

    notes = [
        "info 命令仅需 requests",
        "extract 视频转写需要 ffmpeg 与 faster-whisper",
        "extract 图文仅需 requests",
    ]
    if not python["ok"] and recommended_python:
        notes.append(
            f"检测到可用解释器：{recommended_python['path']} ({recommended_python['version']})"
        )

    return {
        "ok": ok,
        "python": python,
        "interpreters": interpreters,
        "recommended_python": recommended_python,
        "ffmpeg": ffmpeg,
        "packages": packages,
        "scripts_dir": str(scripts_dir),
        "errors": errors,
        "notes": notes,
    }

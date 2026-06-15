#!/usr/bin/env python3
"""Skill wrapper around the installable douyin_capture package."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_SRC = Path(__file__).resolve().parents[3] / "python-package" / "src"
VENV_DIR = SCRIPT_DIR / ".venv"
BOOTSTRAP_ENV = "DOUYIN_CAPTURE_BOOTSTRAPPED"
MIN_PYTHON = (3, 10)


def _full_extract_requested(argv: list[str]) -> bool:
    return "extract" in argv and "--skip-transcribe" not in argv


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _av_compatible() -> bool:
    try:
        import av
    except Exception:
        return False
    return hasattr(av, "audio")


def _candidate_python() -> str | None:
    for name in ("python3.13", "python3.12", "python3.11", "python3.10"):
        path = shutil.which(name)
        if not path:
            continue
        proc = subprocess.run([path, "--version"], capture_output=True, text=True, check=False)
        version = (proc.stdout or proc.stderr).replace("Python ", "").strip()
        parts = version.split(".")
        try:
            version_tuple = tuple(int(part) for part in parts[:2])
        except ValueError:
            continue
        if version_tuple >= MIN_PYTHON:
            return path
    return None


def _ensure_bootstrap(argv: list[str]) -> None:
    if os.environ.get(BOOTSTRAP_ENV) == "1":
        return
    if not _full_extract_requested(argv):
        return
    if (
        sys.version_info >= MIN_PYTHON
        and _module_available("requests")
        and _module_available("faster_whisper")
        and _module_available("zhconv")
        and _av_compatible()
    ):
        return

    venv_python = VENV_DIR / "bin" / "python"
    python = _candidate_python()

    def create_venv() -> None:
        if not python:
            raise RuntimeError("完整转写需要 Python 3.10+，但未找到可用解释器")
        print("[douyin-capture] 5% 初始化 Python 运行环境", file=sys.stderr, flush=True)
        subprocess.run([python, "-m", "venv", str(VENV_DIR)], check=True)

    if not venv_python.exists():
        create_venv()

    def install_requirements() -> None:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(SCRIPT_DIR / "requirements.txt")],
            check=True,
            cwd=SCRIPT_DIR,
        )

    print("[douyin-capture] 8% 安装或更新转写依赖", file=sys.stderr, flush=True)
    try:
        install_requirements()
    except subprocess.CalledProcessError:
        backup = SCRIPT_DIR / f".venv.bad-{int(time.time())}"
        if VENV_DIR.exists():
            VENV_DIR.rename(backup)
        create_venv()
        install_requirements()

    env = {**os.environ, BOOTSTRAP_ENV: "1"}
    os.execve(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *argv[1:]], env)


_ensure_bootstrap(sys.argv)

if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from douyin_capture.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

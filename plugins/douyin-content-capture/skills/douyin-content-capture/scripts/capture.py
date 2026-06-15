#!/usr/bin/env python3
"""Skill wrapper around the installable douyin_capture package."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_SRC = Path(__file__).resolve().parents[3] / "python-package" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from douyin_capture.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

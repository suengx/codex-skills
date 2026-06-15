# Installation

## Copy the skill

Copy the entire `douyin-content-capture/` directory (must contain `SKILL.md`) into one of these locations:

| Scope | Path |
|-------|------|
| User (generic) | `~/.agents/skills/douyin-content-capture/` |
| Claude Code | `~/.claude/skills/douyin-content-capture/` |
| Cursor | `~/.cursor/skills/douyin-content-capture/` |
| Codex | `~/.codex/skills/douyin-content-capture/` |
| Project | `.claude/skills/`, `.cursor/skills/`, or `.github/skills/` |

The folder name must match the skill `name`: `douyin-content-capture`.

## Python dependencies

```bash
cd <skill-root>/scripts
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

This installs the bundled local package from `../../../python-package`.

## System dependencies

| Tool | Required for | Install |
|------|--------------|---------|
| Python 3.10+ | All commands | System package manager |
| FFmpeg | Video transcription (`extract` without `--skip-transcribe`) | `brew install ffmpeg` / `sudo apt install ffmpeg` |

## Verify

```bash
cd <skill-root>/scripts
source .venv/bin/activate
python capture.py doctor --json
```

- `info` works when `ok: true` (Python + requests)
- Full video `extract` also needs `ffmpeg` and `faster-whisper` with no errors in `errors[]`

## Agent note

Use the absolute path to `<skill-root>/scripts` when running `capture.py`. Do not assume the skill lives inside the user's current project directory.

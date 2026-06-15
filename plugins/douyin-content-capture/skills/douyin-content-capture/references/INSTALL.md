# 安装说明

## 复制技能目录

将完整的 `douyin-content-capture/` 目录复制到下列任一位置，目录中必须包含 `SKILL.md`：

| 范围 | 路径 |
|------|------|
| 通用用户目录 | `~/.agents/skills/douyin-content-capture/` |
| Claude Code | `~/.claude/skills/douyin-content-capture/` |
| Cursor | `~/.cursor/skills/douyin-content-capture/` |
| Codex | `~/.codex/skills/douyin-content-capture/` |
| 项目级目录 | `.claude/skills/`、`.cursor/skills/` 或 `.github/skills/` |

目录名必须与 skill 的 `name` 一致，也就是 `douyin-content-capture`。

## Python 依赖

```bash
cd <skill-root>/scripts
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

这会安装同一插件目录内打包好的本地 Python 包：`../../../python-package`。

## 系统依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| Python 3.10+ | 所有命令 | 系统包管理器 |
| yt-dlp | 直连视频下载被 Douyin CDN 拒绝时的 fallback | `brew install yt-dlp` / `pipx install yt-dlp` |
| FFmpeg | 视频转写（`extract` 且未指定 `--skip-transcribe`） | `brew install ffmpeg` / `sudo apt install ffmpeg` |

## 验证

```bash
cd <skill-root>/scripts
source .venv/bin/activate
python capture.py doctor --json
```

- `ok: true` 代表 `info` 已可使用（Python + requests 就够）
- 若要完整视频转写，`errors[]` 中不应再出现 `ffmpeg` 与 `faster-whisper` 缺失项
- 完整 `extract` 会在缺少转写依赖时自动创建 `scripts/.venv` 并安装 `requirements.txt`

## Agent 备注

运行 `capture.py` 时请使用 `<skill-root>/scripts` 的绝对路径，不要假设 skill 位于用户当前项目目录中。

# Troubleshooting

## Share page has no SSR data

**Error:** `分享页未找到内嵌公开数据（_ROUTER_DATA / RENDER_DATA）`

**Agent actions:**

1. Confirm the URL is a Douyin share link (see [URLS.md](URLS.md))
2. Ask user to copy the **App share short link** (`v.douyin.com`)
3. Retry `capture.py info URL --json`

## Link not found in input

**Error:** `未在输入中找到抖音链接`

Pass the full share text including the `https://` URL, or only the URL string.

## FFmpeg missing

**Error:** `未找到 ffmpeg`

Video `extract` without `--skip-transcribe` requires FFmpeg.

- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

Or use `--skip-transcribe` to download only.

## Whisper slow or warnings

- CPU + `small` model: several minutes for long videos is normal
- `float16 → float32` warning on CPU can be ignored
- Suggest `--model tiny` or `--model base` for speed

## Image note: no text in images

The skill uses `desc` caption only. Text rendered inside images is **not** OCR'd. Tell the user this limitation.

## doctor ok but extract fails

| Symptom | Cause | Fix |
|---------|-------|-----|
| Video extract fails after download | FFmpeg missing | Install ffmpeg |
| Transcribe fails | faster-whisper not installed | `pip install -r requirements.txt` |
| Download 403 | CDN header issue | Retry; use fresh share link |

## Agent must not

- Invent CDN URLs from page inspection
- Skip `capture.py` and call `requests` on Douyin directly
- Store output in user workspace without permission (use `~/Downloads/douyin-capture` by default)

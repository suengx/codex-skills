# Output schema

Default output root: `~/Downloads/douyin-capture/`

Each work is saved to: `{output_root}/{aweme_id}-{clean_slug}/`

## Video output

```
{aweme_id}-{slug}/
├── index.html
├── video.mp4
├── audio.wav              # only when transcribed
├── download_url.txt
├── transcript.md
├── transcript_segments.json
└── meta.json
```

## Image note output

```
{aweme_id}-{slug}/
├── index.html
├── images/01.jpg …
├── image_urls.txt
├── transcript.md
└── meta.json
```

## transcript.md

Markdown header fields, then a section heading, then body:

```md
# Douyin Capture Transcript

- 类型: 视频
- 标题: ...
- 作者: ...
- 作品ID: ...
- 来源: ...
- 处理时间: 2026-06-12T20:00:00+08:00

## 文案

（正文）
```

Agents should read body text after `## 文案`. The CLI `extract --json` field `transcript` contains this body only.
The CLI `extract --json` field `transcript_preview` contains a single-line truncated preview capped at 200 characters.

## index.html

Every successful `extract` writes a self-contained local report page:

- modern static layout
- local playback for common video/audio formats
- transcript preview and full markdown
- direct links to all generated artifacts
- graceful fallback to download links when the browser cannot play a media type

## meta.json

| Field | Type | Description |
|-------|------|-------------|
| `aweme_id` | string | Work ID |
| `title` | string | Description / caption |
| `author` | string | Nickname |
| `content_type` | string | `video` or `image` |
| `source_url` | string | Original user input URL |
| `download_url` | string | Video CDN URL (video only) |
| `image_urls` | string[] | Image CDN URLs (image only) |
| `processed_at` | string | ISO 8601, Asia/Shanghai |
| `whisper_model` | string \| null | Model used, if transcribed |
| `files` | object | Relative filenames in output dir |

## CLI JSON mapping

| CLI field | Source |
|-----------|--------|
| `output_root` | Absolute output root, defaulting to `~/Downloads/douyin-capture` |
| `out_dir_name` | Final directory name under `output_root` |
| `transcript` | Body after `## 文案` in `transcript.md` |
| `transcript_preview` | Single-line truncated preview of `transcript` (200 chars max) |
| `transcript_preview_max_chars` | Preview cap, currently `200` |
| `files` | `meta.json` → `files` |
| `artifacts` | Absolute paths built from `out_dir` + `files` |
| `entrypoints.browser_html` | Friendly browser-open target for `index.html` |
| `entrypoints.open_folder` | Friendly folder-open target for the capture directory |
| `out_dir` | Absolute path to work directory |

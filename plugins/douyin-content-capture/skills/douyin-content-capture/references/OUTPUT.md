# 输出结构

默认输出目录：`~/Downloads/douyin-capture/`

每条作品会保存到：`{output_root}/{aweme_id}-{clean_slug}/`

## 视频输出

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

## 图文输出

```
{aweme_id}-{slug}/
├── index.html
├── images/01.jpg …
├── image_urls.txt
├── transcript.md
└── meta.json
```

## transcript.md

文件结构是：Markdown 头部字段，然后是小节标题，再跟正文：

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

Agent 应从 `## 文案` 之后读取正文。CLI `extract --json` 里的 `transcript` 只包含这段正文。
`transcript_preview` 是正文的单行截断预览，最长 200 个字符。

## index.html

每次成功执行 `extract`，都会生成一个独立可打开的本地报告页，包含：

- 静态本地页面
- 常见视频/音频格式的本地播放
- 文案预览和完整内容
- 所有产物的直接链接
- 浏览器无法播放某种媒体时，自动退化为下载入口

## meta.json

| 字段 | 类型 | 说明 |
|------|------|------|
| `aweme_id` | string | 作品 ID |
| `title` | string | 标题或配文 |
| `author` | string | 作者昵称 |
| `content_type` | string | `video` or `image` |
| `source_url` | string | 用户给出的原始链接 |
| `download_url` | string | 视频下载地址（仅视频） |
| `image_urls` | string[] | 图片下载地址（仅图文） |
| `processed_at` | string | ISO 8601, Asia/Shanghai |
| `whisper_model` | string \| null | 转写时使用的模型 |
| `files` | object | 输出目录中的相对文件名 |

## CLI JSON 字段映射

| CLI 字段 | 含义 |
|-----------|------|
| `output_root` | 绝对输出根目录，默认是 `~/Downloads/douyin-capture` |
| `out_dir_name` | `output_root` 下最终生成的目录名 |
| `transcript` | `transcript.md` 中 `## 文案` 之后的正文 |
| `transcript_preview` | 正文的单行截断预览（最多 200 字符） |
| `transcript_preview_max_chars` | 预览最大字符数，当前为 `200` |
| `files` | `meta.json` → `files` |
| `artifacts` | 由 `out_dir` 和 `files` 拼出的绝对路径 |
| `entrypoints.browser_html` | 推荐直接在浏览器中打开的 `index.html` |
| `entrypoints.open_folder` | 推荐直接打开的结果目录 |
| `out_dir` | 最终产物目录的绝对路径 |

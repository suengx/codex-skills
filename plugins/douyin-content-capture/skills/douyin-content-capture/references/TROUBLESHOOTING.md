# 故障排查

## 分享页没有 SSR 数据

**错误：** `分享页未找到内嵌公开数据（_ROUTER_DATA / RENDER_DATA）`

**Agent 处理方式：**

1. 确认输入的是抖音分享链接（见 [URLS.md](URLS.md)）
2. 请用户重新复制 **App 分享短链**（`v.douyin.com`）
3. 再次运行 `capture.py info URL --json`

## 输入中没有找到链接

**错误：** `未在输入中找到抖音链接`

请传入完整分享文案（包含 `https://` 链接），或者只传链接本身。

## 缺少 FFmpeg

**错误：** `未找到 ffmpeg`

视频执行 `extract` 且未指定 `--skip-transcribe` 时，必须安装 FFmpeg。

- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt install ffmpeg`

如果只下载、不转写，可以改用 `--skip-transcribe`。

## Whisper 很慢或出现警告

- CPU + `small` 模型处理长视频时，几分钟是正常现象
- CPU 上出现 `float16 → float32` 警告通常可以忽略
- 如果更关注速度，建议改用 `--model tiny` 或 `--model base`

## 图文内容里嵌在图片里的文字提不出来

当前 skill 只使用 `desc` 配文，不做 OCR，所以图片里直接写上的文字不会被识别。需要明确告诉用户这是当前限制。

## doctor 正常，但 extract 失败

| 现象 | 原因 | 修复方式 |
|------|------|----------|
| 视频下载后处理失败 | 缺少 FFmpeg | 安装 ffmpeg |
| 转写失败 | 未安装 faster-whisper | `pip install -r requirements.txt` |
| 下载返回 403 | CDN Header 问题 | 重试，或换一条新的分享链接 |

## Agent 禁止事项

- 不要通过手工解析页面来伪造 CDN 地址
- 不要绕过 `capture.py`，直接自己对 Douyin 页面发 `requests`
- 未经允许，不要把输出写进用户当前工作区；默认使用 `~/Downloads/douyin-capture`

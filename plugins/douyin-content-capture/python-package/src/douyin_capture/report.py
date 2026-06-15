from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import quote

VIDEO_MIME_TYPES = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".ogv": "video/ogg",
}

AUDIO_MIME_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
}

ARTIFACT_ORDER = [
    "html",
    "video",
    "audio",
    "transcript",
    "transcript_segments",
    "meta",
    "download_url",
    "image_urls",
    "images_dir",
]


def _href_for_relative_path(relative_path: str) -> str:
    return quote(Path(relative_path).as_posix(), safe="/-_.()")


def _artifact_rows(files: dict[str, str]) -> str:
    keys = sorted(files.keys(), key=lambda key: (ARTIFACT_ORDER.index(key) if key in ARTIFACT_ORDER else 999, key))
    rows: list[str] = []
    label_map = {
        "html": "浏览页面",
        "video": "视频文件",
        "audio": "音频文件",
        "transcript": "转写文稿",
        "transcript_segments": "分段文稿",
        "meta": "元数据",
        "download_url": "下载地址",
        "image_urls": "图片地址",
        "images_dir": "图片目录",
    }
    for key in keys:
        relative_path = files[key]
        href = _href_for_relative_path(relative_path)
        label = escape(label_map.get(key, key.replace("_", " ")))
        rows.append(
            f"""
            <li class="artifact-item">
              <div class="artifact-head">
                <span class="artifact-name">{label}</span>
                <button class="action-chip action-chip-small" type="button" data-copy="{escape(relative_path)}">复制路径</button>
              </div>
              <a class="artifact-link" href="{href}" download>{escape(relative_path)}</a>
            </li>
            """
        )
    return "\n".join(rows)


def _render_video(relative_path: str) -> str:
    ext = Path(relative_path).suffix.lower()
    mime_type = VIDEO_MIME_TYPES.get(ext, "video/mp4")
    href = _href_for_relative_path(relative_path)
    return f"""
    <section class="media-panel">
      <div class="media-label">视频预览</div>
      <video class="video-player" controls preload="metadata" playsinline>
        <source src="{href}" type="{mime_type}">
      </video>
    </section>
    """


def _render_audio(relative_path: str) -> str:
    ext = Path(relative_path).suffix.lower()
    mime_type = AUDIO_MIME_TYPES.get(ext, "audio/mpeg")
    href = _href_for_relative_path(relative_path)
    return f"""
    <section class="media-panel media-panel-audio">
      <div class="media-label">音频预览</div>
      <audio class="audio-player" controls preload="metadata">
        <source src="{href}" type="{mime_type}">
      </audio>
    </section>
    """


def _normalize_transcript_body(transcript_body: str, transcript_markdown: str) -> str:
    body = transcript_body.strip()
    if body.startswith("#") and "## 文案" in body:
        return body.split("## 文案", 1)[1].strip()
    markdown = transcript_markdown.strip()
    if markdown.startswith("#") and "## 文案" in markdown:
        return markdown.split("## 文案", 1)[1].strip()
    return body


def _render_transcript_html(transcript_body: str, transcript_preview: str) -> str:
    lines = [line.strip() for line in transcript_body.splitlines() if line.strip()]
    if not lines:
        fallback = transcript_preview.strip() or "暂无转写内容。"
        lines = [fallback]
    return "\n".join(f"<p>{escape(line)}</p>" for line in lines)


def render_capture_report(
    out_dir: Path,
    *,
    meta: dict,
    files: dict[str, str],
    transcript_preview: str,
    transcript_markdown: str,
    transcript_body: str,
) -> Path:
    title_text = meta.get("title") or out_dir.name
    title = escape(title_text)
    author = escape(meta.get("author") or "未知")
    aweme_id = escape(meta.get("aweme_id") or "")
    content_type_raw = str(meta.get("content_type") or "unknown").lower()
    content_type = escape({"video": "视频", "image": "图文"}.get(content_type_raw, content_type_raw))
    out_dir_text = str(out_dir.resolve())
    out_dir_html = escape(out_dir_text)
    transcript_text = _normalize_transcript_body(transcript_body, transcript_markdown)
    transcript_copy = escape(transcript_text or transcript_preview or "")
    transcript_html = _render_transcript_html(transcript_text, transcript_preview)

    media_sections: list[str] = []
    if "video" in files:
        media_sections.append(_render_video(files["video"]))
    if "audio" in files:
        media_sections.append(_render_audio(files["audio"]))

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #f5f6f8;
      --bg-soft: #eef1f5;
      --surface: rgba(255, 255, 255, 0.84);
      --surface-strong: rgba(255, 255, 255, 0.96);
      --surface-muted: #f7f8fa;
      --line: rgba(15, 23, 42, 0.08);
      --line-strong: rgba(37, 99, 235, 0.24);
      --text: #162033;
      --text-soft: #566277;
      --accent: #2563eb;
      --accent-soft: rgba(37, 99, 235, 0.08);
      --shadow: 0 22px 52px rgba(15, 23, 42, 0.08);
      --shadow-soft: 0 8px 24px rgba(15, 23, 42, 0.05);
      --radius-shell: 28px;
      --radius-panel: 22px;
      --radius-inner: 18px;
    }}
    * {{
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      padding: 0;
      min-height: 100%;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 24%),
        radial-gradient(circle at top right, rgba(14, 165, 233, 0.05), transparent 22%),
        linear-gradient(180deg, #f8fafc, #f3f6fa 60%, #eef2f7);
      color: var(--text);
      font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Source Han Sans SC", "Microsoft YaHei", sans-serif;
    }}
    body {{
      overflow: hidden;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
      background-size: 40px 40px;
      mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.2), transparent 94%);
    }}
    .app {{
      width: min(1440px, calc(100vw - 32px));
      height: calc(100vh - 32px);
      margin: 16px auto;
      padding: 12px;
      border-radius: var(--radius-shell);
      border: 1px solid rgba(255, 255, 255, 0.7);
      background: rgba(255, 255, 255, 0.54);
      box-shadow: 0 28px 72px rgba(15, 23, 42, 0.08);
      backdrop-filter: blur(18px);
    }}
    .workspace {{
      display: grid;
      grid-template-columns: 436px minmax(0, 1fr);
      gap: 14px;
      height: 100%;
      min-height: 0;
    }}
    .panel {{
      min-height: 0;
      border: 1px solid var(--line);
      border-radius: var(--radius-panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    .panel-left {{
      background:
        linear-gradient(180deg, rgba(240, 246, 255, 0.94), rgba(248, 250, 252, 0.92) 34%, rgba(255, 255, 255, 0.9)),
        var(--surface);
    }}
    .panel-right {{
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 253, 249, 0.94)),
        var(--surface-strong);
    }}
    .panel-left,
    .panel-right {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      min-height: 0;
    }}
    .panel-header {{
      display: grid;
      gap: 6px;
      padding: 16px 20px 14px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.76), rgba(255, 255, 255, 0.54));
    }}
    .panel-header-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .eyebrow {{
      font-size: 0.78rem;
      color: var(--accent);
      letter-spacing: 0.08em;
      font-weight: 600;
    }}
    .panel-title {{
      margin: 0;
      font-size: 1rem;
      line-height: 1.4;
      font-weight: 700;
      color: var(--text);
    }}
    .panel-note {{
      margin: 0;
      font-size: 0.84rem;
      color: var(--text-soft);
    }}
    .left-scroll,
    .right-scroll {{
      min-height: 0;
      overflow: auto;
      padding: 18px 20px 20px;
      scrollbar-width: thin;
      scrollbar-color: rgba(148, 163, 184, 0.7) transparent;
    }}
    .left-scroll::-webkit-scrollbar,
    .right-scroll::-webkit-scrollbar {{
      width: 10px;
    }}
    .left-scroll::-webkit-scrollbar-thumb,
    .right-scroll::-webkit-scrollbar-thumb {{
      background: rgba(148, 163, 184, 0.45);
      border-radius: 999px;
      border: 2px solid transparent;
      background-clip: padding-box;
    }}
    .left-stack,
    .right-stack {{
      display: grid;
      align-content: start;
      gap: 20px;
      min-height: 0;
    }}
    .section {{
      display: grid;
      gap: 12px;
    }}
    .section-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .section-title {{
      margin: 0;
      font-size: 0.88rem;
      color: var(--text-soft);
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .capture-title {{
      margin: 0;
      font-size: 1.22rem;
      line-height: 1.52;
      font-weight: 700;
      letter-spacing: -0.01em;
    }}
    .media-stack {{
      display: grid;
      gap: 14px;
    }}
    .media-panel {{
      display: grid;
      gap: 10px;
      padding: 0;
    }}
    .media-label {{
      font-size: 0.78rem;
      color: var(--text-soft);
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .video-player,
    .audio-player {{
      width: 100%;
      display: block;
      border: 1px solid rgba(15, 23, 42, 0.1);
      background: #ffffff;
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.7),
        0 10px 24px rgba(15, 23, 42, 0.06);
    }}
    .video-player {{
      aspect-ratio: 16 / 9;
      object-fit: cover;
      border-radius: 18px;
    }}
    .audio-player {{
      border-radius: 999px;
    }}
    .meta-table {{
      display: grid;
      gap: 0;
      border: 1px solid var(--line);
      border-radius: var(--radius-inner);
      background: rgba(255, 255, 255, 0.74);
      overflow: hidden;
    }}
    .meta-row {{
      display: grid;
      grid-template-columns: 88px minmax(0, 1fr);
      gap: 16px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
    }}
    .meta-row:last-child {{
      border-bottom: none;
    }}
    .meta-label {{
      font-size: 0.82rem;
      color: var(--text-soft);
      font-weight: 600;
    }}
    .meta-value {{
      font-size: 0.96rem;
      line-height: 1.6;
      word-break: break-word;
      color: var(--text);
    }}
    .artifact-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: grid;
      gap: 0;
      border-top: 1px solid var(--line);
    }}
    .artifact-item {{
      display: grid;
      gap: 8px;
      padding: 14px 0;
      border-bottom: 1px solid var(--line);
      background: transparent;
      transition: transform 160ms ease;
    }}
    .artifact-item:hover {{
      transform: translateX(2px);
    }}
    .artifact-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}
    .artifact-name {{
      font-size: 0.84rem;
      color: var(--text-soft);
      font-weight: 700;
    }}
    .artifact-link {{
      color: var(--text);
      text-decoration: none;
      word-break: break-word;
      font-family: "SF Mono", "JetBrains Mono", "Cascadia Code", monospace;
      font-size: 0.86rem;
      line-height: 1.55;
    }}
    .artifact-link:hover {{
      color: var(--accent);
    }}
    .action-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}
    .action-chip {{
      appearance: none;
      border: 1px solid rgba(15, 23, 42, 0.1);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.88);
      color: var(--text);
      padding: 9px 14px;
      font-size: 0.86rem;
      line-height: 1;
      cursor: pointer;
      transition: transform 140ms ease, border-color 140ms ease, background 140ms ease, box-shadow 140ms ease;
      box-shadow: 0 1px 0 rgba(255, 255, 255, 0.7);
    }}
    .action-chip:hover {{
      transform: translateY(-1px);
      border-color: var(--line-strong);
      background: var(--accent-soft);
      box-shadow: var(--shadow-soft);
    }}
    .action-chip-small {{
      padding: 7px 11px;
      font-size: 0.78rem;
    }}
    .transcript-frame {{
      min-height: 0;
      background: transparent;
      overflow: visible;
    }}
    .transcript-body {{
      min-height: 100%;
      max-width: 58rem;
      margin: 0 auto;
      padding: 6px 14px 44px;
      font-size: 1rem;
      line-height: 1.92;
      color: var(--text);
      letter-spacing: 0.01em;
      word-break: break-word;
      text-wrap: pretty;
    }}
    .transcript-body p {{
      margin: 0 0 0.7em;
    }}
    .transcript-body p:last-child {{
      margin-bottom: 0;
    }}
    @media (max-width: 980px) {{
      body {{
        overflow: auto;
      }}
      .app {{
        width: min(100vw - 16px, 1440px);
        height: auto;
        margin: 8px auto;
        padding: 10px;
      }}
      .workspace {{
        grid-template-columns: 1fr;
        height: auto;
      }}
      .panel-left,
      .panel-right {{
        min-height: auto;
      }}
      .left-scroll,
      .right-scroll {{
        overflow: visible;
      }}
    }}
  </style>
</head>
<body>
  <main class="app">
    <section class="workspace">
      <aside class="panel panel-left">
        <header class="panel-header">
          <div class="eyebrow">内容工作台</div>
          <div class="panel-title">媒体与产物</div>
          <p class="panel-note">聚焦预览、元信息与文件定位。</p>
        </header>
        <div class="left-scroll">
          <div class="left-stack">
            <section class="section">
              <div class="section-head">
                <h2 class="section-title">媒体预览</h2>
              </div>
              <div class="media-stack">
                {''.join(media_sections)}
              </div>
            </section>

            <section class="section">
              <div>
                <h1 class="capture-title">{title}</h1>
              </div>
            </section>

            <section class="section">
              <div class="section-head">
                <h2 class="section-title">视频元数据</h2>
              </div>
              <div class="meta-table">
                <div class="meta-row">
                  <div class="meta-label">类型</div>
                  <div class="meta-value">{content_type}</div>
                </div>
                <div class="meta-row">
                  <div class="meta-label">作者</div>
                  <div class="meta-value">{author}</div>
                </div>
                <div class="meta-row">
                  <div class="meta-label">作品 ID</div>
                  <div class="meta-value">{aweme_id}</div>
                </div>
                <div class="meta-row">
                  <div class="meta-label">存储目录</div>
                  <div class="meta-value">{out_dir_html}</div>
                </div>
              </div>
            </section>

            <section class="section">
              <div class="section-head">
                <h2 class="section-title">产物路径</h2>
              </div>
              <ul class="artifact-list">
                {_artifact_rows(files)}
              </ul>
            </section>
          </div>
        </div>
      </aside>

      <section class="panel panel-right">
        <header class="panel-header">
          <div class="panel-header-row">
            <div>
              <div class="eyebrow">转写文稿</div>
              <div class="panel-title">文稿阅读与复制</div>
            </div>
            <div class="action-row">
              <button class="action-chip" type="button" data-copy="{transcript_copy}">复制全文</button>
              <button class="action-chip" type="button" data-copy="{out_dir_text}">复制目录</button>
            </div>
          </div>
          <p class="panel-note">本地生成，适合直接浏览、选取与复制。</p>
        </header>
        <div class="right-scroll">
          <div class="right-stack">
            <section class="transcript-frame">
              <div class="transcript-body">
                {transcript_html}
              </div>
            </section>
          </div>
        </div>
      </section>
    </section>
  </main>
  <script>
    const copyText = async (text) => {{
      if (!text) return;
      try {{
        await navigator.clipboard.writeText(text);
      }} catch (err) {{
        const area = document.createElement("textarea");
        area.value = text;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        area.remove();
      }}
    }};

    document.querySelectorAll("[data-copy]").forEach((button) => {{
      button.addEventListener("click", async () => {{
        const original = button.textContent;
        await copyText(button.getAttribute("data-copy") || "");
        button.textContent = "已复制";
        window.setTimeout(() => {{
          button.textContent = original;
        }}, 1200);
      }});
    }});
  </script>
</body>
</html>
"""

    report_path = out_dir / "index.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path

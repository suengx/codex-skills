# Supported URL formats

## Supported

| Format | Example |
|--------|---------|
| Short link | `https://v.douyin.com/xxxxx/` |
| Video page | `https://www.douyin.com/video/7640082170305090171` |
| Note (image) page | `https://www.douyin.com/note/7640701464617132402` |
| Share page | `https://www.iesdouyin.com/share/video/7640082170305090171/` |
| Full share text | `7.48 复制打开抖音… https://v.douyin.com/xxxxx/ …` |
| Jingxuan modal | `https://www.douyin.com/jingxuan?modal_id=7640082170305090171` |

The resolver normalizes `note`/`video`/`modal_id` URLs to `iesdouyin.com/share/...` before fetching SSR data.

## Not supported

- Logged-in-only or private content
- Live streams (`live.douyin.com`)
- User profile pages without a specific work ID
- DRM-protected streams

## Agent tip

If resolution fails, ask the user to re-copy the **share link from the Douyin app** (`v.douyin.com` short link is most reliable).

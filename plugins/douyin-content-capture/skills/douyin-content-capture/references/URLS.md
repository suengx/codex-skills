# 支持的链接形式

## 支持

| 形式 | 示例 |
|------|------|
| App 分享短链 | `https://v.douyin.com/xxxxx/` |
| 视频页面 | `https://www.douyin.com/video/7640082170305090171` |
| 图文页面 | `https://www.douyin.com/note/7640701464617132402` |
| 分享页 | `https://www.iesdouyin.com/share/video/7640082170305090171/` |
| 整段分享文案 | `7.48 复制打开抖音… https://v.douyin.com/xxxxx/ …` |
| 精选 modal 链接 | `https://www.douyin.com/jingxuan?modal_id=7640082170305090171` |

解析器会先把 `note` / `video` / `modal_id` 形式的链接统一规范化为 `iesdouyin.com/share/...`，然后再抓取 SSR 数据。

## 不支持

- 需要登录后才能访问的内容或私密内容
- 直播（`live.douyin.com`）
- 没有明确作品 ID 的用户主页
- 带 DRM 保护的流媒体内容

## Agent 提示

如果解析失败，优先让用户重新从抖音 App 里复制**分享链接**，其中 `v.douyin.com` 短链最稳定。

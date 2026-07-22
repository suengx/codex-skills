# codex-skills

这是 `suengx` 的技能源码仓库，用来统一维护跨平台能力、Codex 适配层与测试配置。

## 仓库定位

- 这里是**源码仓库**，适合统一开发、测试、版本管理。
- 这里**不是推荐的 Codex marketplace 安装入口**。
- 面向 Codex 的按需安装，会使用单技能单仓库的分发方式。

## 当前收录

- `plugins/douyin-content-capture/`
  - `python-package/`：可安装的通用 CLI 包
  - `skills/douyin-content-capture/`：Codex skill 适配层
  - `.codex-plugin/plugin.json`：Codex plugin 清单
- `plugins/init-matt-engineering-discipline/`
  - `skills/init-matt-engineering-discipline/`：仓库初始化脚手架 skill
  - `.codex-plugin/plugin.json`：Codex plugin 清单
  - 用途：安装 Matt Pocock skills，生成中文优先的 agent 协议、GitHub Issues/PR/CI/review/release 治理资产，并内置 worktree 协作纪律

## 安装 CLI

完整转写版：

```bash
python -m pip install "douyin-capture[transcribe] @ git+https://github.com/suengx/codex-skills.git@main#subdirectory=plugins/douyin-content-capture/python-package"
douyin-capture doctor --json
```

仅元数据解析版：

```bash
python -m pip install "douyin-capture @ git+https://github.com/suengx/codex-skills.git@main#subdirectory=plugins/douyin-content-capture/python-package"
```

## Codex 分发说明

Codex 的最佳实践是：

- 源码统一放在本仓库
- 每个技能单独一个分发仓库
- 用户先 `marketplace add` 单个技能仓库，再在 Codex 插件/市场界面按需安装或启用

这样可以避免“加一个市场就把整仓技能都暴露出来”的粗粒度安装体验。

对于纯 skill，也可以让 Codex 从本仓库的具体路径安装：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo suengx/codex-skills \
  --path plugins/init-matt-engineering-discipline/skills/init-matt-engineering-discipline
```

安装后，在下一轮对话中即可说：

```text
用 init-matt-engineering-discipline 初始化当前仓库。
```

当前独立分发仓库：

- `suengx/codex-plugin-douyin-content-capture`
- `suengx/codex-plugin-init-matt-engineering-discipline`

这些分发仓库的 marketplace 策略应保持为 `policy.installation: "AVAILABLE"`，
表示“添加市场后可选安装”，不要改回 `INSTALLED_BY_DEFAULT`。

这样 Codex marketplace 安装入口可以保持单插件粒度；本仓库继续作为源码、测试和同步上游。

## 设计原则

- 核心能力先做成稳定 CLI 或 package contract
- Codex 相关元数据只放在适配层
- 分发粒度按 plugin 控制，不按源码仓库控制
- 普通 skill 的 `SKILL.md` 保持短入口，详细 SOP 放到 `references/`，确定性操作放到 `scripts/`
- 消费型仓库只安装 runnable skill 到 `.agents/skills/`；只有技能创作仓库才维护 `skills/` 源码

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
- 用户按需 `marketplace add` 单个技能仓库

这样可以避免“加一个市场就把整仓技能都暴露出来”的粗粒度安装体验。

当前 `douyin-content-capture` 的独立分发仓库是：

- `suengx/codex-plugin-douyin-content-capture`

## 设计原则

- 核心能力先做成稳定 CLI 或 package contract
- Codex 相关元数据只放在适配层
- 分发粒度按 plugin 控制，不按源码仓库控制

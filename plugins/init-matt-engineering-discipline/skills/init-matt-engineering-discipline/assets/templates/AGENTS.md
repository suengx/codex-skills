# Agent Guide

## Agent skills

### Issue tracker

Issues and PRDs target GitHub Issues for this repo. Issue-writing skills must verify `git remote -v` and `gh auth status` before creating or editing issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the Matt Pocock triage vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

Use a single-context domain layout: root `CONTEXT.md` plus root `docs/adr/`. See `docs/agents/domain.md`.

### Local skills

Matt Pocock skills and project runtime skills are installed under `.agents/skills/`.

Only create `skills/<group>/<skill-name>/` when this repository itself authors and maintains a project-local skill. Product repositories should not keep scaffold source materials in `skills/` unless explicitly intended.

### Worktree / Codex task coordination

Use `worktree-agent-coordination` when an agent starts implementation, resumes stale work, detects `main` changed, prepares completion, commits, pushes, opens a PR, or integrates multiple branches/worktrees.

Codex task/workspace/worktree can provide execution isolation outside the repo's core assets. The repo still requires final convergence through GitHub Issue -> PR -> CI -> Review.

## 中文偏好协议

本仓库默认使用中文维护项目协作资产。除非用户明确要求英文，项目内可维护产物优先使用中文。

中文优先适用于：

- 需求文档、PRD、spec、issue、ticket、ADR、handoff、review 说明。
- prompt、agent 指令、项目自管 skill、工作流说明。
- 用户可见的业务概念解释、领域术语和决策记录。

保留原文适用于：

- 代码标识符、文件名、包名、命令、第三方 API、协议名。
- 英文报错、日志原文、外部文档标题、标准库或框架术语。
- 已有代码库约定中明确使用英文的领域名。

写作要求：

- 先用中文表达工程意图，再保留必要英文原词。
- 不做逐字翻译；以语义准确、团队可维护为准。
- 对业务领域概念，优先使用 `CONTEXT.md` 和已接受 ADR 中的项目术语；不确定时标注不确定性，不自行发明术语。

## 脚手架边界

本文件只定义通用工程纪律：Matt skills、中文优先、GitHub Issues/PR/CI/review/release、worktree/Codex task 协作。

具体业务领域、产品定位、行业术语、业务标签和专门 issue 模板由本仓库后续在 `README.md`、`CONTEXT.md`、`docs/adr/`、GitHub labels 或自管 skill 中维护。

## Matt Pocock skills 心智模型

这套 skills 是工程控制层：先对齐意图，再沉淀规格，再切成可执行单元，再用测试和 review 闭环约束实现。

常用链路：

```text
grill-me / grill-with-docs
-> to-spec
-> to-tickets
-> triage
-> implement
-> execution workspace / branch / worktree
-> PR
-> CI
-> code-review
-> merge
-> release
```

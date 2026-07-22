# Human-Agent GitHub Playbook

## Core model

```text
Issue = 意图资产
Label = 分类和状态语言
Milestone = 阶段目标
Project = 工作视图和调度面板
Execution Workspace / Branch / Worktree = 执行隔离
PR = 变更资产
Review = 治理记录
CI = 客观验证
Release / Tag = 发布边界
ADR / CONTEXT = 长期认知资产
```

本 playbook 是通用工程治理协议，不表达任何业务领域。业务模型、行业术语、产品定义和专门标签由目标仓库维护。

## Main workflow

```text
我有想法
→ grill-me / grill-with-docs
→ to-spec
→ to-tickets
→ triage
→ implement
→ execution workspace / branch / worktree
→ PR
→ CI
→ code-review
→ merge
→ release
→ ADR / CONTEXT 持续沉淀
```

## Issue roles

Issue 是多角色容器。它可以是 idea、spec、bug、decision、ticket、map 或 release task。

Ticket 不是 GitHub 的另一种实体，而是被设计成可执行切片的 issue。

## Execution workspace

执行空间可以由 Codex task、git branch 或 git worktree 承担。它解决“我在哪里干活”的问题，GitHub Issue 和 PR 解决“我为什么干、交付什么、如何审核”的问题。

当 agent 开始实现、恢复旧任务、发现 `main` 更新、准备交付、commit、push、开 PR 或合并多个执行空间时，使用 `worktree-agent-coordination`。它默认先检查事实，再决定是否需要同步 latest main、重新验证或规划 integration order。

## Skill layout

`.agents/skills/` 是运行时技能目录，agent 会从这里读取项目可用的技能。

`skills/` 只在本仓库自己要创作、维护或 fork 项目级 skill 时使用。普通产品仓库默认不保存脚手架 skill 的源码副本。

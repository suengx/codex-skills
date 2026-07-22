# Contributing

本仓库采用 GitHub 标准工程流。

## 工作流

1. 用 GitHub Issue 承载意图。
2. 用 labels 表达状态、类型、领域和优先级。
3. 只有信息完整、边界清楚、验收标准明确的 issue 才能标记 `ready-for-agent`。
4. 一个可执行 issue 对应一个 execution workspace、branch 或 worktree。
5. 通过 PR 汇总变更证据。
6. 合并前通过 CI 和 review。
7. 重要长期决策写入 `docs/adr/`，领域语言写入 `CONTEXT.md`。

## 执行隔离

Codex task、git branch 和 git worktree 都是执行隔离手段，不是最终交付边界。

开始实现、恢复旧任务、发现 `main` 更新、准备交付、commit、push、开 PR 或合并多分支前，使用 `worktree-agent-coordination` 检查当前执行空间、主线差异、未提交变更和验证状态。

## Branch 命名

```text
codex/<issue-number>-short-name
human/<issue-number>-short-name
fix/<issue-number>-short-name
```

## PR 要求

- PR body 必须链接 issue，例如 `Closes #123`。
- PR 必须说明验证结果。
- PR 必须说明当前 branch/worktree 是否已纳入 latest main，以及未验证项。
- 重要变更需要 `code-review`。

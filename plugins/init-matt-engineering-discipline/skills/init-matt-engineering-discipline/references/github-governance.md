# GitHub Governance Reference

Use GitHub as the engineering asset system for human-agent collaboration.

This reference is domain-neutral. It defines repository governance entities, not product or business-domain facts.

## Entity model

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

## Issue roles

Issue is a multi-role container:

- idea issue
- spec issue
- bug issue
- decision issue
- ticket issue
- map issue
- release task

Ticket is not a separate GitHub entity. A ticket is an issue shaped as an executable slice.

Common flow:

```text
small work: one issue -> implement
medium work: spec issue -> ticket issues -> implement one by one
huge unclear work: wayfinder map issue -> decision issues -> spec/tickets
```

## Label sets

Triage labels:

- `needs-triage`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`
- `wontfix`

Type labels:

- `type:bug`
- `type:feature`
- `type:spec`
- `type:task`
- `type:decision`
- `type:refactor`
- `type:docs`
- `type:chore`

Area labels:

- `area:product`
- `area:frontend`
- `area:backend`
- `area:api`
- `area:data`
- `area:infra`
- `area:docs`

Priority labels:

- `priority:p0`
- `priority:p1`
- `priority:p2`
- `priority:p3`

Size/risk labels:

- `size:xs`
- `size:s`
- `size:m`
- `size:l`
- `risk:high`
- `blocked`

Use one triage state and one main type per issue. Multiple areas are allowed. Apply `ready-for-agent` only when scope, acceptance criteria, and validation are clear.

Add domain-specific area labels only inside the target repository after its domain model is clear. Do not bake business terms into the scaffold.

## Recommended GitHub workflow

```text
idea
-> grill-me / grill-with-docs
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
-> ADR / CONTEXT
```

## Recommended repository shape

```text
/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── CODEOWNERS
├── CONTEXT.md
├── docs/
│   ├── agents/
│   └── adr/
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── pull_request_template.md
    └── workflows/
```

## Execution workspace discipline

Execution workspace is the runtime side of GitHub governance. It may be a Codex task workspace, a git branch, a git worktree, or a combination of these.

Use `worktree-agent-coordination` to keep runtime isolation convergent:

- before starting implementation, confirm repo, branch/worktree, dirty state, and `origin/main` reachability
- when resuming stale work, check whether `main` advanced
- before delivery, fetch latest main, report branch/head/main delta, and rerun project validation
- when several branches/worktrees are ready, produce an integration plan instead of mixing them directly

## Runtime skill layout

For ordinary product repositories, runnable skills live in `.agents/skills/`. Do not copy scaffold authoring material into `skills/` by default.

Use `skills/<group>/<skill-name>/` only when the target repository is intentionally maintaining project-local skill source. In that case, the runnable projection still belongs in `.agents/skills/<skill-name>/`.

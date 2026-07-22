# Issue tracker: GitHub Issues

本仓库的 issue、PRD、spec 和 ticket 目标落点是 GitHub Issues。

## 操作前检查

- `git remote -v` 必须指向目标 GitHub 仓库。
- `gh auth status` 必须通过。
- 如果 remote 或认证缺失，停止写入并报告缺失项。

## Skill 语义映射

- 当 skill 要求“publish to the issue tracker”时，创建 GitHub issue。
- 当 skill 要求“fetch the relevant ticket”时，运行 `gh issue view <number> --comments`。
- 当 skill 要求应用 triage role 时，使用 `docs/agents/triage-labels.md` 中的标签映射。

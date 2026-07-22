# Delivery Report

在 `finish` / `pre-delivery` 后，输出必须短但完整。

## 模板

```markdown
**执行空间**
- Repo:
- Branch:
- Worktree:
- HEAD:
- Base / latest main:

**主线同步**
- 已执行 `git fetch`:
- `origin/main` 是否领先当前分支:
- 当前分支领先 `origin/main` 的 commits:
- 是否已 rebase/merge latest main:

**工作区**
- Dirty state:
- Merge/rebase/cherry-pick state:

**验证**
- lint:
- typecheck:
- test:
- build:
- 未验证项:

**交付**
- Commit:
- Push:
- PR:
- 下一步:
```

## 判断规则

- 如果落后 `origin/main`，不能说“已完成”，只能说“本地实现完成，尚未纳入最新 main”。
- 如果未跑测试，不能说“验证通过”。
- 如果工作区有未提交变更，不能说“已提交完成”。
- 如果没有 push/PR，不能说“已交付到 GitHub”。
- 如果 CI 未跑，说明“本地验证通过，CI 未验证”。

## 验证发现

按项目发现命令：

- Node: `package.json` 中的 `lint`、`typecheck`、`test`、`build`。
- Python: `pytest`、`python -m compileall`、项目文档中声明的命令。
- 其他项目：读取 README、CONTRIBUTING、AGENTS、CI workflow。

没有发现命令时，报告未发现，不要补造。

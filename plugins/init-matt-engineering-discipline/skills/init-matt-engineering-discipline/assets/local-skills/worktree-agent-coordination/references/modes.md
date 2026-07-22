# Worktree Coordination Modes

## 模式分类

```text
可主动呼叫的模式
静默触发的模式
被其他模式调用的子模式
```

## 主动模式

### status

用户说：

- “看下当前 worktree 状态”
- “我现在在哪个分支”
- “这个任务和 main 差多少”

目标：只读检查当前执行空间，不改任何状态。

调用：

```bash
python3 scripts/worktree_guard.py status
```

### sync-main

用户说：

- “main 有更新，纳入一下”
- “别的 worktree 已经合并了，重新同步”
- “继续前先跟 main 对齐”

目标：检查 main 前进情况，必要时在授权后 rebase/merge。

默认先执行 `sync-check`，再决定是否同步。

### finish

用户说：

- “这个 worktree 收尾”
- “做好了吗”
- “准备 commit/push/PR”

目标：完成前门禁，确认 latest main、验证结果、交付证据。

### integrate

用户说：

- “几个 worktree 都完成了，帮我排合并路径”
- “多个 agent 的分支怎么收敛”

目标：规划多 branch/worktree 的合并顺序、冲突风险和验证策略。

### recover

用户说：

- “这个 worktree 状态有点乱”
- “我好像切错分支了”
- “rebase/merge 卡住了”

目标：保护当前事实，再决定恢复路径。

## 静默模式

### fresh-start

触发：

- 准备实现 issue/spec。
- 准备修 bug。
- 准备重构。
- 新 Codex task 进入 repo。

目标：避免 agent 在错误目录、错误分支、脏工作区或旧 main 上开工。

### resume-stale-work

触发：

- 继续旧 task。
- 回到旧 worktree。
- 当前 branch 已有本地 commits。
- 距离上次工作已经过了一段时间。

目标：避免在旧 main 上继续扩大 diff。

### main-advanced

触发：

- `origin/main` 比当前分支多 commits。
- 用户提醒别的 worktree 已经合并。

目标：把“主线已经变化”显性化，并要求组合状态验证。

### pre-delivery

触发：

- 准备说“完成”。
- 准备 commit。
- 准备 push。
- 准备 open PR。
- 准备 merge。

目标：防止旧基线、未验证、未 push、未说明风险的交付。

### dirty-worktree-guard

触发：

- `git status --short` 非空。
- detached HEAD。
- merge/rebase/cherry-pick 进行中。
- 当前在 `main` 上有改动。

目标：保护未提交变更和当前用户状态。

## 子模式关系

```text
fresh-start
  -> sync-check

resume-stale-work
  -> sync-check
  -> main-advanced? 

main-advanced
  -> sync-main
  -> validate-after-sync

pre-delivery
  -> sync-check
  -> validate-after-sync
  -> delivery-report

dirty-worktree-guard
  -> protect-dirty-state

integrate
  -> status for each worktree
  -> integration-plan
  -> validate-after-sync
```

## 默认完成门槛

不能宣称完成，除非知道：

- 当前 branch/worktree。
- 当前 HEAD。
- `origin/main` 是否已检查。
- 当前分支是否落后 main。
- 本分支有哪些 commits。
- 工作区是否干净。
- 验证命令和结果。
- push/PR 状态。

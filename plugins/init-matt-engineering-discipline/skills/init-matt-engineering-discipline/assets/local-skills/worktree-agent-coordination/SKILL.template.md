---
name: worktree-agent-coordination
description: 协调 git branch/worktree/Codex task 中的多 agent 执行隔离和主线收敛。Use when an agent starts implementation, resumes stale work, detects main changed, works in a git worktree or branch, prepares to report completion, commit, push, open a PR, or integrate multiple agent branches/worktrees. Provides silent guards, active modes, SOPs, and scripts for status, sync, finish, recover, and integration.
---

# Worktree Agent Coordination

在多 Codex task、多 git worktree、多 branch 并行时，确保隔离工作最终能收敛到最新 `main`，并用验证结果证明组合状态可交付。

核心纪律：

```text
Worktree 是隔离，不是分裂。
隔离工作最终必须重新收敛到最新 main，并用测试证明组合状态可用。
```

## 先识别模式

遇到 branch/worktree/Codex task 相关工作时，先判断当前属于哪个模式，再执行对应 SOP。

### 静默模式

这些模式应该在相关动作前自动触发，不需要用户每次提醒：

- `fresh-start`：准备开始实现、修 bug、重构、处理 issue。
- `resume-stale-work`：继续一个已有 worktree/branch/task。
- `main-advanced`：发现 `origin/main` 比当前工作基线更新。
- `pre-delivery`：准备说完成、commit、push、开 PR、交付总结。
- `dirty-worktree-guard`：检测到未提交变更、detached HEAD、在 main 上直接开发或状态不清。

### 主动模式

用户明确要求时进入：

- `status`：只读查看当前执行空间。
- `sync-main`：纳入 latest main。
- `finish`：收尾当前 worktree/branch。
- `integrate`：多个 worktree/branch 完成后规划收敛路径。
- `recover`：工作区状态混乱时先保护和梳理。

### 子模式

这些由其他模式调用，通常不作为用户入口：

- `sync-check`
- `validate-after-sync`
- `delivery-report`
- `protect-dirty-state`
- `integration-plan`

详细模式见 `references/modes.md`。当不确定模式或需要解释触发关系时读取它。

## 使用脚本采集事实

优先用脚本采集 git 状态，而不是手写一堆命令：

```bash
python3 /path/to/worktree-agent-coordination/scripts/worktree_guard.py status
python3 /path/to/worktree-agent-coordination/scripts/worktree_guard.py start
python3 /path/to/worktree-agent-coordination/scripts/worktree_guard.py sync-check
python3 /path/to/worktree-agent-coordination/scripts/worktree_guard.py finish
python3 /path/to/worktree-agent-coordination/scripts/worktree_guard.py list-worktrees
```

脚本默认只读，除非传入明确的写入参数。它可以自动 `git fetch`，因为这是低风险事实采集。

## SOP

### fresh-start

触发：用户让你实现 issue、修 bug、重构、开始新功能，或一个 Codex task 刚开始进入仓库。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py start
```

必须确认：

- 当前路径是预期 repo。
- 当前 branch/worktree 清楚。
- 当前不在脏状态中冒进。
- 如果在 `main` 上直接开发，要提示风险。
- `origin/main` 是否可达，当前是否落后。
- 是否有明确 issue/spec 或用户给出的目标。

完成标准：能判断当前是否可以开始，或者明确说明开始前必须先处理什么。

### resume-stale-work

触发：继续旧 worktree、旧 branch、旧 Codex task，或任务跨越较长时间。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py sync-check
```

必须确认：

- 本分支相对 `origin/main` 多了哪些 commits。
- `origin/main` 相对本分支多了哪些 commits。
- 是否需要同步 latest main 后继续。
- 是否有未提交变更阻止 rebase/merge。

完成标准：不能在不知道主线是否前进的情况下继续写代码。

### main-advanced / sync-main

触发：用户说“main 有更新”“别的 worktree 已合并”“纳入最新 main”，或脚本发现当前分支落后。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py sync-check
```

默认只检查并报告。是否执行 `rebase origin/main` 或 `merge origin/main` 取决于 repo 策略和用户授权。没有明确策略时，建议 rebase，但不要在脏工作区或会产生冲突时自动推进。

完成标准：同步动作后必须重新验证；没有验证不能报告“完成”。

### pre-delivery / finish

触发：准备说“完成”、commit、push、开 PR、merge、交付总结，或用户问“做好了吗”。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py finish
```

必须确认：

- 是否已 fetch latest `origin/main`。
- 当前是否落后 main。
- 当前是否有未提交变更。
- 本分支是否有要交付的 commits。
- 是否跑过项目验证。
- 是否已 push / PR，或下一步是什么。

完成标准：如果当前分支落后 `origin/main`，或者未在组合状态下验证，不能无条件宣称完成。按 `references/delivery-report.md` 输出交付报告。

### dirty-worktree-guard / recover

触发：工作区有未提交变更、detached HEAD、切错分支、冲突中、rebase/merge 中、状态不清。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py status
```

默认先保护事实，不做破坏性动作。不得静默执行 `reset --hard`、`clean`、强推、删除分支或覆盖用户未提交修改。

完成标准：说明当前风险、保护选项和建议下一步。

### integrate

触发：多个 worktree/branch 都有成果，需要决定合并顺序或收敛路径。

执行：

```bash
python3 /path/to/scripts/worktree_guard.py list-worktrees
```

再读取 `references/integration.md`。

完成标准：输出 integration plan，而不是直接把多个分支混合进 main。

## 验证纪律

默认验证顺序：

```text
lint -> typecheck -> test -> build
```

如果项目没有这些命令，报告“未发现对应命令”，不要假装跑过。验证规则见 `references/delivery-report.md`。

## 安全规则

- 自动检查可以做；改历史、解决冲突、push、merge 需要明确授权或已在用户请求中包含。
- 未提交变更存在时，不要 rebase/merge/switch branch，除非先保护变更并说明风险。
- 在 `main` 上直接开发时，不要扩大改动；优先建议切 branch/worktree。
- 完成前必须检查 latest main。
- 完成报告必须包含 branch、HEAD、main 差异、验证结果和未验证项。

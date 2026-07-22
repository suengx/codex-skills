# Multi-Worktree Integration

`integrate` 是主动模式，适合多个 branch/worktree/agent 都有成果，需要收敛到 main 的情况。

## 不变量

- main 是收敛目标。
- 每个分支先独立同步 latest main。
- 先合低风险、低依赖分支。
- 冲突风险高的分支单独处理。
- 每次合并后都运行验证。
- 不把多个未知状态一次性混进 main。

## 集成计划

输出 integration plan：

```markdown
## 分支清单

| Branch | Worktree | Ahead | Behind | Dirty | Issue/PR | Risk |
| --- | --- | --- | --- | --- | --- | --- |

## 建议顺序

1.
2.
3.

## 冲突风险

## 验证计划

## 需要用户确认的动作
```

## 默认策略

- 优先让每个分支各自开 PR，让 GitHub CI 和 review 承担合并门禁。
- 如果用户要求本地集成，先创建 integration branch，不直接在 main 上混合多个分支。
- 合并失败或测试失败时停止，报告阻塞。

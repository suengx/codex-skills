# Project Context

本仓库使用 Matt Pocock skills、中文优先项目资产和 GitHub 标准工程流程来支持人类 + agent 协作。

本文件初始只记录通用协作语境。产品定位、业务术语、行业规则和长期架构决策应由目标仓库在真实讨论后逐步补充。

## Language

**中文偏好**：
项目内可维护产物默认使用中文，包括文档、prompt、issue、spec、ticket、ADR、handoff、review 说明和项目自管 skill。代码标识符、命令、第三方 API、英文报错和外部协议名按工程惯例保留原文。
_Avoid_: 全量翻译、机械翻译

**Agent skills**：
一组约束 agent 工作流程的本地指令。它们控制澄清、规格化、拆票、实现、测试、诊断、review 和架构改进，不是一次性代码模板。
_Avoid_: 代码模板、万能 prompt

**Issue tracker**：
承载 issue、PRD、spec 和 ticket 的系统。本仓库目标使用 GitHub Issues。
_Avoid_: backlog backend、任务仓库

## Relationships

- `AGENTS.md` 是 agent 进入本仓库时的工作入口。
- `docs/agents/*` 保存 agent 工作流协议。
- `CONTEXT.md` 保存长期领域语言。
- `.agents/skills/*` 是 Codex 可发现的 runnable skill 目录。

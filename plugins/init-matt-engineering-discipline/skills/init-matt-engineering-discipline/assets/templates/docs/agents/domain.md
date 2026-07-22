# Domain Docs

本仓库采用 single-context domain docs 布局。

脚手架只提供领域文档的位置和维护规则，不预置业务领域。产品定义、行业术语、客户场景和业务规则必须由目标仓库自己补充。

## 开始工作前读取

- 根目录 `CONTEXT.md`
- 根目录 `docs/adr/` 中与当前任务相关的 ADR
- `docs/agents/` 中与 agent 工作流相关的协议

如果某个文件不存在，静默继续。只有当术语或决策已经被澄清时，才补充领域文档。

## 使用项目语言

当输出 issue 标题、spec、测试说明、review 结论或重构建议时，使用 `CONTEXT.md` 中定义的术语。不要随意换同义词。

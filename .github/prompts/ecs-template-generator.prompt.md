---
name: ecs-template-generator
description: "Generate a reusable ECS module template for this project. Automatically create component and system modules based on the requested feature."
---

你现在要基于当前仓库已有的 ECS 约定生成一个通用模板。请按以下要求输出：

1. 根据功能描述推断所需组件（Component）和系统（System）。
2. 生成每个组件的完整 Python 文件代码，使用 `@dataclass`，不包含业务逻辑。
3. 生成系统模块完整 Python 文件代码，继承 `core.system.System`，在 `_update` 中使用 `world.get_components(...)` 或 `world.get_entities_with(...)` 执行批量处理。
4. 给出建议的文件路径、文件名和模块目录结构。
5. 提供系统自动注册模式或注册 helper 的建议。
6. 提供设计说明、核心数据流和扩展点。

请始终遵循以下项目约定：
- Component 纯数据，命名如 `PositionComponent`、`HungerComponent`
- System 只在 `_update` 中执行逻辑，并通过查询组件池批量处理实体
- 不要把业务逻辑写进 Component
- 不要改变 `World` 的核心接口设计

示例输入：
- "创建一个用于实体移动的 ECS 模块"
- "实现一个饥饿消耗与恢复系统"
- "生成一个通用的社会关系系统模板"

输出格式要求：
- 先列出模块目录结构、模块路径和文件名
- 再显示每个文件的完整代码
- 如需自动注册系统，则给出注册 helper 或 `__init__.py` 示例
- 最后给出设计说明、数据流和扩展点

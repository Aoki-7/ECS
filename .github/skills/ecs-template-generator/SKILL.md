---
name: ecs-template-generator
description: "Use when you need to generate generic ECS module templates from existing project code. Creates Component dataclasses and System skeletons automatically based on feature requirements."
---

## ECS Template Generator Skill

该技能专注于根据当前仓库已有 ECS 模块风格，生成通用 ECS 模板。

### 适用场景

- 从需求描述自动识别所需组件和系统
- 生成符合项目约定的 Component dataclass 模块
- 生成符合项目约定的 System skeleton 模块
- 生成模块化、可扩展、低耦合的 ECS 结构
- 生成可直接插入到现有 `core/`、`human/`、`environment/` 等模块中的代码

### 输出要求

- 生成代码时应遵循当前仓库的 ECS 约定：
  - `Component` 仅为 dataclass 数据
  - `System` 负责批量查询并操作组件
  - `World` 提供 `get_components` / `get_entities_with` 查询接口
- 必须给出完整文件名和所在路径
- 必须给出建议的模块目录结构和 `__init__.py` 组织方式
- 必须展示系统自动注册模式或注册 helper
- 必须返回可运行的 Python 代码片段
- 必须附带简要设计说明和扩展点

### 生成策略

1. 根据功能需求拆解实体行为，确定最少必要组件
2. 使用 `dataclass` 定义组件字段，避免逻辑嵌入组件
3. 生成一个系统类，使用 `world.get_components(...)` 或 `world.get_entities_with(...)` 执行批量处理
4. 提供默认 `update(self, world, dt)` 调度逻辑和 `_update` 内部实现结构
6. 设计模块目录结构，如：
  - `human/components/xxx_component.py`
  - `human/systems/xxx_system.py`
  - `human/systems/__init__.py`
  - `human/components/__init__.py`
7. 生成自动注册方案：
  - `system_registry.py` 或 `human/systems/__init__.py` 维护系统列表
  - 说明如何在 `World` 初始化时批量注册系统

### 说明

此技能不是直接写死单个功能，而是根据需求自动生成通用 ECS 模块模板，便于后续扩展与复用。
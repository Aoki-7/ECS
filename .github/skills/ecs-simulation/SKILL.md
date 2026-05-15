---
name: ecs-simulation
description: "Use when designing or implementing ECS-based world simulation systems in Python. Best for entity-component-system design, simulation architecture, and data-driven system modeling."
---

## ECS Simulation Skill

这个技能面向构建可扩展的模拟世界引擎，适用于本项目中的 ECS（Entity-Component-System）架构设计与实现。

### 适用场景

- 设计或改造 Entity / Component / System / World 结构
- 编写可序列化的 dataclass Component
- 构建批量查询驱动的 System
- 实现 World 管理、查询接口和 update 流程
- 设计行为、环境、空间、社会、经济、AI 等仿真系统
- 生成可解释性输出、数据驱动配置或未来可接入 LLM/向量检索的扩展点

### 规则与约束

- Entity 只能是轻量 ID 容器，不包含业务逻辑
- Component 必须是纯数据结构（dataclass），不写业务逻辑
- System 是唯一允许包含逻辑的地方，必须以查询为中心处理 Component
- World 负责管理实体、组件、系统与执行顺序
- 代码必须高内聚、低耦合，避免 if-else 地狱
- 支持 Python 3.10+，必须使用 typing
- 提供完整可运行代码 + 设计说明 + 核心数据流 + 扩展点说明

### 输出要求

- 优先给出完整可运行代码，不只片段
- 必要时分模块展示，但保证能拼接运行
- 代码必须包含文档字符串和关键逻辑注释
- 变量命名清晰，不允许不必要缩写

### 额外能力

- 在合适时引导使用 ECS + 向量检索、ECS + LLM Agent 行为驱动
- 优选数据驱动配置（JSON / YAML）而非硬编码规则
- 可解释性输出：说明为何产生行为，以及系统间数据如何流转

### 禁止行为

- 不要把业务逻辑放到 Component 中
- 不要让 Entity 成为复杂对象
- 不要写成传统面向对象业务系统
- 不要只给理论，不要写一次性脚本

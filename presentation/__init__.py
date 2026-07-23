#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化层 — 仪表盘、实时图表、HTML 导出

目录结构:
    presentation/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── human_panel.py           # HumanStatePanel: 终端可视化面板 (实时展示人类状态)
    ├── human_observation_system.py  # HumanObservationSystem: 观察系统 (定期收集关键实体状态)
    ├── human_observation_component.py # HumanObservationComponent: 标记需要被观察的实体
    ├── world_simulation_dashboard.py # WorldSimulationDashboard: 世界模拟仪表盘 (WebSocket + Canvas)
    ├── chart_generator.py       # ChartGenerator: 图表生成 (matplotlib/实时折线图/柱状图)
    ├── event_log_panel.py       # EventLogPanel: 事件日志面板 (实时事件流)
    ├── performance_monitor.py   # PerformanceMonitor: 性能监控 (FPS/内存/CPU)
    └── tests/                   # 可视化测试包 (9 测试)

核心职责:
    1. 终端可视化面板:
       - HumanStatePanel: 实时展示单个人类的完整状态
       - 显示内容: 生理(饥饿/口渴/精力)/认知(情绪/目标/计划)/社交(关系/部落)/库存
       - 使用 rich 库实现彩色表格和进度条
       - 支持键盘交互 (切换显示模式/选择实体)

    2. 观察系统:
       - HumanObservationSystem: 定期收集并输出关键实体状态
       - 观察频率: 可配置 (每 tick/每 10 tick/每 100 tick)
       - 观察范围: 可配置 (全部/特定类别/特定区域)
       - 输出格式: 结构化数据 (JSON/CSV/HTML)

    3. 世界模拟仪表盘:
       - WorldSimulationDashboard: WebSocket 后端 + Canvas 前端
       - 实时数据流: 世界状态通过 WebSocket 推送到前端
       - 可视化组件: 折线图(人口/资源)/热力图(空间分布)/网络图(社交关系)
       - 交互功能: 缩放/平移/选择实体/时间轴控制

    4. 图表生成:
       - ChartGenerator: 基于 matplotlib 的静态图表生成
       - 支持折线图(趋势)/柱状图(对比)/饼图(占比)/热力图(空间)
       - 支持导出 PNG/SVG/PDF

    5. 事件日志:
       - EventLogPanel: 实时事件流展示
       - 事件过滤: 按类别/实体/时间范围过滤
       - 事件搜索: 关键词搜索历史事件
       - 导出功能: 导出为日志文件

    6. 性能监控:
       - PerformanceMonitor: 实时性能指标
       - 指标: FPS/内存使用/CPU 占用/系统执行时间
       - 告警: 性能下降时自动告警
       - 历史: 性能历史记录与趋势分析

与其他模块的关系:
    - core/: 依赖 ECS 框架 (读取 Entity/Component 数据)
    - application/: 从 SimulationLoop 获取世界状态
    - human/: 读取人类组件数据 (生理/认知/社交/库存)
    - animal/: 读取动物组件数据 (位置/状态/行为)
    - plant/: 读取植物组件数据 (位置/生长/产量)
    - environment/: 读取环境数据 (温度/光照/天气/地形)
    - civilization/: 读取文明数据 (科技/人口/建筑/贸易)
    - memory_layer/: 读取记忆数据 (概念/记忆/联想)
    - 所有模块: presentation/ 是只读观察层，可访问任何下层数据

设计原则:
    - 只读观察: 不修改任何组件数据，纯读取展示
    - 单向依赖: 可访问下层数据，但不被下层依赖
    - 可配置: 显示内容/频率/格式均可配置
    - 可扩展: 支持添加新的可视化组件
    - 低开销: 观察不影响模拟性能，支持后台渲染

版本: v4.0
"""

from .human_panel import HumanStatePanel
from .human_observation_system import HumanObservationSystem
from .human_observation_component import HumanObservationComponent

__all__ = [
    "HumanStatePanel",
    "HumanObservationSystem",
    "HumanObservationComponent",
]
"""
可视化层 — 仪表盘、实时图表、HTML 导出

职责：
    - 实时可视化仪表盘
    - WebSocket 后端 + Canvas 前端
    - 世界状态图表、事件日志、性能监控

依赖：
    - core/
    - application/

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化与观察系统模块 — 人机交互界面

职责：
    - HumanStatePanel: 终端可视化面板，实时展示人类状态、环境、库存等信息
    - HumanObservationSystem: 观察系统，定期收集并输出关键实体状态
    - HumanObservationComponent: 标记需要被观察的实体

使用场景：
    - 开发调试：实时观察单个人类的生理、认知、社交状态
    - 演示展示：以表格形式输出世界摘要
    - 数据导出：为外部可视化工具提供结构化数据

设计原则：
    - 本层是只读观察层，不修改任何组件数据
    - 允许访问任何下层模块的数据，但不被下层模块依赖
"""

from .human_panel import HumanStatePanel
from .human_observation_system import HumanObservationSystem
from .human_observation_component import HumanObservationComponent

__all__ = [
    "HumanStatePanel",
    "HumanObservationSystem",
    "HumanObservationComponent",
]


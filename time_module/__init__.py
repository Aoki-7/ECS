#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间系统 — 时间推进、调度器、事件触发

目录结构:
    time_module/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── time_component.py        # TimeComponent: 时间状态 (当前时间/时间流速/暂停状态)
    ├── time_scheduler.py        # TimeScheduler: 最小堆调度器 (一次性/周期性/条件性事件)
    ├── time_system.py           # TimeSystem: 时间推进系统 (驱动调度器执行)
    └── tests/                   # 时间测试包

核心职责:
    1. 时间状态管理:
       - TimeComponent: 存储当前时间、时间流速、暂停状态
       - 支持时间缩放 (加速/减速/暂停)
       - 支持时间单位转换 (tick → 秒 → 分 → 时 → 天)

    2. 事件调度:
       - TimeScheduler: 基于最小堆的事件调度器
       - 一次性事件: 指定时间触发，触发后移除
       - 周期性事件: 指定间隔循环触发
       - 条件性事件: 满足条件时触发
       - 优先级支持: 同时间事件按优先级排序

    3. 时间推进:
       - TimeSystem: 每 tick 推进时间，触发到期事件
       - 支持固定步长 (fixed timestep) 和可变步长
       - 支持时间回溯 (用于存档加载)

    4. 跨系统时间服务:
       - 为所有需要时间感知的系统提供统一时间源
       - 支持系统间时间同步 (所有系统使用同一时间)
       - 支持时间戳生成 (用于事件记录/日志)

与其他模块的关系:
    - core/: 依赖 ECS 框架 (Entity/Component/System/World)
    - environment/: 时间驱动季节变化 (SeasonSystem) 和气候趋势 (ClimateSystem)
    - biology/: 时间驱动生长 (GrowthSystem) 和衰老 (AgingSystem)
    - human/: 时间驱动生理需求 (PhysiologyNeedsSystem) 和行动计划 (ActionSystem)
    - animal/: 时间驱动迁徙 (MigrationSystem) 和繁殖周期 (ReproductionSystem)
    - plant/: 时间驱动光合作用 (PhotosynthesisSystem) 和种子传播 (SeedDispersalSystem)
    - space/: 时间驱动移动执行 (MovementSystem)
    - 几乎所有模块: 任何需要时间推进的系统都依赖 time_module/

设计原则:
    - 统一时间源: 所有系统使用同一时间，避免时间不一致
    - 最小堆调度: O(log n) 事件插入/删除，O(1) 获取最近事件
    - 时间缩放: 支持加速/减速/暂停，不改变事件逻辑
    - 可回溯: 支持时间回溯到任意历史点 (用于存档加载)

版本: v4.0
"""

from .time_component import TimeComponent
from .time_scheduler import TimeScheduler

__all__ = ["TimeComponent", "TimeScheduler"]
"""
human/systems/core 子模块

依赖:
    - human/
    - core/
    - biology/
    - space/
    - environment/
    - memory_layer/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类核心系统包 — 行为流水线的中枢

包含：
    - ActionSystem  : 行动调度器（管理 ActionQueue，出队、进度检查、中断恢复）
    - PlanningSystem: 规划器（将 Intent 分解为原子 Action 序列）
    - IntentSystem  : 意图生成（根据 Needs 和 Goals 生成当前最高优先级意图）

数据流：
    IntentSystem → PlanningSystem → ActionSystem → action/ 下各执行系统
"""



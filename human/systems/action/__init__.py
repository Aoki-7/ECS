"""
行动包 — 搜索、移动、进食、采集、建造

依赖：
    - human.systems/
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为系统子模块 — 人类具体动作的执行

职责：
    - 实现 PlanningSystem 生成的原子动作
    - 每个系统处理一种具体交互：移动、进食、饮水、拾取、搜索、社交、战斗、采集

包含：
    - MovementSystem  : 移动执行（路径跟随、速度计算、碰撞检测）
    - EatSystem       : 进食执行（从背包或地面消耗食物，恢复饥饿值）
    - DrinkSystem     : 饮水执行（从水源获取水分）
    - SleepSystem     : 睡眠执行（恢复精力，受环境安全度影响）
    - PickupSystem    : 拾取执行（将地面物品加入背包）
    - SearchSystem    : 搜索执行（扫描视野范围内的目标类型）
    - SocializeSystem : 社交执行（与其他人类进行对话/交易/结盟）
    - CombatSystem    : 战斗执行（攻击、防御、逃跑判定）
    - HarvestSystem   : 采集执行（从植物/矿点获取资源）

与 core/ 的交互：
    - 通过 World.get_components() 查询目标实体
    - 通过 SpaceSystem.query_radius() 进行空间搜索
    - 通过 add_component/remove_component 修改实体状态
"""

from .pickup_system import PickupSystem
from .eat_system import EatSystem
from .search_system import SearchSystem

__all__ = [
    'PickupSystem',
    'EatSystem',
    'SearchSystem',
]


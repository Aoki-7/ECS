#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:人类系统包初始化文件
@时间:2026/03/13 13:42:02
@作者:Sherry
@版本:1.0
'''

"""
    Human包含的系统说明，按类别组织

    === 核心系统 (Core Systems) ===
    ActionSystem: 行动系统 - 管理实体的行动队列和执行
    PlanningSystem: 规划系统 - 将意图转换为行动序列
    IntentSystem: 意图系统 - 根据需求生成实体的意图

    === 生理系统 (Physiological Systems) ===
    HungerSystem: 饥饿系统 - 管理饥饿值变化
    ThirstSystem: 口渴系统 - 管理口渴值变化
    EnergySystem: 精力系统 - 管理精力值变化
    ComfortSystem: 舒适度系统 - 管理舒适度和疲劳环境耦合
    SocialNeedSystem: 社交需求系统 - 管理社交需求衰减
    HealthSystem: 健康系统 - 管理实体的健康状态

    === 认知系统 (Cognitive Systems) ===
    DecisionSystem: 决策系统 - 处理实体的决策逻辑
    GoalSystem: 目标系统 - 管理实体的长期目标
    PerceptionSystem: 感知系统 - 处理实体的环境感知

    === 社交系统 (Social Systems) ===
    SocialSystem: 社交系统 - 管理实体的社交状态
    PairingSystem: 配对系统 - 处理实体的配对逻辑
    ReproductionSystem: 繁衍系统 - 处理实体的繁衍逻辑

    === 身份系统 (Identity Systems) ===
    IdentitySystem: 身份系统 - 管理实体的身份信息
    BiologySystem: 生物系统 - 处理实体的生物学特征

    === 生存系统 (Survival Systems) ===
    SeekFoodSystem: 寻找食物系统 - 处理寻找食物的行为
    SeekTargetSystem: 寻找目标系统 - 处理寻找目标的行为

    === 行动系统 (Action Systems) ===
    MovementSystem: 移动系统 - 处理实体的移动行为
    EatSystem: 进食系统 - 处理实体的进食行为
    DrinkSystem: 饮水系统 - 处理实体的饮水行为
    SleepSystem: 睡眠系统 - 处理实体的睡眠行为
    PickupSystem: 拾取系统 - 处理实体的拾取行为
    SearchSystem: 搜索系统 - 处理实体的搜索行为
    SocializeSystem: 社交系统 - 处理实体的社交行为

    === 死亡系统 (Death Systems) ===
    DeathSystem: 死亡系统 - 已迁移至 biology/systems/death_system.py（统一版）
    DeathSystem: 死亡系统 - 处理实体的死亡逻辑
"""

"""
human/systems/
├── __init__.py              # 更新：包含所有系统的导入和中文说明
├── core/                    # 核心系统
│   ├── action_system.py     # 行动系统
│   ├── planning_system.py   # 规划系统
│   └── intent_system.py     # 意图系统
├── physiological/           # 生理系统
│   ├── physiology_needs_system.py # 生理需求系统
│   └── health_system.py     # 健康系统
├── cognitive/               # 认知系统
│   └── preception_system.py # 感知系统
├── social/                  # 社交系统
│   ├── social_system.py     # 社交系统
│   ├── pairing_system.py    # 配对系统
│   └── reproduction_system.py # 繁衍系统
├── identity/                # 身份系统
│   └── identity_system.py   # 身份系统
├── survival/                # 生存系统
│   ├── seek_food_system.py  # 寻找食物系统
│   └── seek_target_system.py # 寻找目标系统
├── action/                  # 行动系统
│   └── action_systems/      # 具体行动系统
│       ├── movement_system.py # 移动系统
│       ├── eat_system.py    # 进食系统
│       ├── drink_system.py  # 饮水系统
│       ├── sleep_system.py  # 睡眠系统
│       ├── pickup_system.py # 拾取系统
│       ├── search_system.py # 搜索系统
│       └── socialize_system.py # 社交系统
└── death/                   # 死亡系统
    └── death_system.py      # 死亡系统
"""
# 核心系统
from .core.action_system import ActionSystem
from .core.planning_system import PlanningSystem
from .core.intent_system import IntentSystem

# 生理系统（合并遍历版）
from .physiological.physiology_needs_system import PhysiologyNeedsSystem
from .physiological.health_system import HealthSystem

# 认知系统
# from .cognitive.decision_system import DecisionSystem  # 空文件，暂不导入
# from .cognitive.goal_system import GoalSystem  # 空文件，暂不导入
from .cognitive.preception_system import PerceptionSystem

# 社交系统
from .social.social_system import SocialSystem
from .social.pairing_system import PairingSystem
from .social.reproduction_system import ReproductionSystem

# 身份系统
from .identity.identity_system import IdentitySystem
# from .identity.biology_system import BiologySystem  # 组件不存在，暂不导入

# 生存系统
from .survival.seek_food_system import SeekFoodSystem
from .survival.seek_target_system import SeekTargetSystem

# 行动系统
from .action.movement_system import MovementSystem
from .action.eat_system import EatSystem
from .action.drink_system import DrinkSystem
from .action.sleep_system import SleepSystem
from .action.pickup_system import PickupSystem
from .action.search_system import SearchSystem
from .action.socialize_system import SocializeSystem

# 死亡系统（已迁移至 biology/systems/death_system.py 统一版）
# from .death.death_system import DeathSystem
# 死亡系统
from .death.death_system import DeathSystem

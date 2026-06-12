#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类系统 — 最复杂的智能实体（认知、社交、经济、行动流水线）

目录结构:
    human/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── human_factory.py         # HumanFactory: 按预设创建人类实体
    ├── entities/                # 人类实体定义
    │   └── human_entity.py        # HumanEntity: 人类实体封装
    ├── components/              # 人类组件包 (按功能分类)
    │   ├── basic/                 # 基础属性
    │   │   ├── human_basic_component.py    # 基础属性 (姓名/性别/年龄)
    │   │   └── human_identity_component.py # 身份标识 (ID/家族/部落)
    │   ├── biology/               # 生理组件
    │   │   ├── human_health_component.py   # 健康状态 (疾病/伤口/体力)
    │   │   ├── human_hunger_component.py   # 饥饿状态 (饱腹度/营养需求)
    │   │   ├── human_thirst_component.py   # 口渴状态 (水分/脱水)
    │   │   └── human_sleep_component.py    # 睡眠状态 (精力/疲劳)
    │   ├── cognitive/             # 认知组件
    │   │   ├── memory_component.py         # 记忆存储 (事件/知识/经验)
    │   │   ├── perception_component.py   # 感知数据 (视野/听觉/嗅觉)
    │   │   ├── emotion_component.py       # 情绪状态 (愉悦/恐惧/愤怒)
    │   │   ├── thought_component.py       # 思维内容 (内心独白/推理)
    │   │   ├── goal_component.py          # 目标列表 (长期/短期/紧急)
    │   │   ├── decision_component.py      # 决策记录 (选项/评估/选择)
    │   │   └── plan_component.py          # 行动计划 (步骤/进度/资源)
    │   ├── social/                # 社交组件
    │   │   ├── relationship_component.py   # 关系网络 (亲密度/信任/敌意)
    │   │   ├── pairing_component.py       # 配对状态 (单身/恋爱/已婚)
    │   │   └── tribe_component.py         # 部落归属 (成员/角色/贡献)
    │   ├── abilities/             # 能力组件
    │   │   ├── skill_component.py          # 技能等级 (采集/建造/战斗)
    │   │   ├── speed_component.py         # 移动速度 (基础/修正/当前)
    │   │   └── special_ability_component.py # 特殊能力 (天赋/习得)
    │   ├── economic/              # 经济组件
    │   │   ├── inventory_component.py      # 物品库存 (容量/重量/分类)
    │   │   └── wallet_component.py        # 货币/资源 (数量/类型/交易记录)
    │   └── action/                # 行动组件
    │       ├── action_queue_component.py   # 行动队列 (待执行/执行中/已完成)
    │       └── action_history_component.py  # 行动历史 (记录/统计/反思)
    ├── systems/                 # 人类系统包 (行为流水线)
    │   ├── physiology/            # 生理系统
    │   │   └── physiology_needs_system.py   # 生理需求更新 (饥饿/口渴/精力/社交)
    │   ├── cognitive/             # 认知系统 (核心流水线)
    │   │   ├── perception_system.py       # 感知: 视野填充 (SpaceSystem.query_radius)
    │   │   ├── emotion_system.py          # 情绪: 四层驱动 (生理→环境→行为→社交)
    │   │   ├── thought_system.py          # 思维: 内心独白 (情绪+需求+行为)
    │   │   ├── goal_system.py             # 目标: 人生阶段目标 (童年/青年/成年/老年)
    │   │   ├── decision_system.py         # 决策: 多层评估 (生理+情绪+性格+记忆+目标)
    │   │   ├── planning_system.py         # 规划: Intent → ActionQueue (SEARCH→MOVE→PICKUP→USE)
    │   │   ├── memory_management_system.py  # 记忆管理: 存储/检索/遗忘/压缩 (v4.0 从 Component 迁移)
    │   │   └── intent_system.py           # 意图: Need → Intent (紧急度评分)
    │   ├── social/                # 社交系统
    │   │   ├── social_system.py           # 社交: 关系维护/互动选择/信任更新
    │   │   ├── pairing_system.py          # 配对: 求偶/恋爱/结婚/离婚
    │   │   └── reproduction_system.py     # 繁衍: 怀孕/分娩/育儿
    │   ├── action/                # 行动系统
    │   │   ├── action_system.py           # 行动调度: 出队/进度检查/切换
    │   │   ├── action_management_system.py # 行动管理: 创建/取消/查询 (v4.0 从 Component 迁移)
    │   │   ├── search_system.py           # 搜索: 资源/目标/路径发现
    │   │   ├── movement_system.py         # 移动: 路径执行/障碍物规避
    │   │   ├── eat_system.py              # 进食: 食物消耗/营养吸收
    │   │   ├── drink_system.py            # 饮水: 水源寻找/水分补充
    │   │   ├── sleep_system.py            # 睡眠: 睡眠地点/精力恢复
    │   │   ├── pickup_system.py           # 采集: 资源收集/工具使用
    │   │   ├── socialize_system.py        # 社交行动: 对话/礼物/合作
    │   │   └── combat_system.py           # 战斗: 攻击/防御/逃跑
    │   └── economic/              # 经济系统
    │       └── trade_system.py            # 交易: 价格评估/谈判/执行
    ├── rules/                   # 人类规则
    │   ├── moral_rules.py             # 道德规则 (善恶/公平/责任)
    │   ├── legal_rules.py             # 法律规则 (禁令/惩罚/权利)
    │   └── custom_rules.py            # 习俗规则 (礼仪/传统/禁忌)
    └── tests/                   # 人类测试包 (56 测试)
        ├── test_human_factory.py
        ├── test_memory_management_system.py  # 15 测试 (v4.0 新增)
        ├── test_action_management_system.py   # 8 测试 (v4.0 新增)
        └── ...

核心职责:
    1. 人类实体创建:
       - HumanFactory.create_human(): 按预设创建完整人类实体 (30+ 组件)
       - 支持年龄/性别/性格/技能等多样化预设
       - 生命周期: 婴儿→儿童→青年→成年→老年

    2. 行为流水线 (按 SystemScheduler 依赖图排序):
       Layer 1 — 生理:
         PhysiologyNeedsSystem → 更新饥饿/口渴/精力/社交需求 (环境耦合)
       Layer 2 — 感知:
         PerceptionSystem → 视野填充 (SpaceSystem.query_radius → vision.entities)
       Layer 3 — 认知:
         EmotionSystem → 四层情绪驱动 (生理→环境→行为→社交)
         ThoughtSystem → 内心独白 (情绪+需求+当前行为)
         GoalSystem → 人生阶段目标
         IntentSystem → Need → Intent (紧急度评分)
         DecisionSystem → 多层决策 (生理+情绪+性格+记忆+目标)
         PlanningSystem → Intent → ActionQueue (SEARCH→MOVE→PICKUP→USE)
       Layer 4 — 行动:
         ActionSystem → 调度器 (出队/进度检查/切换)
         动作执行系统群 → Search/Movement/Eat/Drink/Sleep/Pickup/Socialize/Combat
       Layer 5 — 社交:
         SocialSystem → 关系维护/互动选择
         PairingSystem → 求偶/配对
         ReproductionSystem → 繁衍

    3. 记忆管理 (v4.0 从 Component 迁移到 System):
       - MemoryManagementSystem: 存储/检索/遗忘/压缩
       - 记忆类型: 事件/知识/经验/情感
       - 记忆检索: 时间/地点/情感/关联度
       - 记忆遗忘: 时间衰减 + 重要性保护

    4. 行动管理 (v4.0 从 Component 迁移到 System):
       - ActionManagementSystem: 创建/取消/查询/统计
       - 行动类型: 采集/建造/战斗/社交/移动
       - 行动状态: 待执行/执行中/已完成/已取消

与其他模块的关系:
    - core/: 依赖 ECS 框架
    - biology/: 复用 Genome/Energy/LifeCycle/Morphology/Immune/Health 组件
    - biology/systems/: 统一调度生长/衰老/死亡
    - space/: 使用 SpatialIndex 进行位置查询、视野计算、路径规划
    - environment/: 环境因素驱动生理需求 (温度→体温/天气→行动限制)
    - animal/: 人类可驯化动物 (AnimalSocialSystem 驯化接口)
    - plant/: 人类采集植物 (PickupSystem 读取 PlantComponent)
    - resource/: 人类采集资源 (PickupSystem 读取 ResourceComponent)
    - civilization/: 人类个体行为汇聚成文明趋势 (技术/文化/经济)
    - memory_layer/: 人类使用 MemoryLayer 进行跨实体记忆共享
    - society/: 人类社交关系形成社会结构 (部落/村庄/城市)

设计原则:
    - 认知流水线: 感知→情绪→思维→目标→决策→规划→行动
    - 信息损失: 感知不完整、记忆会遗忘、决策有偏差
    - 社交涌现: 个体简单社交规则 → 复杂社会结构
    - 文明演化: 个体知识积累 → 群体技术树

版本: v4.0
"""

from .human_factory import HumanFactory

__all__ = [
    "HumanFactory",
]

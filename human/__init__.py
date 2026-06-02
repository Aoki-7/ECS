#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类系统模块 — 最复杂的智能实体领域

职责：
    - 定义人类特有的组件（生理需求、认知、社交、经济、行动等）
    - 实现人类行为流水线：感知 → 情绪 → 思维 → 目标 → 意图 → 决策 → 规划 → 行动
    - 管理人类的生命周期（出生、成长、衰老、死亡）
    - 支持社交关系、配对、繁衍、部落组织

子模块：
    - components/    : 人类组件包，按功能分类（基础属性/生理/认知/社交/能力/经济/行动）
    - systems/       : 人类系统包，实现行为流水线各阶段
    - entities/      : 人类实体定义与模板
    - rules/         : 人类特有规则（道德、法律、习俗约束）
    - human_factory.py: 人类工厂，按预设创建初始人口

行为流水线（按 System priority 排序）：
    1. PhysiologyNeedsSystem   — 更新饥饿/口渴/精力/社交需求（环境耦合）
    2. PerceptionSystem        — 视野填充：SpaceSystem.query_radius → vision.entities
    3. EmotionSystem           — 四层情绪驱动：生理→环境→行为→社交
    4. ThoughtSystem           — 根据情绪+需求+行为生成内心独白
    5. GoalSystem              — 按人生阶段生成长期目标
    6. IntentSystem            — Need → Intent（紧急度评分）
    7. DecisionSystem          — 多层决策：生理+情绪+性格+记忆+目标
    8. PlanningSystem          — Intent → ActionQueue（SEARCH→MOVE→PICKUP→USE）
    9. ActionSystem            — 调度器：出队/进度检查/切换
    10. 动作执行系统群         — Search/Movement/Eat/Drink/Sleep/Pickup/Socialize/Combat
    11. SocialSystem → PairingSystem → ReproductionSystem — 社交层

与 biology/ 的关系：
    - human/ 复用 biology/ 的生命周期、基因、健康组件
    - human/ 在 biology/ 基础上叠加认知、社交、文明等高级功能
"""

from .human_factory import HumanFactory

__all__ = [
    "HumanFactory",
]

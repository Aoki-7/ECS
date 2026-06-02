#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文明系统模块 — 群体级别的社会演进

职责：
    - CivilizationSystem      : 文明阶段检测（采集→农业→工业，基于科技与人口）
    - ResourceGatheringSystem : 群体资源采集策略与效率计算
    - ConstructionSystem      : 建筑项目管理（需求评估、资源分配、建造进度）
    - TradeSystem            : 宏观贸易（市场供需、贸易路线、价格浮动）
    - TechnologySystem       : 科技树管理（研发进度、技术解锁、知识传播）

与 human/ 的关系：
    - civilization/ 关注"群体"（部落、村庄、文明）
    - human/ 关注"个体"（行为、决策、社交）
    - 个体行为汇聚成群体趋势，群体趋势反过来约束个体行为

与 rules/ 的关系：
    - rules/ 处理微观资源转换（食物腐败、技能提升）
    - civilization/ 处理宏观资源配置（建筑、科技、贸易）
"""

from .systems.civilization_system import CivilizationSystem
from .systems.resource_gathering_system import ResourceGatheringSystem
from .systems.construction_system import ConstructionSystem
from .systems.trade_system import TradeSystem
from .systems.technology_system import TechnologySystem

__all__ = [
    'CivilizationSystem',
    'ResourceGatheringSystem',
    'ConstructionSystem',
    'TradeSystem',
    'TechnologySystem'
]
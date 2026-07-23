"""
规则包 — 约束、道德、法律、习俗

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则系统模块 — 条件驱动的状态转换引擎

职责：
    - TransformationRule: 定义"条件 → 变换"的规则结构
    - TransformationSystem: 每步扫描所有规则，对满足条件的实体执行状态变换
    - RulesConfig: 规则配置管理（加载、启用、优先级排序）

规则类型：
    - 资源转换：食物腐败（新鲜→腐败→剧毒）、木材腐朽、金属氧化
    - 状态转换：湿木头→干木头、生肉→熟肉
    - 技能提升：满足练习条件后提升 SkillComponent 等级
    - 财富积累：交易、采集后的 EconomyComponent 更新

设计原则：
    - 声明式规则：通过配置而非硬编码定义世界运行规律
    - 可扩展：新增规则只需添加 TransformationRule 实例，无需修改系统代码
    - 高性能：利用 World.get_components() 进行联合查询，避免全量遍历

与 civilization/ 的关系：
    - rules/ 处理微观个体状态变化
    - civilization/ 处理宏观文明阶段演进
"""

from .transformation_rule import TransformationRule
from .transformation_system import TransformationSystem
from .rules_config import (
    spoiled_food_condition,
    spoiled_food_transform,
    resource_depletion_condition,
    resource_depletion_transform,
)

__all__ = [
    "TransformationRule",
    "TransformationSystem",
    "spoiled_food_condition",
    "spoiled_food_transform",
    "resource_depletion_condition",
    "resource_depletion_transform",
]

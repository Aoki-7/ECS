#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CraftingKnowledgeComponent — 制作知识组件（自然演化版）- 纯数据版

v3.0.1 新增

核心设计原则：
- 无硬编码配方，配方从实践中自然涌现
- 技术不是"解锁"的，而是"发现"的
- 同一文明可能发展出完全不同的技术路线
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import random

from core.component import Component


@dataclass(slots=True)
class CraftingKnowledgeComponent(Component):
    """
    制作知识组件 - 纯数据

    记录个体/文明通过实践积累的制作经验。
    配方不是预设的，而是从成功尝试中自然形成的。
    """

    # 材料组合 -> 产出记录（从实践中学习）
    # key: "材料A+材料B+..." value: {产出物: 成功次数, 失败次数, 质量统计}
    material_experiments: Dict[str, Dict[str, Dict]] = field(default_factory=dict)

    # 已知制作技巧（从成功中提炼）
    # key: 技巧名 value: 熟练度(0-1)
    techniques: Dict[str, float] = field(default_factory=dict)

    # 成功案例记录（用于传授给他人）
    # [(输入材料, 产出物, 质量, 环境条件), ...]
    success_records: List[Dict] = field(default_factory=list)

    # 失败案例记录（避免重复错误）
    failure_records: List[Dict] = field(default_factory=list)

    # 探索倾向（0=保守，1=激进）— 影响尝试新配方的概率
    exploration_tendency: float = 0.3


@dataclass(slots=True)
class CulturalTechPoolComponent(Component):
    """
    文明技术池组件 - 纯数据

    记录整个文明（部落/社会）共享的技术知识。
    不同于个体的 CraftingKnowledge，这是群体层面的技术积累。
    """

    # 群体共享的配方（由个体成功案例汇聚）
    shared_recipes: Dict[str, Dict] = field(default_factory=dict)

    # 技术传统（该文明偏好的技术方向）
    # 从实践中自然形成，非预设
    tech_traditions: Dict[str, float] = field(default_factory=dict)

    # 知识传播记录（谁教给了谁）
    knowledge_transfers: List[Dict] = field(default_factory=list)

    # 技术多样性指数（越高说明该文明技术路线越独特）
    diversity_index: float = 0.0

    # 注意：integrate_individual_knowledge 已迁移到 CraftingKnowledgeSystem
    # 保留方法作为向后兼容的委托，实际逻辑在 System 中

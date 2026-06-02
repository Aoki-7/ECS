#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
身份层模块 — 实体的标识与属性定义

职责：
    - NameComponent: 实体的唯一名称标识（通用）
    - HumanNameComponent: 人类专用姓名（支持名/姓/全名格式）
    - BiologyComponent: 生物属性（物种、亚种、性别、年龄、寿命预期）
    - SocialComponent: 社会属性（阵营、阶级、职业、声望）

设计原则：
    - 本层提供"我是谁"的基础定义，不处理行为逻辑
    - 被 human/、animal/、plant/ 等领域模块依赖
    - 命名组件支持自动生成（基于物种/文化预设）

与 human/systems/identity/ 的区别：
    - identity/ (本模块) → 纯数据组件
    - human/systems/identity/ → 身份系统的逻辑处理（阵营合法性、年龄增长）
"""

from .name_component import NameComponent
from .human_name_component import HumanNameComponent
from .biology_component import BiologyComponent
from .social_component import FactionComponent

__all__ = [
    "NameComponent",
    "HumanNameComponent",
    "BiologyComponent",
    "FactionComponent",
]

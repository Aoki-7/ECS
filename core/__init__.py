#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:核心模块
@时间:2026/03/09 12:49:26
@作者:Sherry
@版本:1.0
'''

"""
    核心模块，包含
    Component
    Entity
    System
    CategoryComponent
    EntityCategory
    SubCategory 枚举集
"""

# ── ECS 核心 ───────────────
from core.component import Component
from core.entity import Entity
from core.system import System
from core.world import World

# ── 分类系统 ───────────────
from core.category import EntityCategory
from core.category_component import (
    CategoryComponent,
    get_subcategory_enum,
    CATEGORY_SUBCATEGORY_MAP,
    SubCategoryType,
)
from core.subcategory import (
    HumanSubCategory,
    AnimalSubCategory,
    PlantSubCategory,
    MicrobeSubCategory,
    FoodSubCategory,
    ResourceSubCategory,
    ItemSubCategory,
    OrgSubCategory,
    LocationSubCategory,
    SystemSubCategory,
    EventSubCategory,
)

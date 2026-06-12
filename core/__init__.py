"""
ECS 核心框架 — 实体、组件、系统、世界的底层架构

职责：
    - 提供 ECS 基础架构：Entity、Component、System、World
    - v4.0 新增：EntityManager、ArchetypeStore、SystemScheduler
    - 提供统一序列化、事件总线、空间索引等基础设施

版本：v4.0

"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
核心模块 — ECS 基础架构与实体分类系统

包含：
    - Component / Entity / System / World（ECS 核心四件套）
    - EntityCategory / SubCategory 枚举集（全局实体分类）
    - CategoryComponent（分类挂载组件）
    - 分类工具函数（推断、查询、校验）
"""

# ── ECS 核心 ───────────────
from core.component import Component
from core.entity import Entity
from core.system import System
from core.world import World

# ── 分类系统 ───────────────
from identity.category import EntityCategory
from identity.category_component import (
    CategoryComponent,
    get_subcategory_enum,
    get_category_by_subcategory,
    get_all_subcategories,
    infer_category_from_components,
    CATEGORY_SUBCATEGORY_MAP,
    SUBCATEGORY_TO_CATEGORY,
    SubCategoryType,
)
from identity.subcategory import (
    # 生物
    HumanSubCategory,
    AnimalSubCategory,
    PlantSubCategory,
    MicrobeSubCategory,
    # 尸体
    CorpseSubCategory,
    # 资源
    FoodSubCategory,
    WaterSubCategory,
    ResourceSubCategory,
    # 物品与装备
    ItemSubCategory,
    EquipmentSubCategory,
    # 环境
    WeatherSubCategory,
    TerrainSubCategory,
    SoilSubCategory,
    # 抽象/组织
    OrgSubCategory,
    LocationSubCategory,
    BuildingSubCategory,
    GarbageSubCategory,
    # 系统/虚拟
    SystemSubCategory,
    EventSubCategory,
)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块 — ECS 基础架构与实体分类系统

目录结构:
    core/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── entity.py                # Entity: 不可变实体标识 (id, generation)
    ├── component.py             # Component: 纯数据组件基类 (v4.0 零业务逻辑)
    ├── system.py                # System: 业务逻辑系统基类 (v4.0 声明式依赖图)
    ├── world.py                 # World: 协调者模式 (v4.0 委托给专职管理器)
    ├── entity_manager.py        # EntityManager: 实体生命周期管理 (v4.0)
    ├── archetype_store.py       # ArchetypeStore: Archetype-based 列式组件存储 (v4.0)
    ├── system_scheduler.py      # SystemScheduler: 依赖图解析 + 拓扑排序 (v4.0)
    ├── world_event_bus.py     # WorldEventBus: 每 World 独立事件总线 (v4.0)
    ├── component_serializer.py # ComponentSerializer: 统一序列化框架 (v4.0)
    ├── query_api.py             # QueryAPI: 声明式查询接口
    ├── event_bus.py             # EventBus: 全局事件总线 (legacy 兼容)
    ├── spatial_index.py         # SpatialIndex: 均匀网格空间索引
    └── tests/                   # 核心测试 (100+ 测试用例)

核心职责:
    1. ECS 基础架构: 提供 Entity/Component/System/World 四件套
    2. v4.0 架构升级:
       - EntityManager: 取代 World 直接管理实体 ID
       - ArchetypeStore: 取代 World 直接存储组件，列式布局提升缓存友好性
       - SystemScheduler: 取代 World 直接调度系统，声明式依赖替代魔法数字 priority
       - WorldEventBus: 每 World 独立事件总线，避免多 World 事件串扰
       - ComponentSerializer: 统一序列化，@register_component 自动注册
    3. 向后兼容: World 保持 v3.9 API (create_entity/add_component/get_components 等)，
       内部委托给新管理器，避免破坏现有系统

与其他模块的关系:
    - identity/: 实体分类系统 (EntityCategory/SubCategory) 挂载于 ECS 之上
    - 所有其他模块 (biology/animal/plant/human/...): 均依赖 core/ 作为底层框架
    - save_load/: 使用 ComponentSerializer 进行世界序列化

设计原则:
    - 无硬编码: 行为由数据 + 规则驱动，无特殊案例
    - 主客观分离: Component 存储客观状态，System 应用主观解释
    - 信息损失: 距离、时间、介质会降解信息
    - 组件纯数据: v4.0 所有业务逻辑在 System 中，Component 仅含数据

版本: v4.0
"""

# ── ECS 核心 ───────────────
from core.component import Component
from core.entity import Entity
from core.system import System
from core.world import World

# ── v4.0 新增管理器 ─────────
from core.entity_manager import EntityManager
from core.archetype_store import ArchetypeStore
from core.system_scheduler import SystemScheduler
from core.world_event_bus import WorldEventBus
from core.component_serializer import ComponentSerializer, register_component

# ── 基础设施 ───────────────
from core.query_api import QueryResult, WorldQueryMixin
from core.event_bus import EventBus
from core.spatial_index import SpatialIndex

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

__all__ = [
    # ECS 核心
    "Component",
    "Entity",
    "System",
    "World",
    # v4.0 管理器
    "EntityManager",
    "ArchetypeStore",
    "SystemScheduler",
    "WorldEventBus",
    "ComponentSerializer",
    "register_component",
    # 基础设施
    "QueryResult",
    "WorldQueryMixin",
    "EventBus",
    "SpatialIndex",
    # 分类系统
    "EntityCategory",
    "CategoryComponent",
    "SubCategoryType",
    "HumanSubCategory",
    "AnimalSubCategory",
    "PlantSubCategory",
    "MicrobeSubCategory",
    "CorpseSubCategory",
    "FoodSubCategory",
    "WaterSubCategory",
    "ResourceSubCategory",
    "ItemSubCategory",
    "EquipmentSubCategory",
    "WeatherSubCategory",
    "TerrainSubCategory",
    "SoilSubCategory",
    "OrgSubCategory",
    "LocationSubCategory",
    "BuildingSubCategory",
    "GarbageSubCategory",
    "SystemSubCategory",
    "EventSubCategory",
    "get_subcategory_enum",
    "get_category_by_subcategory",
    "get_all_subcategories",
    "infer_category_from_components",
    "CATEGORY_SUBCATEGORY_MAP",
    "SUBCATEGORY_TO_CATEGORY",
]

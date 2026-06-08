#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ECS 分类组件与工具函数

提供实体分类的挂载、校验、查询和推断能力。
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

from core.component import Component
from core.category import EntityCategory
from core.subcategory import (
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


# ── 子分类联合类型 ──────────────────────────────────────────────

SubCategoryType = (
    HumanSubCategory
    | AnimalSubCategory
    | PlantSubCategory
    | MicrobeSubCategory
    | CorpseSubCategory
    | FoodSubCategory
    | WaterSubCategory
    | ResourceSubCategory
    | ItemSubCategory
    | EquipmentSubCategory
    | WeatherSubCategory
    | TerrainSubCategory
    | SoilSubCategory
    | OrgSubCategory
    | LocationSubCategory
    | BuildingSubCategory
    | GarbageSubCategory
    | SystemSubCategory
    | EventSubCategory
    | None
)


# ── Category → 子分类枚举的映射表 ─────────────────────────────────

CATEGORY_SUBCATEGORY_MAP: dict[EntityCategory, type[Enum]] = {
    EntityCategory.HUMAN:      HumanSubCategory,
    EntityCategory.ANIMAL:     AnimalSubCategory,
    EntityCategory.PLANT:      PlantSubCategory,
    EntityCategory.MICROBE:    MicrobeSubCategory,
    EntityCategory.CORPSE:     CorpseSubCategory,
    EntityCategory.FOOD:       FoodSubCategory,
    EntityCategory.WATER:      WaterSubCategory,
    EntityCategory.RESOURCE:   ResourceSubCategory,
    EntityCategory.ITEM:       ItemSubCategory,
    EntityCategory.EQUIPMENT:  EquipmentSubCategory,
    EntityCategory.WEATHER:    WeatherSubCategory,
    EntityCategory.TERRAIN:    TerrainSubCategory,
    EntityCategory.SOIL:       SoilSubCategory,
    EntityCategory.ORG:        OrgSubCategory,
    EntityCategory.LOCATION:   LocationSubCategory,
    EntityCategory.BUILDING:   BuildingSubCategory,
    EntityCategory.GARBAGE:    GarbageSubCategory,
    EntityCategory.SYSTEM:     SystemSubCategory,
    EntityCategory.EVENT:      EventSubCategory,
}


# ── 反向映射：子分类枚举 → Category ─────────────────────────────────

SUBCATEGORY_TO_CATEGORY: dict[type[Enum], EntityCategory] = {
    enum_type: category
    for category, enum_type in CATEGORY_SUBCATEGORY_MAP.items()
}


# ── 组件推断映射：组件类 → EntityCategory ───────────────────────────

_COMPONENT_CATEGORY_HINTS: dict[str, EntityCategory] = {
    "HumanComponent": EntityCategory.HUMAN,
    "AnimalComponent": EntityCategory.ANIMAL,
    "PlantComponent": EntityCategory.PLANT,
    "CorpseComponent": EntityCategory.CORPSE,
    "FoodComponent": EntityCategory.FOOD,
    "WaterComponent": EntityCategory.WATER,
    "EquipmentComponent": EntityCategory.EQUIPMENT,
    "WeatherComponent": EntityCategory.WEATHER,
    "TerrainComponent": EntityCategory.TERRAIN,
    "SoilComponent": EntityCategory.SOIL,
    "GarbageComponent": EntityCategory.GARBAGE,
}


# ── 工具函数 ─────────────────────────────────────────────────────

def get_subcategory_enum(category: EntityCategory) -> type[Enum] | None:
    """
    根据 EntityCategory 返回对应的子分类枚举类型。
    若没有子分类（如 UNKNOWN），返回 None。
    """
    return CATEGORY_SUBCATEGORY_MAP.get(category)


def get_category_by_subcategory(subcategory: SubCategoryType) -> EntityCategory | None:
    """
    根据子分类值返回对应的主分类。
    """
    if subcategory is None:
        return None
    enum_type = type(subcategory)
    return SUBCATEGORY_TO_CATEGORY.get(enum_type)


def infer_category_from_components(entity_components: list[type]) -> EntityCategory:
    """
    根据实体已挂载的组件类型推断其主分类。

    Args:
        entity_components: 实体上已挂载的组件类列表（如 [HumanComponent, SpaceComponent]）

    Returns:
        推断出的 EntityCategory，无法推断时返回 EntityCategory.UNKNOWN
    """
    for comp_cls in entity_components:
        name = comp_cls.__name__
        if name in _COMPONENT_CATEGORY_HINTS:
            return _COMPONENT_CATEGORY_HINTS[name]
    return EntityCategory.UNKNOWN


def get_all_subcategories(category: EntityCategory) -> list[Enum]:
    """
    获取某主分类下的所有子分类枚举值。

    Args:
        category: 主分类

    Returns:
        子分类枚举值列表，无子分类时返回空列表
    """
    enum_type = CATEGORY_SUBCATEGORY_MAP.get(category)
    if enum_type is None:
        return []
    return list(enum_type)


# ── 组件定义 ─────────────────────────────────────────────────────

@dataclass(slots=True)
class CategoryComponent(Component):
    """
    ECS 分类组件

    将 EntityCategory + 子分类挂载到实体上，支持快速筛选和统计。

    用法:
        entity = world.create_entity()
        comp = CategoryComponent(
            category=EntityCategory.HUMAN,
            subcategory=HumanSubCategory.WORKER
        )
        world.add_component(entity, comp)

        # 查询匹配
        if comp.matches(EntityCategory.HUMAN):  # True
            ...
        if comp.matches(EntityCategory.HUMAN, HumanSubCategory.WORKER):  # True
            ...
    """

    category: EntityCategory = EntityCategory.UNKNOWN
    subcategory: SubCategoryType = None
    tags: list[str] = field(default_factory=list)  # 额外标签，灵活扩展

    def __post_init__(self):
        # 校验子分类与主分类是否匹配
        if self.subcategory is not None and self.category is not EntityCategory.UNKNOWN:
            expected_enum = get_subcategory_enum(self.category)
            if expected_enum is None:
                raise ValueError(
                    f"类别 {self.category.name} 没有对应的子分类枚举"
                )
            if not isinstance(self.subcategory, expected_enum):
                raise ValueError(
                    f"子分类 {self.subcategory} 不属于 {self.category.name} 的子分类枚举 "
                    f"{expected_enum.__name__}"
                )

    def matches(self, category: EntityCategory, subcategory: SubCategoryType = None) -> bool:
        """
        检查是否匹配指定的分类（和可选的子分类）。

        Args:
            category: 要匹配的主分类
            subcategory: 可选的子分类，为 None 时只匹配主分类

        Returns:
            是否匹配
        """
        if self.category != category:
            return False
        if subcategory is not None and self.subcategory != subcategory:
            return False
        return True

    def has_tag(self, tag: str) -> bool:
        """检查是否包含指定标签"""
        return tag in self.tags

    def add_tag(self, tag: str) -> None:
        """添加标签（去重）"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典"""
        return {
            "category": self.category.name,
            "subcategory": self.subcategory.name if self.subcategory else None,
            "tags": self.tags.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CategoryComponent":
        """从字典反序列化"""
        category = EntityCategory[data["category"]] if data.get("category") else EntityCategory.UNKNOWN
        subcategory = None
        if data.get("subcategory") and category is not EntityCategory.UNKNOWN:
            enum_type = get_subcategory_enum(category)
            if enum_type is not None:
                subcategory = enum_type[data["subcategory"]]
        return cls(
            category=category,
            subcategory=subcategory,
            tags=data.get("tags", []).copy(),
        )

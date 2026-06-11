#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ECS 分类组件与工具函数

v3.9 迁移：从 core/ 移回 identity/，保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

from core.component import Component
from identity.category import EntityCategory
from identity.subcategory import (
    HumanSubCategory,
    AnimalSubCategory,
    PlantSubCategory,
    MicrobeSubCategory,
    CorpseSubCategory,
    FoodSubCategory,
    WaterSubCategory,
    ResourceSubCategory,
    ItemSubCategory,
    EquipmentSubCategory,
    WeatherSubCategory,
    TerrainSubCategory,
    SoilSubCategory,
    OrgSubCategory,
    LocationSubCategory,
    BuildingSubCategory,
    GarbageSubCategory,
    SystemSubCategory,
    EventSubCategory,
)


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


SUBCATEGORY_TO_CATEGORY: dict[type[Enum], EntityCategory] = {
    enum_type: category
    for category, enum_type in CATEGORY_SUBCATEGORY_MAP.items()
}


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


def get_subcategory_enum(category: EntityCategory) -> type[Enum] | None:
    """根据 EntityCategory 返回对应的子分类枚举类型。"""
    return CATEGORY_SUBCATEGORY_MAP.get(category)


def get_category_by_subcategory(subcategory: SubCategoryType) -> EntityCategory | None:
    """根据子分类值返回对应的主分类。"""
    if subcategory is None:
        return None
    enum_type = type(subcategory)
    return SUBCATEGORY_TO_CATEGORY.get(enum_type)


def infer_category_from_components(entity_components: list[type]) -> EntityCategory:
    """根据实体已挂载的组件类型推断其主分类。"""
    for comp_cls in entity_components:
        name = comp_cls.__name__
        if name in _COMPONENT_CATEGORY_HINTS:
            return _COMPONENT_CATEGORY_HINTS[name]
    return EntityCategory.UNKNOWN


def get_all_subcategories(category: EntityCategory) -> list[Enum]:
    """获取某主分类下的所有子分类枚举值。"""
    enum_type = CATEGORY_SUBCATEGORY_MAP.get(category)
    if enum_type is None:
        return []
    return list(enum_type)


@dataclass(slots=True)
class CategoryComponent(Component):
    """ECS 分类组件"""

    category: EntityCategory = EntityCategory.UNKNOWN
    subcategory: SubCategoryType = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.subcategory is not None and self.category is not EntityCategory.UNKNOWN:
            expected_enum = get_subcategory_enum(self.category)
            if expected_enum is None:
                raise ValueError(f"类别 {self.category.name} 没有对应的子分类枚举")
            if not isinstance(self.subcategory, expected_enum):
                raise ValueError(
                    f"子分类 {self.subcategory} 不属于 {self.category.name} 的子分类枚举 "
                    f"{expected_enum.__name__}"
                )

    def matches(self, category: EntityCategory, subcategory: SubCategoryType = None) -> bool:
        """检查是否匹配指定的分类。"""
        if self.category != category:
            return False
        if subcategory is not None and self.subcategory != subcategory:
            return False
        return True

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.name,
            "subcategory": self.subcategory.name if self.subcategory else None,
            "tags": self.tags.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CategoryComponent":
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

# core/category_component.py

from dataclasses import dataclass, asdict, field
from typing import Any, Optional
from enum import Enum

from core.category import EntityCategory
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
from core.component import Component


# ── 子分类联合类型 ──────────────────────────────────────────────

SubCategoryType = (
    HumanSubCategory
    | AnimalSubCategory
    | PlantSubCategory
    | MicrobeSubCategory
    | FoodSubCategory
    | ResourceSubCategory
    | ItemSubCategory
    | OrgSubCategory
    | LocationSubCategory
    | SystemSubCategory
    | EventSubCategory
    | None
)


# ── Category → 子分类枚举的映射表 ─────────────────────────────────

CATEGORY_SUBCATEGORY_MAP: dict[EntityCategory, type[Enum]] = {
    EntityCategory.HUMAN:     HumanSubCategory,
    EntityCategory.ANIMAL:    AnimalSubCategory,
    EntityCategory.PLANT:     PlantSubCategory,
    EntityCategory.MICROBE:   MicrobeSubCategory,
    EntityCategory.FOOD:      FoodSubCategory,
    EntityCategory.RESOURCE:  ResourceSubCategory,
    EntityCategory.ITEM:      ItemSubCategory,
    EntityCategory.ORG:       OrgSubCategory,
    EntityCategory.LOCATION:  LocationSubCategory,
    EntityCategory.SYSTEM:    SystemSubCategory,
    EntityCategory.EVENT:     EventSubCategory,
}


def get_subcategory_enum(category: EntityCategory) -> type[Enum] | None:
    """
    根据 EntityCategory 返回对应的子分类枚举类型。
    若没有子分类（如 UNKNOWN），返回 None。
    """
    return CATEGORY_SUBCATEGORY_MAP.get(category)


# ── 组件定义 ─────────────────────────────────────────────────────

@dataclass
class CategoryComponent(Component):
    """
    ECS 分类组件
    将 EntityCategory + 子分类挂载到实体上。

    用法:
        entity = world.create_entity()
        comp = CategoryComponent(
            category=EntityCategory.HUMAN,
            subcategory=HumanSubCategory.WORKER
        )
        world.add_component(entity, comp)
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

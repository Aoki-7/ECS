"""
身份系统 — 实体分类、子类别、标签管理

职责：

依赖：
    - core/

"""
from .category import EntityCategory
from .subcategory import (
    HumanSubCategory, AnimalSubCategory, PlantSubCategory, MicrobeSubCategory,
    CorpseSubCategory, FoodSubCategory, WaterSubCategory, ResourceSubCategory,
    ItemSubCategory, EquipmentSubCategory, WeatherSubCategory, TerrainSubCategory,
    SoilSubCategory, OrgSubCategory, LocationSubCategory, BuildingSubCategory,
    GarbageSubCategory, SystemSubCategory, EventSubCategory,
)
from .category_component import CategoryComponent
from .event_log_component import EventLogComponent
from .event_log_system import EventLogSystem

__all__ = [
    "EntityCategory",
    "HumanSubCategory", "AnimalSubCategory", "PlantSubCategory", "MicrobeSubCategory",
    "CorpseSubCategory", "FoodSubCategory", "WaterSubCategory", "ResourceSubCategory",
    "ItemSubCategory", "EquipmentSubCategory", "WeatherSubCategory", "TerrainSubCategory",
    "SoilSubCategory", "OrgSubCategory", "LocationSubCategory", "BuildingSubCategory",
    "GarbageSubCategory", "SystemSubCategory", "EventSubCategory",
    "CategoryComponent",
    "EventLogComponent",
    "EventLogSystem",
]

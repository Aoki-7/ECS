#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定居点组件，管理村庄/城镇的状态
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set
from enum import Enum
from core.component import Component

class SettlementType(Enum):
    """定居点类型"""
    CAMP = "camp"                # 营地：10人以下
    VILLAGE = "village"          # 村庄：10-100人
    TOWN = "town"                # 城镇：100-1000人
    CITY = "city"                # 城市：1000人以上

class BuildingType(Enum):
    """建筑类型"""
    HOUSE = "house"              # 房屋：居住，增加人口容量
    STORAGE = "storage"          # 仓库：存储资源
    WORKSHOP = "workshop"        # 工坊：制作工具/物品
    WALL = "wall"                # 围墙：防御
    FARMLAND = "farmland"        # 农田：农业生产

@dataclass(slots=True)
class SettlementComponent(Component):
    """定居点组件"""
    name: str = "New Settlement"
    settlement_type: SettlementType = SettlementType.CAMP

    # 中心位置
    center_x: float = 0.0
    center_y: float = 0.0

    # 范围
    radius: float = 10.0

    # 居民
    residents: Set[int] = field(default_factory=set)  # 居民实体ID

    # 建筑
    buildings: List[Dict] = field(default_factory=list)  # 建筑列表 {type, x, y, level}

    # 资源存储
    stored_resources: Dict[str, float] = field(default_factory=dict)  # 资源类型 -> 数量

    # 防御值
    defense: float = 0.0

    def add_resident(self, entity_id: int):
        """添加居民"""
        self.residents.add(entity_id)
        self._update_type()

    def remove_resident(self, entity_id: int):
        """移除居民"""
        if entity_id in self.residents:
            self.residents.remove(entity_id)
            self._update_type()

    def _update_type(self):
        """根据人口数量更新定居点类型"""
        pop = len(self.residents)
        if pop < 10:
            self.settlement_type = SettlementType.CAMP
        elif pop < 100:
            self.settlement_type = SettlementType.VILLAGE
        elif pop < 1000:
            self.settlement_type = SettlementType.TOWN
        else:
            self.settlement_type = SettlementType.CITY

    def add_building(self, building_type: BuildingType, x: float, y: float, level: int = 1):
        """添加建筑"""
        self.buildings.append({
            "type": building_type,
            "x": x,
            "y": y,
            "level": level,
        })
        # 围墙增加防御
        if building_type == BuildingType.WALL:
            self.defense += level * 10.0

    def get_population(self) -> int:
        """获取人口数量"""
        return len(self.residents)

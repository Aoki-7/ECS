#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根系系统

v3.2 新增 — P0

职责：
    - 管理植物根系生长
    - 计算根系竞争（水分/养分）
    - 支持菌根共生

依赖：
    - RootComponent
    - PlantComponent
    - SpaceComponent（位置）
    - SoilComponent（土壤养分）
"""

import math
from typing import Dict, List, Optional, Tuple

from core.system import System
from core.world import World

from biology.components.root_component import RootComponent
from plant.components.plant_component import PlantComponent
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent

import logging

logger = logging.getLogger(__name__)


class RootSystem(System):
    """
    根系系统

    每帧更新：
    1. 根系生长（深度、范围、密度）
    2. 水分吸收（与周围植物竞争）
    3. 养分吸收（与周围植物竞争）
    4. 菌根共生效果
    """

    tick_interval = 5  # 每5帧执行一次（根系变化较慢）

    # 生长参数
    GROWTH_RATE = 0.001
    MAX_DEPTH = 5.0
    MAX_SPREAD = 10.0

    # 竞争参数
    COMPETITION_RADIUS = 5.0
    COMPETITION_FACTOR = 0.5

    def update(self, world: World, dt: float) -> None:
        """更新所有植物的根系"""
        # 1. 根系生长
        self._grow_roots(world, dt)

        # 2. 计算根系竞争
        competition_map = self._calculate_competition(world)

        # 3. 水分和养分吸收
        self._absorb_resources(world, competition_map, dt)

        # 4. 菌根共生
        self._apply_mycorrhizal(world, dt)

    def _grow_roots(self, world: World, dt: float) -> None:
        """根系生长"""
        for entity, (root, plant) in world.get_components(RootComponent, PlantComponent):
            if root is None or plant is None:
                continue

            # 根据植物健康度计算生长速率（PlantComponent 没有 health 字段，使用默认值 1.0）
            plant_health = getattr(plant, 'health', 1.0)
            growth_factor = plant_health * self.GROWTH_RATE * dt

            # 深度生长
            if root.depth < self.MAX_DEPTH:
                root.depth = min(self.MAX_DEPTH, root.depth + growth_factor)

            # 范围扩展
            if root.spread < self.MAX_SPREAD:
                root.spread = min(self.MAX_SPREAD, root.spread + growth_factor * 2)

            # 密度增加
            if root.density < 1.0:
                root.density = min(1.0, root.density + growth_factor * 0.5)

    def _calculate_competition(self, world: World) -> Dict[int, float]:
        """
        计算每株植物的根系竞争系数

        Returns:
            {entity_id: competition_factor}
        """
        competition_map: Dict[int, float] = {}

        # 获取所有带根系的植物
        plants = []
        for entity, (root, space) in world.get_components(RootComponent, SpaceComponent):
            if root is None or space is None:
                continue
            plants.append((entity.id, space, root))

        # 计算竞争
        for i, (eid1, space1, root1) in enumerate(plants):
            competition = 0.0

            for j, (eid2, space2, root2) in enumerate(plants):
                if i == j:
                    continue

                # 计算距离
                dist = math.hypot(space1.x - space2.x, space1.y - space2.y)

                # 如果根系范围重叠，产生竞争
                overlap = (root1.spread + root2.spread) - dist
                if overlap > 0:
                    # 竞争强度与重叠程度成正比
                    competition += (overlap / root1.spread) * root2.density

            competition_map[eid1] = min(1.0, competition * self.COMPETITION_FACTOR)

        return competition_map

    def _absorb_resources(self, world: World, competition_map: Dict[int, float], dt: float) -> None:
        """吸收水分和养分（从土壤和地下水）"""
        for entity, (root, plant, space) in world.get_components(RootComponent, PlantComponent, SpaceComponent):
            if root is None or plant is None or space is None:
                continue

            # 获取竞争系数
            competition = competition_map.get(entity.id, 0.0)

            # 实际吸收量 = 基础吸收量 * (1 - 竞争) * 健康度
            effective_factor = (1.0 - competition) * root.root_health

            # 水分吸收（优先从地下水，其次土壤）
            water_absorbed = root.water_absorption * effective_factor * dt
            
            # 先从地下水吸水
            groundwater_absorbed = self._absorb_from_groundwater(world, space, water_absorbed)
            remaining_water = water_absorbed - groundwater_absorbed
            
            # 再从土壤吸水
            soil_water_absorbed = self._absorb_from_soil(world, space, remaining_water)
            
            total_water = groundwater_absorbed + soil_water_absorbed
            if hasattr(plant, 'water') and hasattr(plant, 'max_water'):
                plant.water = min(plant.max_water, plant.water + total_water)

            # 养分吸收（如果 PlantComponent 支持）
            nutrient_absorbed = root.nutrient_absorption * effective_factor * dt
            if hasattr(plant, 'nutrients') and hasattr(plant, 'max_nutrients'):
                plant.nutrients = min(plant.max_nutrients, plant.nutrients + nutrient_absorbed)

            # 从土壤中扣除
            self._consume_soil_resources(world, space, soil_water_absorbed, nutrient_absorbed)

    def _absorb_from_groundwater(self, world: World, space: SpaceComponent, amount: float) -> float:
        """从地下水吸水"""
        total_absorbed = 0.0
        
        for entity, (groundwater, gw_space) in world.get_components(GroundwaterComponent, SpaceComponent):
            if groundwater is None or gw_space is None:
                continue
            
            dist = math.hypot(space.x - gw_space.x, space.y - gw_space.y)
            if dist < 10.0:  # 10单位范围内
                absorb = min(amount * 0.5, groundwater.water_table * 0.1)
                groundwater.water_table -= absorb * 0.1
                total_absorbed += absorb
                
        return total_absorbed
    
    def _absorb_from_soil(self, world: World, space: SpaceComponent, amount: float) -> float:
        """从土壤吸水"""
        total_absorbed = 0.0
        
        for entity, (soil, soil_space) in world.get_components(SoilComponent, SpaceComponent):
            if soil is None or soil_space is None:
                continue
            
            dist = math.hypot(space.x - soil_space.x, space.y - soil_space.y)
            if dist < 5.0:  # 5单位范围内
                absorb = min(amount, soil.moisture * 10)
                soil.moisture = max(0.0, soil.moisture - absorb * 0.01)
                total_absorbed += absorb
                
        return total_absorbed

    def _consume_soil_resources(self, world: World, space: SpaceComponent, water: float, nutrient: float) -> None:
        """从土壤中消耗资源"""
        # 简化处理：直接减少世界土壤总量
        # 实际应该从 SpaceSystem 获取对应位置的土壤
        pass

    def _apply_mycorrhizal(self, world: World, dt: float) -> None:
        """应用菌根共生效果"""
        for entity, (root, plant) in world.get_components(RootComponent, PlantComponent):
            if root is None or plant is None:
                continue

            if not root.mycorrhizal:
                continue

            # 菌根共生效果：增加养分吸收效率（如果 PlantComponent 支持）
            bonus = 0.2 * dt
            if hasattr(plant, 'nutrients') and hasattr(plant, 'max_nutrients'):
                plant.nutrients = min(plant.max_nutrients, plant.nutrients + bonus)

            # 菌根也增加水分吸收（如果 PlantComponent 支持）
            water_bonus = 0.1 * dt
            if hasattr(plant, 'water') and hasattr(plant, 'max_water'):
                plant.water = min(plant.max_water, plant.water + water_bonus)

    def get_root_zone_entities(self, world: World, entity_id: int, radius: Optional[float] = None) -> List[int]:
        """
        获取与指定实体根系区域重叠的其他实体

        Args:
            entity_id: 目标实体 ID
            radius: 搜索半径（默认使用根系 spread）

        Returns:
            重叠的实体 ID 列表
        """
        entity = world.query_entity(entity_id)
        if entity is None:
            return []

        space = world.get_component(entity, SpaceComponent)
        root = world.get_component(entity, RootComponent)
        if space is None or root is None:
            return []

        search_radius = radius or root.spread
        overlapping = []

        for other_id, (other_space, other_root) in world.get_components(SpaceComponent, RootComponent):
            if other_id == entity_id:
                continue

            dist = math.hypot(space.x - other_space.x, space.y - other_space.y)
            if dist < search_radius + other_root.spread:
                overlapping.append(other_id)

        return overlapping

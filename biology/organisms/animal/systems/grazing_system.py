#!/usr/bin/env python3
"""
动物啃食系统 v4.16.0
实现食草动物啃食植物、获取食物的行为逻辑
"""

import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from biology.organisms.animal.components.animal_component import AnimalComponent
from biology.organisms.animal.components.animal_needs_component import AnimalNeedsComponent
from biology.organisms.plant.components.plant_component import PlantComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class GrazingSystem(System):
    """
    食草动物啃食系统
    处理食草动物寻找和啃食植物的行为
    """

    tick_interval = 5  # 每5tick执行一次
    priority = 170  # 在动物需求系统之后运行

    # 啃食参数
    GRAZING_RADIUS = 2.0  # 啃食范围（米）
    MAX_PLANT_CONSUMPTION_PER_TICK = 0.3  # 每次最多啃食植物大小的30%
    MIN_PLANT_SIZE_TO_GRAZE = 0.2  # 植物最小可啃食大小
    HUNGER_THRESHOLD_TO_GRAZE = 50.0  # 饥饿度超过50才会主动啃食

    def update(self, world: World, dt: float):
        # 遍历所有饥饿的食草动物
        for entity, animal, needs, space in world.query(
            AnimalComponent,
            AnimalNeedsComponent,
            SpaceComponent
        ):
            # 只要肉食偏好低于0.7的动物都可以食用植物（包括偏杂食的动物）
            if animal.carnivore_preference >= 0.7:
                continue
            # 只处理饥饿的动物（hunger 0=饱，1=饿）
            if needs.hunger < self.HUNGER_THRESHOLD_TO_GRAZE / 100.0:
                continue
            if needs.hunger <= 0.1:  # 10%以下算饱足
                continue
            if animal.is_dead:
                continue
            
            # 搜索周围的可食用植物
            edible_plants = self._find_edible_plants(world, space.x, space.y, animal)
            if not edible_plants:
                # 没有找到植物，触发寻路（后续对接动物行为规划）
                continue
            
            # 选择最近的可食用植物
            selected_plant = min(edible_plants, key=lambda x: x[1])  # 按距离排序选最近
            plant_entity, distance = selected_plant
            
            # 距离足够近则啃食
            if distance <= self.GRAZING_RADIUS:
                self._graze_plant(world, entity, animal, needs, plant_entity)
            else:
                # 距离太远，向植物移动（后续对接移动系统）
                pass

    def _find_edible_plants(self, world: World, x: float, y: float, animal: AnimalComponent) -> list[Tuple[Entity, float]]:
        """查找周围可食用的植物"""
        edible_plants = []
        search_radius = animal.perception_range if hasattr(animal, 'perception_range') else 10.0
        
        for e, plant, lc, s in world.query(PlantComponent, LifeCycleComponent, SpaceComponent):
            if lc.is_dead:
                continue
            if lc.stage < 2:  # 植物至少到生长期才可食用
                continue
            if hasattr(plant, 'is_edible') and not plant.is_edible:
                continue
            if plant.size < self.MIN_PLANT_SIZE_TO_GRAZE:
                continue
            
            # 计算距离
            distance = ((s.x - x)**2 + (s.y - y)**2)**0.5
            if distance <= search_radius:
                # 检查动物是否可以食用这种植物
                if hasattr(animal, 'edible_plants') and plant.type not in animal.edible_plants:
                    continue
                edible_plants.append((e, distance))
        
        return edible_plants

    def _graze_plant(self, world: World, animal_entity: Entity, animal: AnimalComponent, needs: AnimalNeedsComponent, plant_entity: Entity) -> None:
        """动物啃食植物"""
        plant = world.get_component(plant_entity, PlantComponent)
        if not plant:
            return
        
        # 计算啃食量
        max_graze = min(
            self.MAX_PLANT_CONSUMPTION_PER_TICK * plant.size,
            animal.max_food_intake if hasattr(animal, 'max_food_intake') else 0.5
        )
        # 饥饿度越高，吃的越多，最多吃到饱
        graze_amount = min(max_graze, needs.hunger)
        graze_amount = max(0.05, graze_amount)  # 最少啃食0.05单位
        
        # 减少植物大小
        plant.size = max(0.0, plant.size - graze_amount)
        
        # 植物被啃光了则死亡
        if plant.size <= 0.01:
            lc = world.get_component(plant_entity, LifeCycleComponent)
            if lc:
                lc.is_dead = True
                lc.stage = 4  # DEAD
        
        # 满足动物饥饿需求
        nutrition_value = plant.nutrition_value if hasattr(plant, 'nutrition_value') else 0.8
        # 吃多少就减少多少饥饿度，乘以营养价值系数
        hunger_reduction = graze_amount * nutrition_value
        needs.hunger = max(0.0, needs.hunger - hunger_reduction)
        
        # 啃食降低植物生长速度
        if hasattr(plant, 'growth_rate'):
            plant.growth_rate = max(0.0, plant.growth_rate - 0.3)
        
        logger.debug(f"[GrazingSystem] E{animal_entity.id}啃食植物E{plant_entity.id}，获得{hunger_gain:.1f}饱食度")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农场系统

v3.0.1 新增 — 农业系统自然演化版

职责：
    - 管理农田地块的生长周期
    - 处理播种/灌溉/收割行为
    - 从环境条件计算作物生长
    - 记录农业知识到 FarmingKnowledgeComponent
"""

import random
from typing import Dict, List, Optional

from core.system import System
from core.world import World

from civilization.components.farm_component import (
    FarmPlotComponent, FarmingKnowledgeComponent, IrrigationComponent
)
from civilization.components.building_component import BuildingComponent
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent

import logging

logger = logging.getLogger(__name__)


class FarmSystem(System):
    """
    农场系统

    处理农田的生长、灌溉、收割。
    无硬编码作物规则，生长从环境条件自然计算。
    """

    tick_interval = 5  # 每5帧执行一次

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有农田"""
        env = world.get_environment()
        time = world.get_time()
        season = self._get_season(time.day_of_year) if time else "spring"

        conditions = {
            "temperature": getattr(env, "air_temperature", 20.0) if env else 20.0,
            "light": getattr(env, "par", 500.0) / 1000.0 if env else 0.5,
            "moisture": getattr(env, "relative_humidity", 50.0) / 100.0 if env else 0.5,
        }

        for entity, (farm, space) in world.get_components(
            FarmPlotComponent, SpaceComponent
        ):
            # 获取土壤组件
            soil = world.get_component(entity, SoilComponent)
            if soil:
                farm.soil_quality = self._calculate_soil_quality(soil)

            # 更新作物生长
            farm.update_growth(dt, conditions)

            # 自动灌溉（如果有灌溉组件）
            irrigation = world.get_component(entity, IrrigationComponent)
            if irrigation and farm.water_level < 0.3:
                irrigation.irrigate(farm, 0.2)

    def _calculate_soil_quality(self, soil: SoilComponent) -> float:
        """从土壤属性计算质量"""
        # pH 适宜度（6.0-7.5 最佳）
        ph_factor = max(0.0, 1.0 - abs(soil.ph - 6.75) / 2.0)

        # 养分因子
        nutrient_factor = min(1.0, (soil.nitrogen + soil.phosphorus + soil.potassium) / 200.0)

        # 有机质因子
        organic_factor = min(1.0, soil.organic_matter / 5.0)

        # 湿度因子（当前湿度 vs 适宜湿度）
        moisture_factor = 1.0 - abs(soil.moisture - 0.5) * 2.0

        return (ph_factor + nutrient_factor + organic_factor + moisture_factor) / 4.0

    def _get_season(self, day_of_year: int) -> str:
        """从日期获取季节"""
        if day_of_year < 80:
            return "spring"
        elif day_of_year < 172:
            return "summer"
        elif day_of_year < 266:
            return "autumn"
        else:
            return "winter"


class HarvestSystem(System):
    """
    收割系统

    处理收割行为，计算产量，记录知识。
    """

    tick_interval = 1

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理 HARVEST 动作"""
        from core.components.action_component import ActionComponent, ActionType, ActionStatus
        from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
        from human.components.economic.inventory.inventory_component import InventoryComponent

        for entity, (action, task, inventory) in world.get_components(
            ActionComponent, TaskComponent, InventoryComponent
        ):
            if action.current_action != ActionType.HARVEST:
                continue

            self._process_harvest(world, entity, action, task, inventory)

    def _process_harvest(
        self, world, entity, action, task, inventory
    ) -> None:
        """处理单个收割行为"""
        from core.components.action_component import ActionStatus
        from human.components.cognitive.task_component import TaskStatus

        # 获取目标农田
        target_id = action.target_entity
        if target_id is None:
            self._fail(action, task, "无目标农田")
            return

        target_entity = world.query_entity(target_id)
        if target_entity is None:
            self._fail(action, task, "目标不存在")
            return

        farm = world.get_component(target_entity, FarmPlotComponent)
        if farm is None:
            self._fail(action, task, "目标不是农田")
            return

        # 检查是否可收割
        if not farm.can_harvest():
            self._fail(action, task, "作物未成熟")
            return

        # 计算产量
        yield_amount = farm.calculate_yield()

        # 记录农业知识
        knowledge = world.get_component(entity, FarmingKnowledgeComponent)
        if knowledge:
            soil = world.get_component(target_entity, SoilComponent)
            soil_type = soil.soil_type if soil else "unknown"
            time = world.get_time()
            season = self._get_season(time.day_of_year) if time else "unknown"

            knowledge.record_planting(
                crop_type=farm.crop_type,
                soil_type=soil_type,
                season=season,
                yield_amount=yield_amount,
                success=True,
            )

        # 重置农田
        farm.crop_type = None
        farm.growth_stage = 0.0
        farm.health = 1.0
        farm.yield_history.append(yield_amount)
        
        # 限制历史大小防止内存泄漏
        if len(farm.yield_history) > 100:
            farm.yield_history = farm.yield_history[-100:]

        # 标记完成
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE
        action.progress = 1.0

        logger.debug(
            f"[Harvest] E{entity.id} 收割了 {yield_amount:.2f} 单位作物"
        )

    def _fail(self, action, task, reason: str) -> None:
        """标记失败"""
        from core.components.action_component import ActionStatus
        from human.components.cognitive.task_component import TaskStatus

        action.status = ActionStatus.FAILED
        task.status = TaskStatus.FAILED
        action.progress = 0.0
        logger.debug(f"[Harvest] 失败: {reason}")

    def _get_season(self, day_of_year: int) -> str:
        if day_of_year < 80:
            return "spring"
        elif day_of_year < 172:
            return "summer"
        elif day_of_year < 266:
            return "autumn"
        else:
            return "winter"


class IrrigationSystem(System):
    """
    灌溉系统

    管理水源和灌溉行为。
    """

    tick_interval = 10

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新灌溉系统"""
        # 处理 IRRIGATE 动作
        from core.components.action_component import ActionComponent, ActionType

        for entity, (action,) in world.get_components(ActionComponent):
            if action.current_action != ActionType.DRINK:  # 复用 DRINK 或新增 IRRIGATE
                continue

            # 简化为自动灌溉逻辑
            pass

    def find_water_source(
        self, world: World, x: float, y: float, radius: float = 10.0
    ) -> Optional[int]:
        """查找附近水源"""
        from space.space_component import SpaceComponent
        from resource.water.components.water_component import WaterComponent

        best_source = None
        best_dist = float('inf')

        for entity, (space, water) in world.get_components(
            SpaceComponent, WaterComponent
        ):
            dist = ((space.x - x) ** 2 + (space.y - y) ** 2) ** 0.5
            if dist <= radius and dist < best_dist:
                best_dist = dist
                best_source = entity.id

        return best_source

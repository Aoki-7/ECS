#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
农场系统

提供 Farm 组件的静态操作方法。
"""

from typing import Dict, Optional
from core.system import System
from core.world import World

from civilization.components.farm_component import FarmPlotComponent, FarmingKnowledgeComponent, IrrigationComponent


class FarmSystem(System):
    """农场系统"""
    tick_interval = 20

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新农场生长"""
        for entity, farm in world.get_components(FarmPlotComponent):
            if isinstance(farm, list):
                farm = farm[0]
            FarmPlotSystem.update_growth(farm, dt, {"temperature": 20.0, "light": 0.7, "moisture": 0.5})

    def _calculate_soil_quality(self, soil) -> float:
        """计算土壤质量"""
        return 0.5

    def _get_season(self, tick: int) -> str:
        """获取季节"""
        day = tick % 365
        if day < 80:
            return "spring"
        elif day < 172:
            return "summer"
        elif day < 266:
            return "autumn"
        else:
            return "winter"


class HarvestSystem(System):
    """收割系统"""
    tick_interval = 50

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理收割"""
        for entity, farm in world.get_components(FarmPlotComponent):
            if isinstance(farm, list):
                farm = farm[0]
            if FarmPlotSystem.can_harvest(farm):
                farm.yield_history.append({
                    'crop_type': farm.crop_type,
                    'yield_amount': FarmPlotSystem.calculate_yield(farm),
                    'tick': getattr(world, 'tick', 0),
                })
                farm.growth_stage = 0.0
                farm.crop_type = None
                farm.is_planted = False
                farm.is_harvestable = False
                farm.last_harvest_tick = getattr(world, 'tick', 0)


class FarmPlotSystem:
    """农田地块系统 - 静态方法操作 FarmPlotComponent"""

    @staticmethod
    def can_harvest(farm: FarmPlotComponent) -> bool:
        """是否可以收割"""
        return farm.crop_type is not None and farm.growth_stage >= 0.9

    @staticmethod
    def calculate_yield(farm: FarmPlotComponent) -> float:
        """计算产量"""
        if farm.crop_type is None:
            return 0.0
        base_yield = farm.soil_quality * 0.5
        growth_bonus = farm.growth_stage * 0.5
        return min(1.0, base_yield + growth_bonus)

    @staticmethod
    def update_growth(farm: FarmPlotComponent, dt: float, conditions: Dict) -> None:
        """更新生长阶段"""
        if farm.crop_type is None:
            return
        
        temp = conditions.get("temperature", 20.0)
        light = conditions.get("light", 0.5)
        moisture = conditions.get("moisture", 0.5)
        
        growth_rate = 0.01 * dt
        if 15 <= temp <= 25:
            growth_rate *= 1.5
        growth_rate *= light
        growth_rate *= moisture
        
        farm.growth_stage = min(1.0, farm.growth_stage + growth_rate)
        farm.is_harvestable = farm.growth_stage >= 0.9


class FarmingKnowledgeSystem:
    """农业知识系统 - 静态方法操作 FarmingKnowledgeComponent"""

    @staticmethod
    def record_planting(
        knowledge: FarmingKnowledgeComponent,
        crop_type: str, soil_type: str, season: str,
        yield_amount: float, success: bool,
    ) -> None:
        """记录种植经验"""
        if crop_type not in knowledge.planting_techniques:
            knowledge.planting_techniques[crop_type] = 0.0
        knowledge.planting_techniques[crop_type] += 0.1

    @staticmethod
    def get_best_crop_for_conditions(
        knowledge: FarmingKnowledgeComponent,
        soil_type: str, season: str,
    ) -> Optional[str]:
        """获取最佳作物"""
        if not knowledge.known_crops:
            return None
        return knowledge.known_crops[0]

    @staticmethod
    def suggest_irrigation_level(knowledge: FarmingKnowledgeComponent) -> float:
        """建议灌溉水平"""
        return 0.5


class IrrigationSystem:
    """灌溉系统 - 静态方法操作 IrrigationComponent"""

    @staticmethod
    def irrigate(
        irrigation: IrrigationComponent,
        farm: FarmPlotComponent,
        amount: float,
    ) -> float:
        """灌溉"""
        actual = amount * irrigation.efficiency
        farm.moisture = min(1.0, farm.moisture + actual)
        farm.water_level = farm.moisture
        farm.irrigated_this_cycle = True
        return actual

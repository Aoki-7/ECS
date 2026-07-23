#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/nutrient_system.py
@说明:营养系统

职责：
    - 计算营养胁迫程度
    - 从环境吸收营养
    - 消耗营养（生长、修复）
"""

from core.system import System
from core.world import World

from biology.components.nutrient_component import NutrientComponent


class NutrientSystem(System):
    """营养系统"""

    tick_interval = 5

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新营养状态"""
        for entity, (nutrient,) in world.get_components(NutrientComponent):
            # 计算营养胁迫
            nitrogen_stress = self._calculate_stress(nutrient.nitrogen, nutrient.max_nitrogen)
            phosphorus_stress = self._calculate_stress(nutrient.phosphorus, nutrient.max_phosphorus)
            potassium_stress = self._calculate_stress(nutrient.potassium, nutrient.max_potassium)

            # 可以在这里添加营养吸收和消耗逻辑
            # 例如：从土壤吸收、用于生长等

    def _calculate_stress(self, current: float, max_value: float) -> float:
        """计算胁迫程度（0-1）"""
        if max_value <= 0:
            return 0.0
        return 1.0 - (current / max_value)

    def get_nitrogen_stress(self, nutrient: NutrientComponent) -> float:
        """获取氮胁迫程度"""
        return self._calculate_stress(nutrient.nitrogen, nutrient.max_nitrogen)

    def get_phosphorus_stress(self, nutrient: NutrientComponent) -> float:
        """获取磷胁迫程度"""
        return self._calculate_stress(nutrient.phosphorus, nutrient.max_phosphorus)

    def get_potassium_stress(self, nutrient: NutrientComponent) -> float:
        """获取钾胁迫程度"""
        return self._calculate_stress(nutrient.potassium, nutrient.max_potassium)
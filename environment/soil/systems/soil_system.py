# AI Generated
"""
土壤系统
处理土壤湿度和养分的动态变化
"""

from core.system import System
from core.world import World
from environment.soil.components.soil_component import SoilComponent


class SoilSystem(System):
    """
    土壤系统

    负责更新土壤状态：
    - 土壤湿度变化（蒸发、渗透）
    - 养分循环
    - 温度变化
    """

    def __init__(self):
        super().__init__()
        self.priority = 10

    def update(self, world: World, delta_hours: float):
        """
        更新所有土壤组件
        """
        # 遍历所有拥有SoilComponent的实体
        for entity, (soil,) in world.get_components(SoilComponent):
            self._update_soil(soil, delta_hours)

    def _update_soil(self, soil: SoilComponent, delta_hours: float):
        """
        更新单个土壤组件
        """
        # 1. 土壤湿度变化
        # 简单模型：自然蒸发
        evaporation_rate = 0.01 * delta_hours  # 每小时蒸发1%
        soil.moisture = max(
            soil.wilting_point,
            min(soil.saturation, soil.moisture - evaporation_rate)
        )

        # 2. 土壤温度变化
        # 简单模型：趋向环境温度
        # 假设环境温度为20°C
        target_temp = 20.0
        temp_change_rate = 0.1 * delta_hours
        soil.temperature += (target_temp - soil.temperature) * temp_change_rate

        # 3. 养分自然消耗
        nutrient_decay = 0.001 * delta_hours
        soil.nitrogen *= (1 - nutrient_decay)
        soil.phosphorus *= (1 - nutrient_decay)
        soil.potassium *= (1 - nutrient_decay)

        # 4. pH值自然变化
        # 趋向中性(pH=7)
        ph_change_rate = 0.01 * delta_hours
        if soil.ph < 7.0:
            soil.ph = min(7.0, soil.ph + ph_change_rate)
        elif soil.ph > 7.0:
            soil.ph = max(7.0, soil.ph - ph_change_rate)

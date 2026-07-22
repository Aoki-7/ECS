#!/usr/bin/env python3
"""
养分循环系统 v4.16.0
实现碳、氮、磷的生物地球化学循环，完善生态物质循环闭环
"""

import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.physics_weather.components.temperature_component import TemperatureComponent
from plant.components.plant_component import PlantComponent
from biology.components.corpse_component import CorpseComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class NutrientCycleSystem(System):
    """
    养分循环系统
    处理土壤中碳、氮、磷的形态转化与循环过程
    """

    tick_interval = 20  # 每20tick执行一次
    priority = 135  # 在尸体分解系统之后，植物生长系统之前运行

    # 氮循环参数
    AMMONIFICATION_RATE = 0.02  # 氨化作用速率：有机氮转化为铵态氮的比例每小时
    NITRIFICATION_RATE = 0.03  # 硝化作用速率：铵态氮转化为硝态氮的比例每小时
    DENITRIFICATION_RATE = 0.01  # 反硝化作用速率：硝态氮转化为气态氮流失的比例每小时
    NITROGEN_FIXATION_RATE = 0.005  # 固氮作用速率：微生物固氮量每小时
    PLANT_NITROGEN_UPTAKE_RATIO = 0.7  # 植物吸收氮中70%是硝态氮，30%是铵态氮

    # 磷循环参数
    ORGANIC_PHOSPHORUS_MINERALIZATION_RATE = 0.01  # 有机磷矿化速率每小时
    PHOSPHORUS_FIXATION_RATE = 0.02  # 磷固定速率：有效磷转化为无效磷的比例每小时
    
    # 有机质分解参数
    ORGANIC_MATTER_DECOMPOSITION_RATE = 0.005  # 有机质分解速率每小时
    DECOMPOSITION_TEMP_OPTIMAL = 30.0  # 微生物最适温度
    DECOMPOSITION_MOISTURE_OPTIMAL = 0.6  # 微生物最适湿度

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        if not world_env:
            return
        
        global_temp = world_env.temperature  # 气温 °C

        # 遍历所有土壤网格
        for entity, soil, temp_comp, space in world.query(
            SoilComponent,
            TemperatureComponent,
            SpaceComponent
        ):
            # 计算微生物活性因子（温度和湿度共同影响）
            temp_factor = self._calculate_temp_factor(temp_comp.get_average_soil_temperature(0.5))
            moisture_factor = self._calculate_moisture_factor(soil.moisture)
            microbial_factor = temp_factor * moisture_factor * soil.microbial_activity
            
            if microbial_factor <= 0.01:
                # 微生物活性极低，跳过循环
                continue
            
            # ============== 碳循环：有机质分解 ==============
            om_decompose_amount = soil.organic_matter * self.ORGANIC_MATTER_DECOMPOSITION_RATE * microbial_factor * dt / 3600.0
            soil.organic_matter = max(0.1, soil.organic_matter - om_decompose_amount)
            
            # 有机质分解释放养分
            released_n = om_decompose_amount * 10  # 有机质含氮量约1%，转换为mg/kg
            released_p = om_decompose_amount * 2   # 有机质含磷量约0.2%
            soil.nitrogen_organic += released_n
            soil.phosphorus_organic += released_p
            
            # 分解产生CO2释放到大气（暂时省略）
            # 同时增加微生物生物量
            soil.microbial_biomass += om_decompose_amount * 0.1

            # ============== 氮循环 ==============
            # 1. 氨化作用：有机氮 → 铵态氮
            ammonification_amount = soil.nitrogen_organic * self.AMMONIFICATION_RATE * microbial_factor * dt / 3600.0
            soil.nitrogen_organic -= ammonification_amount
            soil.nitrogen_ammonium += ammonification_amount
            
            # 2. 硝化作用：铵态氮 → 硝态氮（需要氧气，湿度小于0.8时有效）
            if soil.moisture < 0.8:
                nitrification_amount = soil.nitrogen_ammonium * self.NITRIFICATION_RATE * microbial_factor * dt / 3600.0
                soil.nitrogen_ammonium -= nitrification_amount
                soil.nitrogen_nitrate += nitrification_amount
            
            # 3. 反硝化作用：硝态氮 → 气态氮流失（缺氧条件，湿度大于0.8时发生）
            if soil.moisture >= 0.8:
                denitrification_amount = soil.nitrogen_nitrate * self.DENITRIFICATION_RATE * microbial_factor * dt / 3600.0
                soil.nitrogen_nitrate -= denitrification_amount
            
            # 4. 生物固氮：微生物将气态氮转化为有机氮
            fixation_amount = self.NITROGEN_FIXATION_RATE * microbial_factor * dt / 3600.0 * 10  # mg/kg
            soil.nitrogen_organic += fixation_amount
            
            # ============== 磷循环 ==============
            # 1. 有机磷矿化：有机磷 → 有效磷
            mineralization_amount = soil.phosphorus_organic * self.ORGANIC_PHOSPHORUS_MINERALIZATION_RATE * microbial_factor * dt / 3600.0
            soil.phosphorus_organic -= mineralization_amount
            soil.phosphorus_available += mineralization_amount
            
            # 2. 磷固定：有效磷 → 被土壤吸附固定为无效磷（暂时计入有机磷）
            fixation_amount = soil.phosphorus_available * self.PHOSPHORUS_FIXATION_RATE * (1 - soil.ph / 7.0) * dt / 3600.0
            fixation_amount = max(0.0, fixation_amount)  # 中性土壤固定最少，酸性/碱性土壤固定多
            soil.phosphorus_available -= fixation_amount
            soil.phosphorus_organic += fixation_amount
            
            # ============== 同步总养分值，保持旧API兼容 ==============
            soil._sync_total_nutrients()
            
            # ============== 植物养分吸收（在植物生长系统之前补充） ==============
            self._process_plant_uptake(world, space.x, space.y, soil, dt)

    def _calculate_temp_factor(self, soil_temp: float) -> float:
        """计算温度对微生物活性的影响"""
        if soil_temp <= 0 or soil_temp >= 50:
            return 0.01
        # 温度响应曲线：最适30°C
        if soil_temp <= self.DECOMPOSITION_TEMP_OPTIMAL:
            return (soil_temp / self.DECOMPOSITION_TEMP_OPTIMAL)**2
        else:
            return max(0.01, 1.0 - (soil_temp - self.DECOMPOSITION_TEMP_OPTIMAL) / (50.0 - self.DECOMPOSITION_TEMP_OPTIMAL))

    def _calculate_moisture_factor(self, moisture: float) -> float:
        """计算湿度对微生物活性的影响"""
        if moisture <= 0.05 or moisture >= 0.95:
            return 0.01
        # 湿度响应曲线：最适60%
        if moisture <= self.DECOMPOSITION_MOISTURE_OPTIMAL:
            return moisture / self.DECOMPOSITION_MOISTURE_OPTIMAL
        else:
            return max(0.1, 1.0 - (moisture - self.DECOMPOSITION_MOISTURE_OPTIMAL) / (1.0 - self.DECOMPOSITION_MOISTURE_OPTIMAL))

    def _process_plant_uptake(self, world: World, x: float, y: float, soil: SoilComponent, dt: float) -> None:
        """处理当前位置植物的养分吸收"""
        # 查找当前位置的植物
        for e, plant, s in world.query(PlantComponent, SpaceComponent):
            if round(s.x) != round(x) or round(s.y) != round(y):
                continue
            if not hasattr(plant, 'growth_rate') or plant.growth_rate <= 0:
                continue
            
            # 植物生长需要吸收氮磷钾
            # 按生长速率比例吸收
            uptake_n = plant.growth_rate * 0.02 * dt / 3600.0  # 每单位生长吸收20mg/kg氮
            uptake_p = plant.growth_rate * 0.005 * dt / 3600.0 # 吸收5mg/kg磷
            
            # 优先吸收有效态养分
            # 氮：70%硝态氮，30%铵态氮
            uptake_nitrate = min(uptake_n * self.PLANT_NITROGEN_UPTAKE_RATIO, soil.nitrogen_nitrate)
            remaining_n = uptake_n - uptake_nitrate
            uptake_ammonium = min(remaining_n, soil.nitrogen_ammonium)
            
            # 实际吸收量
            actual_n = uptake_nitrate + uptake_ammonium
            actual_p = min(uptake_p, soil.phosphorus_available)
            
            # 扣除土壤养分
            soil.nitrogen_nitrate -= uptake_nitrate
            soil.nitrogen_ammonium -= uptake_ammonium
            soil.phosphorus_available -= actual_p
            
            # 植物未吸收的部分不影响，继续保留在土壤中
            soil._sync_total_nutrients()
            break

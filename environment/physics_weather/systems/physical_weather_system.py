#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物理天气演化系统

【核心思想】
天气由连续物理量（温度、气压、湿度、云量、降水、风速）的自然演化决定，
离散天气状态（多云、小雨等）由物理量实时推导，而非通过状态机切换。

【物理模型】
1. 温度: 日循环（正弦波）+ 季节偏置 + 云量阻尼 + 随机噪声
2. 气压: 长周期波（天气系统通过）+ 年周期 + 噪声
3. 绝对湿度: 蒸发增加 + 降水消耗 + 平流回归
4. 相对湿度: 从绝对湿度和温度实时计算
5. 云量: 相对湿度驱动（含滞后效应）+ 气团上升贡献
6. 降水: 云量+湿度超阈值触发，消耗水汽
7. 风速: 气压梯度驱动 + 随机变化 + 回归基线

v3.9 变更：
- 6 大物理量更新拆分为独立处理器类
- 便于单元测试和物理模型替换
"""

import math
import random

from core.world import World
from core.system import System

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.config.physics_constants import (
    saturation_absolute_humidity,
    relative_humidity,
)
from environment.season.season_component import SeasonComponent
from environment.season.season_state import seasonal_insolation_factor, earth_sun_distance_factor
from environment.climate.climate_component import ClimateComponent

from .weather_processors import (
    TemperatureProcessor,
    PressureProcessor,
    HumidityProcessor,
    CloudCoverProcessor,
    PrecipitationProcessor,
    WindSpeedProcessor,
)


class PhysicalWeatherSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    物理天气演化系统

    每步更新所有连续物理量，模拟真实大气物理过程。
    可与 SeasonComponent 耦合（可选），也可以独立运行。
    """

    def __init__(self, latitude: float = 35.0, elevation: float = 0.0):
        super().__init__()
        self.latitude = latitude
        self.elevation = elevation

        # 初始化处理器
        self._processors = [
            TemperatureProcessor(latitude, elevation),
            PressureProcessor(),
            HumidityProcessor(),
            CloudCoverProcessor(),
            PrecipitationProcessor(),
            WindSpeedProcessor(),
        ]

    def update(self, world: World, dt: float = 1.0) -> None:
        """主更新：对所有 PhysicalWeatherComponent 执行物理演化"""
        # 获取世界时间
        time = world.get_time()
        hour = time.hour if time else 12.0
        day_of_year = time.day_of_year if time else 1
        total_hours = time.total_hours if time else 0.0

        # 获取季节和气候（可选）
        # 防御：使用 world.get_world_component 替代 entity.get_component
        season = world.get_world_component(SeasonComponent)
        climate = world.get_world_component(ClimateComponent)

        # 季节因子
        seasonal_temp_offset = 0.0
        rainfall_factor = 1.0
        climate_humidity_bias = 0.0

        if season is not None:
            # 从年份进度推导季节因子
            year_fraction = season.year_progress / season.year_length_hours if season.year_length_hours > 0 else 0.5
            # 夏季(0.5)温度高，冬季(0.0/1.0)温度低
            seasonal_temp_offset = 10.0 * math.sin(2.0 * math.pi * (year_fraction - 0.25))
            rainfall_factor = 1.0 + 0.3 * math.sin(2.0 * math.pi * year_fraction)

        if climate is not None:
            seasonal_temp_offset += getattr(climate, 'temperature_offset', 0.0)
            rainfall_factor *= getattr(climate, 'rainfall_multiplier', 1.0)
            climate_humidity_bias = getattr(climate, 'humidity_bias', 0.0)

        # 遍历所有天气组件
        for entity, (weather,) in world.get_components(PhysicalWeatherComponent):
            self._update_weather(
                weather, dt, hour, day_of_year, total_hours,
                seasonal_temp_offset, rainfall_factor, climate_humidity_bias,
                world
            )

    def _update_weather(
        self,
        weather: PhysicalWeatherComponent,
        dt: float,
        hour: float,
        day_of_year: int,
        total_hours: float,
        seasonal_temp_offset: float,
        rainfall_factor: float,
        climate_humidity_bias: float,
        world: World,
    ) -> None:
        """更新单个天气组件"""
        # 顺序执行 6 大物理过程
        for processor in self._processors:
            processor.process(
                weather, dt,
                hour=hour,
                day_of_year=day_of_year,
                total_hours=total_hours,
                temp_offset=seasonal_temp_offset,
                rainfall_factor=rainfall_factor,
                climate_humidity_bias=climate_humidity_bias,
                world=world,
            )

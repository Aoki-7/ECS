#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气 Modifier 桥接系统

【作用】
    老版 WeatherSystem 中直接消费 WeatherModifierComponent 的增量修正
    （极端天气事件生成的 temp_delta / humidity_delta / rainfall_delta），
    新版 PhysicalWeatherSystem 聚焦物理演化，不关心 modifier 层，
    由本系统作为独立薄层读取 modifier 并应用到 PhysicalWeatherComponent。

【数据流】
    WeatherEventFactory
        → 创建实体含 WeatherModifierComponent
        → 本系统每步迭代 modifier，写入 PhysicalWeatherComponent
        → PhysicalWeatherSystem 负责物理演化（不关心 modifier 来源）

【运行顺序】
    应在 PhysicalWeatherSystem 之后运行，让 modifier 在物理演化基础上叠加。
"""

from core.world import World
from core.system import System

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.components.weather_event_components import (
    WeatherModifierComponent,
)


class WeatherModifierBridgeSystem(System):
    """
    天气 Modifier → PhysicalWeatherComponent 桥接

    将极端天气事件产生的物理量增量修正写入 PhysicalWeatherComponent。
    """

    def update(self, world: World, delta_hours: float):
        # ── 获取世界级物理天气组件 ──
        weather = world._world_entity.get_component(PhysicalWeatherComponent)
        if weather is None:
            return

        # ── 遍历所有活动的 modifier ──
        for entity, (modifier,) in world.get_components(WeatherModifierComponent):
            modifier: WeatherModifierComponent

            # 温度修正
            weather.temperature += modifier.temp_delta * (delta_hours / modifier.duration_hours)

            # 湿度修正（绝对湿度增量）
            weather.absolute_humidity += modifier.humidity_delta * (delta_hours / modifier.duration_hours)
            weather.absolute_humidity = max(0.1, min(35.0, weather.absolute_humidity))

            # 降水修正
            weather.precipitation_rate += modifier.rainfall_delta * (delta_hours / modifier.duration_hours)
            weather.precipitation_rate = max(0.0, weather.precipitation_rate)

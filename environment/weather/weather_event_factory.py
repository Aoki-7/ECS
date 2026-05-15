
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_event_factory.py
@说明:
@时间:2026/03/05 12:51:34
@作者:Sherry
@版本:1.0
'''




import random


from core.world import World
from environment.weather.components.weather_modifier_component import WeatherEventTagComponent, LifetimeComponent, WeatherModifierComponent


class WeatherEventTemplates:
    """
    极端天气事件模板

    每个模板定义：
    - duration: 持续时间范围（小时）
    - temp: 温度变化范围（摄氏度，相对当前温度）
    - humidity: 湿度变化范围（百分比，相对当前湿度）
    - rainfall: 降雨量变化范围（毫米/小时，相对当前降雨量）

    支持的事件类型：
    cold_wave:    寒潮 — 温度骤降、持续时间较长
    heat_wave:    热浪 — 温度骤升、伴干旱
    storm:        风暴 — 强降水、短时高影响
    drought:      干旱 — 长期无雨、湿度剧降
    typhoon:      台风 — 强风暴雨、短时高影响
    snowstorm:    暴雪 — 极寒降雪、能见度骤降
    """
    TEMPLATES = {
        "cold_wave": {
            "duration": (6, 24),
            "temp": (-10.0, -3.0),
            "humidity": (0.0, 0.2),
            "rainfall": (0.0, 2.0),
        },
        "heat_wave": {
            "duration": (6, 24),
            "temp": (3.0, 10.0),
            "humidity": (-0.2, 0.0),
            "rainfall": (0.0, 1.0),
        },
        "storm": {
            "duration": (3, 12),
            "temp": (-2.0, 2.0),
            "humidity": (0.2, 0.5),
            "rainfall": (5.0, 20.0),
        },
        "drought": {
            "duration": (24, 72),
            "temp": (2.0, 6.0),
            "humidity": (-0.5, -0.2),
            "rainfall": (-5.0, -1.0),
        },
        "typhoon": {
            "duration": (3, 18),
            "temp": (-1.0, 1.0),
            "humidity": (0.3, 0.6),
            "rainfall": (10.0, 50.0),
        },
        "snowstorm": {
            "duration": (3, 12),
            "temp": (-15.0, -5.0),
            "humidity": (0.1, 0.3),
            "rainfall": (3.0, 10.0),
        },
    }



class WeatherEventFactory:

    def __init__(self, world: World):
        self.world = world

    def create_event(self, event_type: str):

        if event_type not in WeatherEventTemplates.TEMPLATES:
            raise ValueError(f"Unknown weather event type: {event_type}")

        tpl = WeatherEventTemplates.TEMPLATES[event_type]

        duration = random.uniform(*tpl["duration"])
        temp_delta = random.uniform(*tpl["temp"])
        humidity_delta = random.uniform(*tpl["humidity"])
        rainfall_delta = random.uniform(*tpl["rainfall"])

        # 创建实体
        entity = self.world.create_entity()

        self.world.add_component(
            entity,
            WeatherEventTagComponent(event_type=event_type)
        )

        # 挂载组件
        self.world.add_component(
            entity,
            WeatherModifierComponent(
                duration_hours=duration,
                temp_delta=temp_delta,
                humidity_delta=humidity_delta,
                rainfall_delta=rainfall_delta
            )
        )

        self.world.add_component(
            entity,
            LifetimeComponent(remaining_hours=duration)
        )
        
        return entity

    def create_random_event(self):
        """
        随机生成一个天气事件
        """
        event_type = random.choice(
            list(WeatherEventTemplates.TEMPLATES.keys())
        )
        return self.create_event(event_type)

    def spawn_batch(self, count: int):
        """
        批量生成天气事件
        """
        if count <= 0:
            raise ValueError("Batch count must be positive.")

        entities = []
        for _ in range(count):
            entities.append(self.create_random_event())

        return entities
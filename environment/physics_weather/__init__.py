"""
物理天气子模块 — 连续物理量天气系统

依赖:
    - environment/
    - core/

版本: v4.0
"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物理天气模块 — 纯物理量驱动的天气系统

【核心理念】
天气由连续物理量（温度、气压、湿度、云量、降水速率、风速）的自然演化决定。
离散天气状态标签（晴/多云/小雨等）由物理量「实时推导」而非「存储」。

与现有 weather 模块的区别：
    weather/           → 半马尔可夫链 + 状态机（离散状态为主）
    physics_weather/   → 纯物理演化 + 状态推导（连续物理量为主）

【模块结构】
    components/
        physical_weather_component.py   — 纯数据：仅存连续物理量
    systems/
        physical_weather_system.py      — 演化逻辑：更新所有物理量
    config/
        physics_constants.py            — 物理常数与可调参数
        weather_thresholds.py           — 天气状态分类阈值与枚举
    utils/
        weather_classifier.py           — 从物理量推导天气标签

【使用示例】
    from environment.physics_weather import (
        PhysicalWeatherComponent,
        PhysicalWeatherSystem,
        classify, DerivedWeatherState,
    )

    # 挂载组件
    world.get_world_entity().add_component(PhysicalWeatherComponent())

    # 创建并注册系统
    weather_system = PhysicalWeatherSystem(latitude=35.0)
    world.add_system(weather_system)

    # 每步更新
    weather_system.update(world, delta_hours=1.0)

    # 获取物理量
    wc = world.get_world_entity().get_component(PhysicalWeatherComponent)

    # 推导天气状态
    state = classify_from_component(wc)
"""

# ── 组件 ──
from .components.physical_weather_component import PhysicalWeatherComponent

# ── 系统 ──
from .systems.physical_weather_system import PhysicalWeatherSystem

# ── 分类器 ──
from .utils.weather_classifier import (
    classify,
    classify_from_component,
    classify_cloud_cover,
    classify_precipitation_type,
    classify_precipitation_intensity,
    classify_wind_level,
    classify_visibility,
    DerivedWeatherState,
)

# ── 配置枚举 ──
from .config.weather_thresholds import (
    CloudCoverLevel,
    PrecipitationType,
    PrecipitationIntensity,
    WindLevel,
    VisibilityState,
)

# ── 物理函数 ──
from .config.physics_constants import (
    saturation_vapor_pressure,
    saturation_absolute_humidity,
    relative_humidity,
)

__all__ = [
    # 组件
    "PhysicalWeatherComponent",
    # 系统
    "PhysicalWeatherSystem",
    # 分类器
    "classify",
    "classify_from_component",
    "classify_cloud_cover",
    "classify_precipitation_type",
    "classify_precipitation_intensity",
    "classify_wind_level",
    "classify_visibility",
    "DerivedWeatherState",
    # 枚举
    "CloudCoverLevel",
    "PrecipitationType",
    "PrecipitationIntensity",
    "WindLevel",
    "VisibilityState",
    # 物理函数
    "saturation_vapor_pressure",
    "saturation_absolute_humidity",
    "relative_humidity",
]


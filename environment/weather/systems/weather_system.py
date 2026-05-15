#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_system.py
@说明:天气基础系统
@时间:2026/04/22 14:03:41
@作者:Sherry
@版本:1.0
'''



import random
import math

from core.world import World
from core.system import System

from environment.weather.components.weather_component import WeatherComponent
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.season.season_component import SeasonComponent
from environment.weather.components.weather_modifier_component import WeatherModifierComponent

from environment.weather.config.weather_types import *
from environment.weather.config.weather_transition import *


class WeatherSystem(System):

    def __init__(self):
        self.temp_noise = 0.0

    def update(self, world: World, delta_hours: float):

        time = world.get_time()

        weather, atm, season = world._world_entity.get_components(
            WeatherComponent,
            AtmosphereComponent,
            SeasonComponent
        )
        if not weather or not atm or not season:
            return

        # ======================
        # 1️⃣ 多维状态更新（半马尔可夫）
        # ======================

        self._update_dimension(weather, "sky", "sky_remaining_hours",
                               SKY_TRANSITIONS, SKY_DURATION, delta_hours)

        self._update_dimension(weather, "precipitation_type", "precipitation_type_remaining_hours",
                               PRECIPITATION_TYPE_TRANSITIONS, PRECIPITATION_DURATION, delta_hours)

        self._update_dimension(weather, "precipitation_intensity", "precipitation_intensity_remaining_hours",
                               PRECIPITATION_INTENSITY_TRANSITIONS, PRECIPITATION_DURATION, delta_hours)

        self._update_dimension(weather, "visibility", "visibility_remaining_hours",
                               VISIBILITY_TRANSITIONS, FOG_DURATION, delta_hours)

        self._update_dimension(weather, "wind", "wind_remaining_hours",
                               WIND_TRANSITIONS, WIND_DURATION, delta_hours)

        self._update_dimension(weather, "extreme", "extreme_remaining_hours",
                               EXTREME_TRANSITIONS, EXTREME_DURATION, delta_hours)

        # ======================
        # 2️⃣ 约束层（关键）
        # ======================

        self._apply_constraints(weather, atm)

        # ======================
        # 3️⃣ 天气效果计算
        # ======================

        rainfall, sunlight_factor, humidity = self._compute_weather_effect(weather)

        weather.rainfall = rainfall
        atm.humidity = humidity

        # ======================
        # 4️⃣ 温度系统（原逻辑）
        # ======================

        self.temp_noise += random.uniform(-0.4, 0.4)
        self.temp_noise *= 0.96

        base_temp = 18 + season.temperature_offset

        hour = time.hour
        diurnal_phase = (hour - 14) / 24 * math.pi * 2

        base_diurnal_range = 8
        humidity_factor = 1 - atm.humidity * 0.6
        diurnal_range = base_diurnal_range * humidity_factor

        diurnal_temp = math.sin(diurnal_phase) * diurnal_range

        temperature = base_temp + diurnal_temp + self.temp_noise

        # ======================
        # 5️⃣ 光照
        #    基础 sunlight 由 CloudSystem 根据云量物理量计算，
        #    WeatherSystem 仅应用季节修正，不覆盖 base 值。
        # ======================

        weather.sunlight *= season.sunlight_factor
        weather.rainfall *= season.rainfall_factor

        # ======================
        # 6️⃣ Modifier
        # ======================

        for _, (modifier,) in world.get_components(WeatherModifierComponent):
            temperature += modifier.temp_delta
            atm.humidity += modifier.humidity_delta
            weather.rainfall += modifier.rainfall_delta

        # ======================
        # 7️⃣ 写回
        # ======================

        weather.temperature = temperature

    # =========================================================
    # 通用维度更新（半马尔可夫）
    # =========================================================

    def _update_dimension(self, weather, attr, timer_attr,
                          transitions, duration_map, delta_hours):

        remaining = getattr(weather, timer_attr, 0)
        remaining -= delta_hours

        if remaining <= 0:
            current = getattr(weather, attr)

            next_state = self._sample(transitions[current])

            setattr(weather, attr, next_state)

            dur = duration_map.get(next_state, (2, 6))
            remaining = random.uniform(*dur)

        setattr(weather, timer_attr, remaining)

    def _sample(self, transition_dict):
        states = list(transition_dict.keys())
        probs = list(transition_dict.values())
        return random.choices(states, weights=probs, k=1)[0]

    # =========================================================
    # 约束层（核心：保证物理一致性）
    # =========================================================

    def _apply_constraints(self, weather: WeatherComponent, atm: AtmosphereComponent):

        # ☀ 晴天 → 禁止降水
        if weather.sky == SkyState.CLEAR:
            weather.precipitation_type = PrecipitationType.NONE
            weather.precipitation_intensity = PrecipitationIntensity.NONE

        # 🌧 无降水 → 强度归零
        if weather.precipitation_type == PrecipitationType.NONE:
            weather.precipitation_intensity = PrecipitationIntensity.NONE

        # 🌫 低湿度 → 禁止浓雾
        if atm.humidity < 0.6 and weather.visibility == VisibilityState.DENSE_FOG:
            weather.visibility = VisibilityState.FOG

        # 🌧 云量影响降水（关键耦合）
        if weather.sky in (SkyState.CLEAR, SkyState.PARTLY_CLOUDY):
            if random.random() < 0.8:
                weather.precipitation_type = PrecipitationType.NONE

        # ⛈ 极端天气约束
        if weather.extreme == ExtremeWeather.THUNDERSTORM:
            weather.precipitation_type = PrecipitationType.RAIN
            weather.precipitation_intensity = PrecipitationIntensity.HEAVY
            weather.wind = WindLevel.STRONG

    # =========================================================
    # 天气 → 物理量映射
    # =========================================================

    def _compute_weather_effect(self, weather: WeatherComponent):

        rainfall = 0.0
        humidity = 0.5
        sunlight = 1.0

        # ☀ 云层影响光照
        sky_map = {
            SkyState.CLEAR: 1.0,
            SkyState.PARTLY_CLOUDY: 0.85,
            SkyState.CLOUDY: 0.65,
            SkyState.OVERCAST: 0.45,
        }
        sunlight *= sky_map[weather.sky]

        # 🌧 降水
        if weather.precipitation_type != PrecipitationType.NONE:

            intensity_map = {
                PrecipitationIntensity.LIGHT: (1, 4),
                PrecipitationIntensity.MODERATE: (4, 10),
                PrecipitationIntensity.HEAVY: (10, 30),
                PrecipitationIntensity.EXTREME: (30, 80),
            }

            low, high = intensity_map.get(weather.precipitation_intensity, (0, 0))
            rainfall = random.uniform(low, high)

            humidity += 0.2

        # 🌫 能见度
        if weather.visibility == VisibilityState.FOG:
            sunlight *= 0.7
            humidity += 0.1

        elif weather.visibility == VisibilityState.DENSE_FOG:
            sunlight *= 0.5
            humidity += 0.2

        # 💨 风（轻影响）
        if weather.wind in (WindLevel.STRONG, WindLevel.GALE):
            humidity *= 0.9  # 风大 → 吹散湿气

        return rainfall, sunlight, min(humidity, 1.0)
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气处理器模块

将 PhysicalWeatherSystem 的 6 大物理量更新拆分为独立处理器，
便于单元测试、物理模型替换和性能优化。
"""

import math
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

from core.world import World

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.config.physics_constants import (
    DIURNAL_PEAK_HOUR,
    DEFAULT_DIURNAL_RANGE,
    SEASONAL_TEMP_AMPLITUDE,
    TEMP_NOISE_STD,
    TEMP_NOISE_REGRESSION,
    CLOUD_DAMPING_FACTOR,
    STANDARD_PRESSURE,
    PRESSURE_SEASONAL_AMP,
    PRESSURE_SYNOPTIC_PERIOD_HOURS,
    PRESSURE_SYNOPTIC_AMP,
    PRESSURE_NOISE_STD,
    PRESSURE_MIN,
    PRESSURE_MAX,
    EVAPORATION_COEFFICIENT,
    PRECIPITATION_CONSUMPTION,
    HUMIDITY_ADVECTION_TIMESCALE,
    BACKGROUND_ABSOLUTE_HUMIDITY,
    ABSOLUTE_HUMIDITY_MIN,
    ABSOLUTE_HUMIDITY_MAX,
    CLOUD_FORMATION_RH_THRESHOLD,
    CLOUD_DISSIPATION_RH_THRESHOLD,
    CLOUD_FORMATION_RATE,
    CLOUD_DISSIPATION_BASE_RATE,
    CLOUD_DISSIPATION_RH_RATE,
    CLOUD_PRESSURE_DROP_RATE,
    CLOUD_MAX_GROWTH_RATE,
    CLOUD_DAYTIME_DISSIPATION_FACTOR,
    PRECIP_CLOUD_THRESHOLD,
    PRECIP_RH_THRESHOLD,
    PRECIP_BASE_RATE,
    PRECIP_HUMIDITY_DRAIN_FACTOR,
    WIND_BASELINE,
    WIND_SEASONAL_AMP,
    WIND_PRESSURE_GRADIENT_COEFF,
    WIND_NOISE_STD,
    WIND_REGRESSION_COEFF,
    WIND_MIN,
    WIND_MAX,
    saturation_absolute_humidity,
    relative_humidity,
)

logger = logging.getLogger(__name__)


class WeatherProcessor(ABC):
    """天气处理器基类"""

    @abstractmethod
    def process(self, weather: PhysicalWeatherComponent, dt: float, **kwargs) -> None:
        """执行物理量更新"""
        pass


class TemperatureProcessor(WeatherProcessor):
    """温度处理器 — 日循环 + 季节偏置 + 云量阻尼 + 噪声"""

    SEASONAL_DIURNAL_FACTOR_MIN: float = 0.6
    SEASONAL_DIURNAL_FACTOR_MAX: float = 1.0
    LATITUDE_DIURNAL_SCALE: float = 0.3
    SNOW_DIURNAL_DAMPING: float = 0.7

    def __init__(self, latitude: float = 35.0, elevation: float = 0.0):
        self.latitude = latitude
        self.elevation = elevation

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                hour: float = 12.0, day_of_year: int = 1,
                temp_offset: float = 0.0, **kwargs) -> None:
        base_temp = 18.0 + temp_offset

        # 日循环
        hour_angle = 2.0 * math.pi * (hour - DIURNAL_PEAK_HOUR) / 24.0

        # 季节因子
        seasonal_diurnal_factor = (
            self.SEASONAL_DIURNAL_FACTOR_MIN
            + (self.SEASONAL_DIURNAL_FACTOR_MAX - self.SEASONAL_DIURNAL_FACTOR_MIN)
            * 0.5 * (1.0 + math.sin(math.radians((360.0 / 365.0) * (day_of_year - 81))))
        )

        # 纬度因子
        lat_deg = abs(self.latitude)
        latitude_diurnal_factor = (
            1.0
            - self.LATITUDE_DIURNAL_SCALE * (1.0 - math.exp(-((lat_deg - 45.0) / 20.0) ** 2))
        )

        # 云量阻尼
        cloud_factor = 1.0 - CLOUD_DAMPING_FACTOR * weather.cloud_cover

        effective_range = (
            DEFAULT_DIURNAL_RANGE
            * seasonal_diurnal_factor
            * latitude_diurnal_factor
            * cloud_factor
        )

        diurnal_anomaly = (effective_range / 2.0) * math.cos(hour_angle)

        # 噪声
        weather._temp_noise *= TEMP_NOISE_REGRESSION
        weather._temp_noise += random.gauss(0, TEMP_NOISE_STD * dt)

        new_temp = base_temp + diurnal_anomaly + weather._temp_noise
        new_temp += self.elevation * -0.0065
        weather.temperature = new_temp


class PressureProcessor(WeatherProcessor):
    """气压处理器 — 年周期 + 中周期 + 噪声"""

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                hour: float = 12.0, day_of_year: int = 1, **kwargs) -> None:
        total_hours = day_of_year * 24.0 + hour

        # 年周期
        yearly_phase = 2.0 * math.pi * day_of_year / 365.0
        yearly_component = PRESSURE_SEASONAL_AMP * math.sin(yearly_phase)

        # 中周期
        synoptic_phase = 2.0 * math.pi * total_hours / PRESSURE_SYNOPTIC_PERIOD_HOURS
        synoptic_component = PRESSURE_SYNOPTIC_AMP * math.sin(
            synoptic_phase + weather._pressure_phase
        )

        noise = random.gauss(0, PRESSURE_NOISE_STD * dt)

        new_pressure = STANDARD_PRESSURE + yearly_component + synoptic_component + noise
        weather.pressure = max(PRESSURE_MIN, min(PRESSURE_MAX, new_pressure))

        weather._pressure_phase += random.uniform(-0.05, 0.05) * dt


class HumidityProcessor(WeatherProcessor):
    """湿度处理器 — 蒸发 + 降水消耗 + 平流"""

    SOIL_EVAP_FEEDBACK_RATE: float = 0.02
    SOIL_EVAP_WIND_FACTOR: float = 0.1

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                world: Optional[World] = None,
                rainfall_factor: float = 1.0,
                climate_humidity_bias: float = 0.0, **kwargs) -> None:
        ah = weather.absolute_humidity
        sat_ah = saturation_absolute_humidity(weather.temperature)
        rh = ah / sat_ah if sat_ah > 0 else 1.0

        # 蒸发
        evap_factor = 1.0 + climate_humidity_bias
        evaporation = (
            EVAPORATION_COEFFICIENT
            * max(0.5, weather.wind_speed)
            * max(0.0, 1.0 - rh)
            * max(0.5, evap_factor)
        )

        # 土壤蒸发回馈
        if world is not None:
            try:
                from environment.soil.components.soil_moisture_component import (
                    SoilMoistureComponent,
                )
                soil_moisture = world.get_world_entity().get_component(SoilMoistureComponent)
                if soil_moisture is not None and soil_moisture.moisture > 0.01:
                    moisture_ratio = soil_moisture.moisture / max(soil_moisture.capacity, 0.1)
                    soil_evap = (
                        self.SOIL_EVAP_FEEDBACK_RATE
                        * moisture_ratio
                        * (1.0 + self.SOIL_EVAP_WIND_FACTOR * weather.wind_speed)
                        * dt
                    )
                    evaporation += soil_evap
            except (ImportError, AttributeError):
                pass

        # 降水消耗
        precip_loss = weather.precipitation_rate * PRECIPITATION_CONSUMPTION * dt

        # 平流
        advection = (BACKGROUND_ABSOLUTE_HUMIDITY - ah) / HUMIDITY_ADVECTION_TIMESCALE * dt

        ah += (evaporation - precip_loss) * dt + advection
        ah = max(ABSOLUTE_HUMIDITY_MIN, min(ABSOLUTE_HUMIDITY_MAX, ah))
        weather.absolute_humidity = ah

        weather.relative_humidity = relative_humidity(ah, weather.temperature)


class CloudCoverProcessor(WeatherProcessor):
    """云量处理器 — 相对湿度驱动 + 气压下降促进"""

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                hour: float = 12.0, **kwargs) -> None:
        rh = weather.relative_humidity
        cloud = weather.cloud_cover

        base_decay = CLOUD_DISSIPATION_BASE_RATE * cloud * dt

        daytime_factor = 0.0
        if 6.0 <= hour <= 18.0:
            daytime_factor = CLOUD_DAYTIME_DISSIPATION_FACTOR * cloud * dt

        if rh > CLOUD_FORMATION_RH_THRESHOLD:
            rh_excess = rh - CLOUD_FORMATION_RH_THRESHOLD
            growth = CLOUD_FORMATION_RATE * rh_excess * (1.0 - cloud) * dt

            pressure_anomaly = STANDARD_PRESSURE - weather.pressure
            uplift_factor = max(0.0, pressure_anomaly / 50.0)
            growth += CLOUD_PRESSURE_DROP_RATE * uplift_factor * (1.0 - cloud) * dt
            growth = min(growth, CLOUD_MAX_GROWTH_RATE * dt)

            cloud += growth - base_decay - daytime_factor
        elif rh < CLOUD_DISSIPATION_RH_THRESHOLD:
            rh_deficit = CLOUD_DISSIPATION_RH_THRESHOLD - rh
            extra_decay = CLOUD_DISSIPATION_RH_RATE * rh_deficit * cloud * dt
            cloud -= (base_decay + extra_decay + daytime_factor)
        else:
            cloud -= (base_decay + daytime_factor)

        weather.cloud_cover = max(0.0, min(1.0, cloud))


class PrecipitationProcessor(WeatherProcessor):
    """降水处理器 — 云量+湿度条件触发"""

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                rainfall_factor: float = 1.0, **kwargs) -> None:
        cloud = weather.cloud_cover
        rh = weather.relative_humidity

        if cloud > PRECIP_CLOUD_THRESHOLD and rh > PRECIP_RH_THRESHOLD:
            cloud_factor = (cloud - PRECIP_CLOUD_THRESHOLD) / (1.0 - PRECIP_CLOUD_THRESHOLD)
            rh_factor = (rh - PRECIP_RH_THRESHOLD) / (1.0 - PRECIP_RH_THRESHOLD)

            rate = PRECIP_BASE_RATE * cloud_factor * rh_factor * rainfall_factor

            drain = rate * PRECIP_HUMIDITY_DRAIN_FACTOR * dt
            weather.absolute_humidity = max(ABSOLUTE_HUMIDITY_MIN, weather.absolute_humidity - drain)

            cloud_drain = rate * 0.01 * dt
            weather.cloud_cover = max(0.0, weather.cloud_cover - cloud_drain)

            weather.precipitation_rate = rate
        else:
            weather.precipitation_rate *= math.exp(-2.0 * dt)
            if weather.precipitation_rate < 0.001:
                weather.precipitation_rate = 0.0


class WindSpeedProcessor(WeatherProcessor):
    """风速处理器 — 基线 + 气压梯度 + 噪声"""

    def process(self, weather: PhysicalWeatherComponent, dt: float,
                day_of_year: int = 1, **kwargs) -> None:
        seasonal = WIND_SEASONAL_AMP * math.sin(
            2.0 * math.pi * (day_of_year - 80) / 365.0
        )
        baseline = WIND_BASELINE + seasonal

        pressure_anomaly = abs(STANDARD_PRESSURE - weather.pressure)
        gradient_term = pressure_anomaly * WIND_PRESSURE_GRADIENT_COEFF

        weather._wind_noise *= WIND_REGRESSION_COEFF
        weather._wind_noise += random.gauss(0, WIND_NOISE_STD * dt)

        new_wind = baseline + gradient_term + weather._wind_noise
        weather.wind_speed = max(WIND_MIN, min(WIND_MAX, new_wind))
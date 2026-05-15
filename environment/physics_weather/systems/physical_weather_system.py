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

【ECS 职责】
- PhysicalWeatherSystem 读写 PhysicalWeatherComponent
- 不涉及任何离散状态枚举
"""

import math
import random

from core.world import World
from core.system import System

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.config.physics_constants import (
    # 温度
    DIURNAL_PEAK_HOUR,
    DEFAULT_DIURNAL_RANGE,
    SEASONAL_TEMP_AMPLITUDE,
    TEMP_NOISE_STD,
    TEMP_NOISE_REGRESSION,
    CLOUD_DAMPING_FACTOR,
    # 气压
    STANDARD_PRESSURE,
    PRESSURE_SEASONAL_AMP,
    PRESSURE_SYNOPTIC_PERIOD_HOURS,
    PRESSURE_SYNOPTIC_AMP,
    PRESSURE_NOISE_STD,
    PRESSURE_MIN,
    PRESSURE_MAX,
    # 水汽
    EVAPORATION_COEFFICIENT,
    PRECIPITATION_CONSUMPTION,
    HUMIDITY_ADVECTION_TIMESCALE,
    BACKGROUND_ABSOLUTE_HUMIDITY,
    ABSOLUTE_HUMIDITY_MIN,
    ABSOLUTE_HUMIDITY_MAX,
    # 云量
    CLOUD_FORMATION_RH_THRESHOLD,
    CLOUD_DISSIPATION_RH_THRESHOLD,
    CLOUD_FORMATION_RATE,
    CLOUD_DISSIPATION_BASE_RATE,
    CLOUD_DISSIPATION_RH_RATE,
    CLOUD_PRESSURE_DROP_RATE,
    CLOUD_MAX_GROWTH_RATE,
    CLOUD_DAYTIME_DISSIPATION_FACTOR,
    # 降水
    PRECIP_CLOUD_THRESHOLD,
    PRECIP_RH_THRESHOLD,
    PRECIP_BASE_RATE,
    PRECIP_HUMIDITY_DRAIN_FACTOR,
    # 风速
    WIND_BASELINE,
    WIND_SEASONAL_AMP,
    WIND_PRESSURE_GRADIENT_COEFF,
    WIND_NOISE_STD,
    WIND_REGRESSION_COEFF,
    WIND_MIN,
    WIND_MAX,
    # 物理函数
    saturation_absolute_humidity,
    relative_humidity,
    saturation_vapor_pressure,
)
from environment.season.season_component import SeasonComponent


class PhysicalWeatherSystem(System):
    """
    物理天气演化系统

    每步更新所有连续物理量，模拟真实大气物理过程。
    可与 SeasonComponent 耦合（可选），也可以独立运行。
    """

    def __init__(self, latitude: float = 35.0, elevation: float = 0.0):
        super().__init__()
        self.latitude = latitude
        self.elevation = elevation

    def update(self, world: World, delta_hours: float):
        """主更新入口"""
        weather = world._world_entity.get_component(PhysicalWeatherComponent)
        if weather is None:
            return

        time = world.get_time()
        season_comp = world._world_entity.get_component(SeasonComponent)

        # 获取季节信息（可选耦合）
        season_offset = 0.0
        season_rainfall_factor = 1.0
        if season_comp is not None:
            season_offset = season_comp.temperature_offset
            season_rainfall_factor = season_comp.rainfall_factor

        hour = time.hour
        day_of_year = time.day_of_year

        # =========================================================
        # 1️⃣ 温度演化
        # =========================================================
        self._update_temperature(weather, hour, day_of_year, season_offset, delta_hours)

        # =========================================================
        # 2️⃣ 气压演化
        # =========================================================
        self._update_pressure(weather, hour, day_of_year, delta_hours)

        # =========================================================
        # 3️⃣ 水汽演化 & 相对湿度计算
        # =========================================================
        self._update_humidity(
            weather, delta_hours, season_rainfall_factor,
        )

        # =========================================================
        # 4️⃣ 云量演化
        # =========================================================
        self._update_cloud_cover(weather, hour, delta_hours)

        # =========================================================
        # 5️⃣ 降水演化
        # =========================================================
        self._update_precipitation(
            weather, delta_hours, season_rainfall_factor,
        )

        # =========================================================
        # 6️⃣ 风速演化
        # =========================================================
        self._update_wind_speed(weather, hour, day_of_year, delta_hours)

    # ============================================================
    # 🌡 温度更新
    # ============================================================

    def _update_temperature(
        self,
        weather: PhysicalWeatherComponent,
        hour: float,
        day_of_year: int,
        season_offset: float,
        delta_hours: float,
    ):
        """温度演化：日循环 + 季节偏置 + 云量阻尼 + 噪声"""

        # 基准温度：季节偏置
        base_temp = 18.0 + season_offset

        # 日循环：正弦波，峰值在 14:00，谷值在 5:00
        # 将小时映射到 [0, 2π]，峰值在 hour=14
        hour_angle = 2.0 * math.pi * (hour - DIURNAL_PEAK_HOUR) / 24.0
        diurnal_range = DEFAULT_DIURNAL_RANGE * (
            1.0 - CLOUD_DAMPING_FACTOR * weather.cloud_cover
        )
        diurnal_anomaly = (diurnal_range / 2.0) * math.cos(hour_angle)

        # 温度噪声：累积有偏随机游走 + 回归
        weather._temp_noise *= TEMP_NOISE_REGRESSION
        weather._temp_noise += random.gauss(0, TEMP_NOISE_STD * delta_hours)

        # 合成温度，考虑海拔递减
        new_temp = base_temp + diurnal_anomaly + weather._temp_noise
        new_temp += self.elevation * -0.0065  # 海拔递减率
        weather.temperature = new_temp

    # ============================================================
    # 🌀 气压更新
    # ============================================================

    def _update_pressure(
        self,
        weather: PhysicalWeatherComponent,
        hour: float,
        day_of_year: int,
        delta_hours: float,
    ):
        """
        气压演化：
        - 年周期（季节变化）
        - 中周期（天气系统通过，~5天）
        - 随机噪声
        """
        total_hours = day_of_year * 24.0 + hour

        # 年周期
        yearly_phase = 2.0 * math.pi * day_of_year / 365.0
        yearly_component = PRESSURE_SEASONAL_AMP * math.sin(yearly_phase)

        # 中周期（天气系统）
        synoptic_phase = (
            2.0 * math.pi * total_hours / PRESSURE_SYNOPTIC_PERIOD_HOURS
        )
        synoptic_component = PRESSURE_SYNOPTIC_AMP * math.sin(
            synoptic_phase + weather._pressure_phase
        )

        # 随机噪声
        noise = random.gauss(0, PRESSURE_NOISE_STD * delta_hours)

        new_pressure = (
            STANDARD_PRESSURE + yearly_component + synoptic_component + noise
        )

        # 钳制到合理范围
        weather.pressure = max(PRESSURE_MIN, min(PRESSURE_MAX, new_pressure))

        # 缓慢更新气压相位（模拟天气系统相位漂移）
        weather._pressure_phase += random.uniform(-0.05, 0.05) * delta_hours

    # ============================================================
    # 💧 水汽与相对湿度更新
    # ============================================================

    def _update_humidity(
        self,
        weather: PhysicalWeatherComponent,
        delta_hours: float,
        rainfall_factor: float = 1.0,
    ):
        """
        绝对湿度演化：
        - 蒸发：取决于风速和当前湿度亏缺
        - 降水消耗：降水带走水汽
        - 平流：向背景湿度漂移

        相对湿度从绝对湿度和温度实时重算。
        """
        ah = weather.absolute_humidity

        # ── 蒸发项 ──
        # 蒸发率 = coeff * wind * (1 - RH)
        # 湿度越低、风速越大，蒸发越快
        sat_ah = saturation_absolute_humidity(weather.temperature)
        rh = ah / sat_ah if sat_ah > 0 else 1.0
        evaporation = (
            EVAPORATION_COEFFICIENT
            * max(0.5, weather.wind_speed)
            * max(0.0, 1.0 - rh)
        )

        # ── 降水消耗项 ──
        # 降水消耗水汽
        precip_loss = (
            weather.precipitation_rate * PRECIPITATION_CONSUMPTION * delta_hours
        )

        # ── 平流项 ──
        # 向背景湿度漂移
        advection = (
            (BACKGROUND_ABSOLUTE_HUMIDITY - ah)
            / HUMIDITY_ADVECTION_TIMESCALE
            * delta_hours
        )

        # 合成
        ah += (evaporation - precip_loss) * delta_hours + advection
        ah = max(ABSOLUTE_HUMIDITY_MIN, min(ABSOLUTE_HUMIDITY_MAX, ah))
        weather.absolute_humidity = ah

        # ── 重算相对湿度 ──
        weather.relative_humidity = relative_humidity(ah, weather.temperature)

    # ============================================================
    # ☁️ 云量更新
    # ============================================================

    def _update_cloud_cover(
        self,
        weather: PhysicalWeatherComponent,
        hour: float,
        delta_hours: float,
    ):
        """
        云量演化（含滞后效应）：
        - 基线消散：任何时候云量都以小速率自然衰减
        - RH > 形成阈值 → 云量增长
        - RH 低于形成阈值但高于消散阈值 → 云量缓慢衰减
        - RH < 消散阈值 → 云量快速衰减
        - 气压快速下降（低压）促进云量增长（上升气流）
        - 白天太阳辐射有额外消散效果
        
        物理意义：云是动态平衡，既不会无限累积，
        也不会在条件合适时完全不形成。
        """
        rh = weather.relative_humidity
        cloud = weather.cloud_cover

        # ── 基线消散（始终存在） ──
        base_decay = CLOUD_DISSIPATION_BASE_RATE * cloud * delta_hours

        # ── 日间额外消散（6:00 ~ 18:00） ──
        daytime_factor = 0.0
        if 6.0 <= hour <= 18.0:
            daytime_factor = CLOUD_DAYTIME_DISSIPATION_FACTOR * cloud * delta_hours

        # ── RH 驱动的消散或形成 ──
        if rh > CLOUD_FORMATION_RH_THRESHOLD:
            # 成云阶段
            rh_excess = rh - CLOUD_FORMATION_RH_THRESHOLD
            growth = CLOUD_FORMATION_RATE * rh_excess * (1.0 - cloud) * delta_hours
            
            # 气团上升贡献
            pressure_anomaly = STANDARD_PRESSURE - weather.pressure
            uplift_factor = max(0.0, pressure_anomaly / 50.0)
            growth += CLOUD_PRESSURE_DROP_RATE * uplift_factor * (1.0 - cloud) * delta_hours
            
            growth = min(growth, CLOUD_MAX_GROWTH_RATE * delta_hours)
            
            # 净变化 = 增长 - 基线消散 - 日间消散
            cloud += growth - base_decay - daytime_factor
        elif rh < CLOUD_DISSIPATION_RH_THRESHOLD:
            # 快速消散阶段（空气干燥）
            rh_deficit = CLOUD_DISSIPATION_RH_THRESHOLD - rh
            extra_decay = CLOUD_DISSIPATION_RH_RATE * rh_deficit * cloud * delta_hours
            cloud -= (base_decay + extra_decay + daytime_factor)
        else:
            # 过渡区（阈值之间）：基线消散 + 日间消散
            cloud -= (base_decay + daytime_factor)

        weather.cloud_cover = max(0.0, min(1.0, cloud))

    # ============================================================
    # 🌧 降水更新
    # ============================================================

    def _update_precipitation(
        self,
        weather: PhysicalWeatherComponent,
        delta_hours: float,
        rainfall_factor: float = 1.0,
    ):
        """
        降水演化：
        - 条件：云量 > 阈值 AND 相对湿度 > 阈值
        - 速率：正比于云量和湿度超出量
        - 消耗：降水消耗水汽（自抑制）
        """
        cloud = weather.cloud_cover
        rh = weather.relative_humidity

        if (cloud > PRECIP_CLOUD_THRESHOLD
                and rh > PRECIP_RH_THRESHOLD):
            # 云量因子：线性从阈值到1
            cloud_factor = (cloud - PRECIP_CLOUD_THRESHOLD) / (
                1.0 - PRECIP_CLOUD_THRESHOLD
            )
            # 湿度因子：线性从阈值到1
            rh_factor = (rh - PRECIP_RH_THRESHOLD) / (
                1.0 - PRECIP_RH_THRESHOLD
            )

            rate = (
                PRECIP_BASE_RATE
                * cloud_factor
                * rh_factor
                * rainfall_factor
            )

            # 降水消耗水汽（自抑制机制）
            drain = rate * PRECIP_HUMIDITY_DRAIN_FACTOR * delta_hours
            weather.absolute_humidity = max(
                ABSOLUTE_HUMIDITY_MIN,
                weather.absolute_humidity - drain,
            )

            # 降水也从云量中消耗（水滴落下后云减少）
            cloud_drain = rate * 0.01 * delta_hours
            weather.cloud_cover = max(0.0, weather.cloud_cover - cloud_drain)

            weather.precipitation_rate = rate
        else:
            # 无降水的条件下，降水速率指数衰减到0
            weather.precipitation_rate *= math.exp(-2.0 * delta_hours)
            if weather.precipitation_rate < 0.001:
                weather.precipitation_rate = 0.0

    # ============================================================
    # 🌬 风速更新
    # ============================================================

    def _update_wind_speed(
        self,
        weather: PhysicalWeatherComponent,
        hour: float,
        day_of_year: int,
        delta_hours: float,
    ):
        """
        风速演化：
        - 基线风速（受季节影响）
        - 气压梯度贡献（低压系统风更大）
        - 随机变化 + 回归基线
        """
        # 季节影响
        seasonal = WIND_SEASONAL_AMP * math.sin(
            2.0 * math.pi * (day_of_year - 80) / 365.0
        )
        baseline = WIND_BASELINE + seasonal

        # 气压梯度贡献
        pressure_anomaly = abs(STANDARD_PRESSURE - weather.pressure)
        gradient_term = pressure_anomaly * WIND_PRESSURE_GRADIENT_COEFF

        # 噪声 + 回归
        weather._wind_noise *= WIND_REGRESSION_COEFF
        weather._wind_noise += random.gauss(0, WIND_NOISE_STD * delta_hours)

        new_wind = baseline + gradient_term + weather._wind_noise
        weather.wind_speed = max(WIND_MIN, min(WIND_MAX, new_wind))

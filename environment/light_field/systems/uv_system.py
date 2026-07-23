#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紫外线系统

v3.6 新增 — P1

职责：
    - 计算紫外线强度
    - 臭氧层吸收 UV-C/UV-B
    - 影响生物（DNA损伤、维生素D合成）

设计原则：
    - 纯物理驱动：太阳角度、臭氧浓度、海拔
    - 无硬编码 UV 指数

依赖：
    - LightFieldComponent
    - AtmosphereComponent（臭氧）
"""

import logging
from typing import Dict

from core.system import System
from core.world import World

from environment.light_field.components.light_field_component import LightFieldComponent
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent

logger = logging.getLogger(__name__)


class UVSystem(System):
    """
    紫外线系统

    物理原理：
    - UV 强度 ∝ 太阳高度角
    - UV-B 被臭氧吸收（吸收系数 ~300 × UV-A）
    - UV-C 几乎被完全吸收
    - 海拔越高 UV 越强（每升高 1000m + 10-12%）

    每帧更新：
    1. 计算基础 UV（基于太阳角度）
    2. 臭氧层吸收
    3. 海拔修正
    4. 云层衰减
    """

    tick_interval = 5

    # 物理常数
    UV_SOLAR_CONSTANT = 50.0  # 太阳常数中的 UV 部分 W/m²
    OZONE_ABSORPTION_UVA = 0.01   # 臭氧对 UV-A 的吸收系数
    OZONE_ABSORPTION_UVB = 3.0    # 臭氧对 UV-B 的吸收系数
    OZONE_ABSORPTION_UVC = 100.0  # 臭氧对 UV-C 的吸收系数

    def update(self, world: World, dt: float) -> None:
        """更新 UV"""
        for entity, (light, atmos) in world.get_components(
            LightFieldComponent, AtmosphereComponent
        ):
            if light is None:
                continue

            # 1. 基础 UV（基于太阳高度角）
            self._calculate_base_uv(light)

            # 2. 臭氧层吸收
            self._apply_ozone_absorption(light, atmos)

            # 3. 海拔修正
            self._apply_altitude_correction(light, atmos)

            # 4. 计算 UV 指数
            self._calculate_uv_index(light)

    def _calculate_base_uv(self, light: LightFieldComponent) -> None:
        """计算基础 UV（基于太阳高度角）"""
        # 太阳高度角 → UV 强度
        # UV ∝ sin(太阳高度角)
        elevation_rad = light.sun_elevation * 0.0174533  # 度 → 弧度
        
        # 简化的 sin 计算
        sin_elev = self._sin(elevation_rad)
        
        if sin_elev <= 0:
            # 夜间无 UV
            light.uva = 0.0
            light.uvb = 0.0
            light.uvc = 0.0
            return

        # 基础 UV（太阳常数 × sin(高度角)）
        base_uv = self.UV_SOLAR_CONSTANT * sin_elev

        # 光谱分布
        light.uva = base_uv * 0.95  # UV-A 占 95%
        light.uvb = base_uv * 0.05  # UV-B 占 5%
        light.uvc = base_uv * 0.001  # UV-C 占 0.1%

    def _apply_ozone_absorption(self, light: LightFieldComponent,
                                atmos: AtmosphereComponent) -> None:
        """应用臭氧层吸收"""
        if atmos is None:
            return

        ozone_ppm = atmos.o3_ppm

        # 比尔-朗伯定律：I = I₀ × exp(-ε × c × l)
        # 简化：吸收 ∝ 臭氧浓度 × 吸收系数
        
        # UV-A 少量吸收
        uva_absorption = ozone_ppm * self.OZONE_ABSORPTION_UVA
        light.uva *= self._exp(-uva_absorption)

        # UV-B 大量吸收
        uvb_absorption = ozone_ppm * self.OZONE_ABSORPTION_UVB
        light.uvb *= self._exp(-uvb_absorption)

        # UV-C 几乎完全吸收
        uvc_absorption = ozone_ppm * self.OZONE_ABSORPTION_UVC
        light.uvc *= self._exp(-uvc_absorption)

    def _apply_altitude_correction(self, light: LightFieldComponent,
                                   atmos: AtmosphereComponent) -> None:
        """海拔修正（每升高 1000m + 10%）"""
        if atmos is None:
            return

        altitude_km = atmos.altitude / 1000.0
        
        # 海拔修正因子
        correction = 1.0 + altitude_km * 0.1

        light.uva *= correction
        light.uvb *= correction
        light.uvc *= correction

    def _calculate_uv_index(self, light: LightFieldComponent) -> None:
        """计算 UV 指数"""
        # UVI = 0.04 × (UV-A + 1.5 × UV-B) W/m²
        # 加权 UV-B（对皮肤影响更大）
        weighted_uv = light.uva + 1.5 * light.uvb
        light.uv_index = weighted_uv * 0.04

    def _sin(self, theta: float) -> float:
        """简化的 sin 计算"""
        # 归一化到 -π~π
        theta = theta % 6.283185307179586
        if theta > 3.141592653589793:
            theta = 6.283185307179586 - theta
            sign = -1
        else:
            sign = 1
        
        theta2 = theta * theta
        result = theta - theta * theta2 / 6 + theta * theta2 * theta2 / 120
        return sign * result

    def _exp(self, x: float) -> float:
        """简化的 exp 计算"""
        # 泰勒展开
        if x < -5:
            return 0.0
        if x > 5:
            return 148.413
        
        result = 1.0
        term = 1.0
        for i in range(1, 20):
            term *= x / i
            result += term
            if abs(term) < 1e-10:
                break
        
        return result
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UV生物系统

v3.6 新增 — P2

职责：
    - UV影响生物健康
    - UV-B导致DNA损伤
    - UV-A促进维生素D合成
    - 过度暴露导致晒伤

设计原则：
    - 纯物理驱动：UV强度 × 暴露时间 → 生物效应
    - 无硬编码阈值

依赖：
    - HealthStatusComponent
    - LightFieldComponent（UV数据）
"""

import logging
from typing import Dict

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent
from biology.systems.health_status_system import HealthStatusSystem
from environment.light_field.components.light_field_component import LightFieldComponent

logger = logging.getLogger(__name__)


class UVBiologySystem(System):
    """
    UV生物系统

    物理原理：
    - UV-B (280-315nm) → DNA损伤、皮肤癌风险
    - UV-A (315-400nm) → 维生素D合成、皮肤老化
    - UV-C (100-280nm) → 几乎被臭氧层吸收

    每帧更新：
    1. 计算UV暴露量
    2. DNA损伤累积
    3. 维生素D合成
    4. 晒伤判定
    """

    tick_interval = 5  # 每5帧执行一次

    # 生物效应系数
    UVB_DNA_DAMAGE_RATE = 0.0001    # UV-B DNA损伤速率
    UVA_VITAMIN_D_RATE = 0.001      # UV-A 维生素D合成速率
    SUNBURN_THRESHOLD = 50.0        # 晒伤阈值（UV指数 × 时间）

    def update(self, world: World, dt: float) -> None:
        """更新UV生物效应"""
        for entity, (health, light) in world.get_components(
            HealthStatusComponent, LightFieldComponent
        ):
            if health is None or light is None:
                continue

            # 1. UV-B DNA损伤
            self._apply_uvb_damage(health, light, dt)

            # 2. UV-A 维生素D合成
            self._apply_uva_vitamin_d(health, light, dt)

            # 3. 晒伤判定
            self._check_sunburn(health, light, dt)

    def _apply_uvb_damage(self, health: HealthStatusComponent,
                          light: LightFieldComponent, dt: float) -> None:
        """UV-B导致DNA损伤"""
        uvb = light.uvb

        if uvb <= 0:
            return

        # DNA损伤 ∝ UV-B强度 × 时间
        dna_damage = uvb * self.UVB_DNA_DAMAGE_RATE * dt

        if dna_damage > 0.001:
            HealthStatusSystem.add_wound(None, health, "dna_damage", dna_damage, damage_per_sec=dna_damage * 0.01)

    def _apply_uva_vitamin_d(self, health: HealthStatusComponent,
                             light: LightFieldComponent, dt: float) -> None:
        """UV-A促进维生素D合成"""
        uva = light.uva

        if uva <= 0:
            return

        # 维生素D合成 ∝ UV-A强度 × 时间
        vitamin_d = uva * self.UVA_VITAMIN_D_RATE * dt

        # 维生素D提升免疫力和骨骼健康
        if hasattr(health, 'repair_efficiency'):
            health.repair_efficiency = min(1.0, health.repair_efficiency + vitamin_d * 0.001)

    def _check_sunburn(self, health: HealthStatusComponent,
                       light: LightFieldComponent, dt: float) -> None:
        """检查晒伤"""
        uv_index = light.uv_index

        if uv_index <= 3:
            return

        # 晒伤风险 ∝ UV指数 × 时间
        exposure = uv_index * dt

        if exposure > self.SUNBURN_THRESHOLD:
            burn_severity = (exposure - self.SUNBURN_THRESHOLD) * 0.01
            HealthStatusSystem.add_wound(None, health, "sunburn", burn_severity, damage_per_sec=burn_severity * 0.1)

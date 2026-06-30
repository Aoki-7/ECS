#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
营养级传递系统

根据食物链关系计算能量在各营养级之间的传递效率，
并据此调节实体的能量获取和消耗。

核心公式：
    营养级 N 的能量 = 营养级 N-1 的能量 × 传递效率（通常 10%）

Lindeman 十分之一定律：
    每上升一个营养级，可用能量约为前一级的 10%。
"""

import logging
from core.system import System
from core.world import World

from biology.ecology.components.food_chain_component import FoodChainComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class TrophicLevelSystem(System):
    tick_interval = 30
    """
    营养级传递系统

    职责：
        1. 计算各营养级的总生物量
        2. 根据 Lindeman 定律调节能量传递效率
        3. 顶级捕食者因能量传递损失而承受更高的能量消耗压力
    """

    # Lindeman 传递效率基准
    BASE_TRANSFER_EFFICIENCY = 0.1

    # 营养级能量消耗倍率（顶级捕食者需要更多能量维持生存）
    TROPHIC_MAINTENANCE_COST = {
        1: 0.0,   # 生产者通过光合作用获得能量
        2: 0.02,  # 初级消费者额外消耗
        3: 0.05,  # 次级消费者额外消耗
        4: 0.10,  # 顶级捕食者额外消耗
    }

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行营养级传递计算
        """
        # 统计各营养级总生物量
        trophic_biomass = self._calculate_trophic_biomass(world)

        # 计算能量金字塔是否稳定
        for entity, (fc, energy, space) in world.get_components(
            FoodChainComponent, EnergyComponent, SpaceComponent
        ):
            if not world.has_entity(entity):
                continue

            # 应用营养级维持消耗（注意 dt 已被 world.update 按 tick_interval 缩放，
            # 因此维护消耗需除以 tick_interval 以保持每步实际消耗率一致）
            maintenance = self.TROPHIC_MAINTENANCE_COST.get(fc.trophic_level, 0.0)
            if maintenance > 0 and energy.value > 0:
                actual_dt = dt / self.tick_interval
                energy.value = max(0.0, energy.value - maintenance * energy.max_energy * actual_dt)

            # 如果某营养级生物量过低，降低该营养级实体的能量获取效率
            if fc.trophic_level >= 2:
                lower_level = fc.trophic_level - 1
                lower_biomass = trophic_biomass.get(lower_level, 0.0)
                if lower_biomass < 5.0:  # 猎物稀缺
                    # 能量额外消耗（饥饿压力）
                    actual_dt = dt / self.tick_interval
                    energy.value = max(0.0, energy.value - 0.05 * energy.max_energy * actual_dt)

        # 记录生态金字塔状态
        if logger.isEnabledFor(logging.DEBUG):
            pyramid = " → ".join(
                f"L{k}:{v:.1f}" for k, v in sorted(trophic_biomass.items())
            )
            if logger.isEnabledFor(logging.DEBUG):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[Trophic] 能量金字塔: {pyramid}")

    def _calculate_trophic_biomass(self, world: World) -> dict[int, float]:
        """计算各营养级的总生物量"""
        biomass = {}
        for entity, (fc,) in world.get_components(FoodChainComponent):
            if not world.has_entity(entity):
                continue
            level = fc.trophic_level
            biomass[level] = biomass.get(level, 0.0) + fc.biomass
        return biomass

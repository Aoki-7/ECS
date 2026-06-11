#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/immune_system.py
@说明:免疫系统

负责感染传播、免疫反应演化与症状影响。

状态转换链：
    healthy → incubating → infected → recovering → healthy/immune

传播机制：
    - 感染期实体具有传染性
    - 潜伏期超过 12 小时后也开始传染
    - 传播范围受 SpaceComponent 坐标限制（SPREAD_RADIUS 格内）
    - 免疫记忆可降低再感染概率
"""

import random
from typing import List, Tuple

from core.system import System
from core.world import World
from identity.event_log_system import EventLog

from biology.components.immune_component import ImmuneComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent


class ImmuneSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    免疫系统

    职责：
        1. 感染传播：contagious 实体向周围易感实体传播病原体
        2. 免疫反应：更新感染持续时间，驱动状态转换
        3. 症状影响：感染期持续消耗宿主能量
    """

    # 传播半径（格子）
    SPREAD_RADIUS = 3
    # 基础传播概率
    BASE_SPREAD_CHANCE = 0.05
    # 潜伏期（小时）
    INCUBATION_PERIOD = 24.0
    # 感染期（小时）
    INFECTION_PERIOD = 48.0
    # 康复期（小时）
    RECOVERY_PERIOD = 24.0
    # 症状能量消耗系数（每小时）
    SYMPTOM_ENERGY_DRAIN = 0.5

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self.enable_log = True

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行免疫更新

        Args:
            world: World 实例
            dt: 时间步长（小时）
        """
        self._spread_infection(world, dt)
        self._evolve_infection(world, dt)
        self._apply_symptoms(world, dt)

    # -------------------------------------------------
    # 感染传播
    # -------------------------------------------------

    def _spread_infection(self, world: World, dt: float):
        """contagious 实体向周围传播（使用空间索引避免 O(N²)）"""
        from space.space_system import SpaceSystem
        space_system = world.get_system(SpaceSystem)

        # 收集所有 contagious 实体
        contagious: List[Tuple] = []
        for entity, (immune, space) in list(world.get_components(
            ImmuneComponent, SpaceComponent
        )):
            if immune.is_contagious:
                contagious.append((entity, immune, space))

        if not contagious:
            return

        # 向周围传播
        for src_entity, src_immune, src_space in contagious:
            # 使用空间索引查询半径内实体，避免全量遍历
            nearby_ids = set()
            if space_system is not None:
                nearby_ids = space_system.query_radius(
                    src_space.x, src_space.y, self.SPREAD_RADIUS, getattr(src_space, 'layer', 0)
                )

            for dst_id in nearby_ids:
                if dst_id == src_entity.id:
                    continue
                dst_entity = world.query_entity(dst_id)
                if dst_entity is None:
                    continue
                dst_immune = world.get_component(dst_entity, ImmuneComponent)
                if dst_immune is None or not dst_immune.is_healthy:
                    continue
                dst_space = world.get_component(dst_entity, SpaceComponent)
                if dst_space is None:
                    continue

                distance = max(abs(src_space.x - dst_space.x), abs(src_space.y - dst_space.y))
                spread_chance = self.BASE_SPREAD_CHANCE * (
                    1.0 - distance / (self.SPREAD_RADIUS + 1)
                )
                spread_chance *= src_immune.symptom_severity

                # 免疫记忆降低感染概率
                immunity = dst_immune.get_immunity(src_immune.pathogen_type)
                spread_chance *= (1.0 - immunity)

                if spread_chance > 0 and self._rng.random() < spread_chance:
                    self._infect(dst_immune, src_immune.pathogen_type)
                    if self.enable_log:
                        EventLog.log(
                            world,
                            event_type="infection",
                            description=(
                                f"实体 E{dst_entity.id} 被"
                                f" {src_immune.pathogen_type} 感染"
                            ),
                            entity_id=dst_entity.id,
                            severity="warning",
                        )

    def _infect(self, immune: ImmuneComponent, pathogen_type: str):
        """设置感染状态"""
        immune.infection_status = "incubating"
        immune.pathogen_type = pathogen_type
        immune.infection_duration = 0.0
        immune.symptom_severity = 0.0
        immune.infection_count += 1

    # -------------------------------------------------
    # 免疫反应演化
    # -------------------------------------------------

    def _evolve_infection(self, world: World, dt: float):
        """更新感染状态机"""
        for entity, (immune,) in world.get_components(ImmuneComponent):
            if immune.is_healthy:
                continue

            immune.infection_duration += dt

            if immune.infection_status == "incubating":
                if immune.infection_duration >= self.INCUBATION_PERIOD:
                    immune.infection_status = "infected"
                    immune.symptom_severity = self._rng.uniform(0.3, 0.8)

            elif immune.infection_status == "infected":
                total_infected_time = (
                    immune.infection_duration - self.INCUBATION_PERIOD
                )
                if total_infected_time >= self.INFECTION_PERIOD:
                    # 根据抵抗力 + 免疫记忆判定康复
                    recovery_chance = immune.resistance * (
                        1.0 + immune.get_immunity(immune.pathogen_type)
                    )
                    recovery_chance = min(1.0, recovery_chance)

                    if self._rng.random() < recovery_chance:
                        immune.infection_status = "recovering"
                        immune.symptom_severity *= 0.5
                    else:
                        # 恶化：症状加重
                        immune.symptom_severity = min(
                            1.0, immune.symptom_severity + 0.1
                        )

            elif immune.infection_status == "recovering":
                total_time = (
                    immune.infection_duration
                    - self.INCUBATION_PERIOD
                    - self.INFECTION_PERIOD
                )
                if total_time >= self.RECOVERY_PERIOD:
                    immune.infection_status = "healthy"
                    # 建立免疫记忆
                    current = immune.immune_memory.get(immune.pathogen_type, 0.0)
                    immune.immune_memory[immune.pathogen_type] = min(
                        1.0, current + 0.3
                    )
                    immune.pathogen_type = None
                    immune.symptom_severity = 0.0
                    immune.infection_duration = 0.0

    # -------------------------------------------------
    # 症状影响
    # -------------------------------------------------

    def _apply_symptoms(self, world: World, dt: float):
        """感染期消耗宿主能量"""
        for entity, (immune, energy) in world.get_components(
            ImmuneComponent, EnergyComponent
        ):
            if immune.infection_status == "infected":
                drain = (
                    immune.symptom_severity
                    * self.SYMPTOM_ENERGY_DRAIN
                    * dt
                )
                energy.value = max(0.0, energy.value - drain)

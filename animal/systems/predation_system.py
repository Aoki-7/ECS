#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物捕食系统

处理食肉动物 (diet="carnivore") 的捕食行为：
    1. 在感知范围内搜索食草动物
    2. 计算攻击成功率
    3. 成功则对猎物造成伤害（减少能量）
    4. 若猎物能量耗尽，标记为死亡（PendingDeathComponent）
    5. 捕食者获得能量补充

与 GrazingSystem 的关系：
    - GrazingSystem 处理植物 → 食草动物的能量转移
    - PredationSystem 处理食草动物 → 食肉动物的能量转移
    - 两者共同构成食物链的两级消费层
"""

import random

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem
from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent

import logging

logger = logging.getLogger(__name__)


class PredationSystem(System):
    tick_interval = 15
    """
    捕食系统

    职责：
        1. 遍历食肉动物
        2. 使用空间索引查找附近食草动物
        3. 计算攻击成功率并执行伤害
        4. 猎物死亡时挂载 PendingDeathComponent
        5. 将猎物能量转移给捕食者
    """

    # 单次攻击基础伤害
    BASE_DAMAGE = 15.0

    # 攻击成功率（简化模型，后续可扩展为基因决定）
    BASE_SUCCESS_RATE = 0.6

    # 营养转化率（猎物能量 → 捕食者能量的比例）
    ENERGY_CONVERSION_RATIO = 0.4

    # 捕食后冷却期（避免同一捕食者每帧都攻击）
    ATTACK_COOLDOWN_TICKS = 3

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0
        self._last_attack: dict[int, int] = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行捕食更新

        Args:
            world: World 实例
            dt: 时间步长（预留）
        """
        self._tick_counter += 1

        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (predator, pred_energy, pred_space) in world.get_components(
            AnimalComponent, EnergyComponent, SpaceComponent
        ):
            if predator.diet != "carnivore":
                continue

            # 冷却期检查
            last_tick = self._last_attack.get(
                entity.id, -self.ATTACK_COOLDOWN_TICKS
            )
            if self._tick_counter - last_tick < self.ATTACK_COOLDOWN_TICKS:
                continue

            # 只在饥饿时捕食（能量低于 60% 最大值）
            hunger_threshold = getattr(pred_energy, "max_energy", 100.0) * 0.6
            if pred_energy.value >= hunger_threshold:
                continue

            # 搜索附近猎物
            prey_id = self._find_prey(world, space_system, pred_space, predator)
            if prey_id is None:
                continue

            # 执行攻击
            self._execute_attack(world, entity, predator, pred_energy, prey_id)
            self._last_attack[entity.id] = self._tick_counter

    def _find_prey(
        self,
        world: World,
        space_system: SpaceSystem,
        pred_space: SpaceComponent,
        predator: AnimalComponent,
    ) -> int | None:
        """
        在捕食范围内寻找最佳猎物

        优先选择能量最高的食草动物（最肥美）。
        """
        nearby = space_system.query_radius(
            x=pred_space.x, y=pred_space.y, r=predator.grazing_range
        )

        best_prey = None
        best_energy = 0.0

        for candidate_id in nearby:
            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            prey_animal = world.get_component(candidate, AnimalComponent)
            if prey_animal is None:
                continue

            # 只捕食食草动物
            if prey_animal.diet not in ("herbivore",):
                continue

            # 检查猎物是否已有 PendingDeath（避免重复攻击将死猎物）
            if world.get_component(candidate, PendingDeathComponent) is not None:
                continue

            prey_energy = world.get_component(candidate, EnergyComponent)
            if prey_energy is None:
                continue

            # 优先选择能量高的猎物
            if prey_energy.value > best_energy:
                best_energy = prey_energy.value
                best_prey = candidate_id

        return best_prey

    def _execute_attack(
        self,
        world: World,
        predator_id: int,
        predator: AnimalComponent,
        pred_energy: EnergyComponent,
        prey_id: int,
    ) -> None:
        """
        执行攻击逻辑
        """
        # 攻击成功率判定（简化：固定概率 + 随机波动）
        success_rate = self.BASE_SUCCESS_RATE + self._rng.uniform(-0.1, 0.1)
        success_rate = max(0.1, min(0.95, success_rate))

        if self._rng.random() > success_rate:
            logger.debug(
                f"[Predation] E{predator_id} 攻击 E{prey_id} 失败"
            )
            return

        # 对猎物造成伤害
        prey_entity = world.query_entity(prey_id)
        if prey_entity is None:
            return

        prey_energy = world.get_component(prey_entity, EnergyComponent)
        if prey_energy is None:
            return

        damage = self.BASE_DAMAGE * self._rng.uniform(0.8, 1.2)
        prey_energy.value -= damage

        # 能量转移给捕食者
        energy_gain = damage * self.ENERGY_CONVERSION_RATIO
        pred_energy.value = min(
            getattr(pred_energy, "max_energy", 100.0),
            pred_energy.value + energy_gain
        )

        logger.debug(
            f"[Predation] E{predator_id}({predator.species}) 攻击 E{prey_id} "
            f"造成 {damage:.1f} 伤害，获得能量 {energy_gain:.1f}"
        )

        # 如果猎物能量耗尽，标记死亡
        if prey_energy.value <= 0:
            time_component = world.get_time()
            world_time = time_component.total_hours if time_component else 0.0

            if prey_entity is not None:
                world.add_component(
                    prey_entity,
                    PendingDeathComponent(
                        reason="predation",
                        source_system="PredationSystem",
                        priority=8,
                        timestamp=world_time,
                        details=f"predator=E{predator_id}, damage={damage:.1f}",
                    )
                )

            logger.info(
                f"[Predation] E{prey_id} 被 E{predator_id} 捕食致死"
            )

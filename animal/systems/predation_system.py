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
from core.category_component import CategoryComponent
from core.category import EntityCategory
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent

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

    # 攻击参数已去硬编码，改为从基因表型动态推导：
    #   - damage        ← predator.speed_factor × predator.strength
    #   - success_rate  ← predator.speed_factor / prey.speed_factor
    #   - conversion    ← 1.0 - metabolism_rate（低代谢=高转化效率）
    #   - cooldown      ← metabolism_rate 的倒数（高代谢=恢复慢）

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

            # 读取捕食者表型（用于动态推导攻击参数）
            pred_pheno = world.get_component(entity, PhenotypeComponent)
            pred_morph = world.get_component(entity, MorphologyComponent)

            # 从基因推导攻击冷却：高代谢 = 恢复慢 = 长冷却
            metabolism = pred_pheno.get("metabolism_rate", 0.02) if pred_pheno else 0.02
            attack_cooldown = max(1, int(5.0 / (metabolism * 100 + 0.1)))

            # 冷却期检查
            last_tick = self._last_attack.get(entity.id, -attack_cooldown)
            if self._tick_counter - last_tick < attack_cooldown:
                continue

            # 只在饥饿时捕食（能量低于 60% 最大值）
            hunger_threshold = getattr(pred_energy, "max_energy", 100.0) * 0.6
            if pred_energy.value >= hunger_threshold:
                continue

            # 搜索附近猎物
            prey_id = self._find_prey(world, space_system, pred_space, predator)
            if prey_id is None:
                continue

            # 执行攻击（参数由基因动态推导）
            self._execute_attack(
                world, entity, predator, pred_energy, pred_pheno, pred_morph, prey_id
            )
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

            # 通过 CategoryComponent 精确校验：确保是动物实体
            cat = world.get_component(candidate, CategoryComponent)
            if cat is not None and cat.category != EntityCategory.ANIMAL:
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
        pred_pheno: PhenotypeComponent,
        pred_morph: MorphologyComponent,
        prey_id: int,
    ) -> None:
        """
        执行攻击逻辑

        攻击参数全部由基因表型动态推导：
            - 伤害    = 速度因子 × 力量（体重）× 随机波动
            - 成功率 = 捕食者速度 / 猎物速度（速度优势越大越易成功）
            - 转化率 = 1.0 - 代谢率（低代谢=高转化效率）
        """
        prey_entity = world.query_entity(prey_id)
        if prey_entity is None:
            return

        # 读取猎物表型
        prey_pheno = world.get_component(prey_entity, PhenotypeComponent)
        prey_morph = world.get_component(prey_entity, MorphologyComponent)

        # ── 动态推导攻击参数 ──
        # 捕食者速度
        pred_speed = pred_pheno.get("speed_factor", 1.0) if pred_pheno else 1.0
        pred_strength = pred_morph.weight if pred_morph else 10.0

        # 猎物速度
        prey_speed = prey_pheno.get("speed_factor", 1.0) if prey_pheno else 1.0

        # 成功率：速度优势比，随机波动 ±15%
        speed_ratio = pred_speed / max(prey_speed, 0.1)
        success_rate = min(0.95, 0.4 + speed_ratio * 0.3)
        success_rate += self._rng.uniform(-0.15, 0.15)
        success_rate = max(0.05, min(0.98, success_rate))

        if self._rng.random() > success_rate:
            logger.debug(
                f"[Predation] E{predator_id} 攻击 E{prey_id} 失败 "
                f"(成功率 {success_rate:.2f})"
            )
            return

        # 对猎物造成伤害
        prey_energy = world.get_component(prey_entity, EnergyComponent)
        if prey_energy is None:
            return

        # 伤害 = 力量 × 速度 × 随机波动
        damage = pred_strength * pred_speed * self._rng.uniform(0.7, 1.3)
        prey_energy.value -= damage

        # 能量转化率：低代谢 = 高转化效率（类似高效消化系统）
        metabolism = pred_pheno.get("metabolism_rate", 0.02) if pred_pheno else 0.02
        conversion_ratio = max(0.1, min(0.8, 1.0 - metabolism * 10))
        energy_gain = damage * conversion_ratio
        pred_energy.value = min(
            getattr(pred_energy, "max_energy", 100.0),
            pred_energy.value + energy_gain
        )

        logger.debug(
            f"[Predation] E{predator_id}({predator.species}) 攻击 E{prey_id} "
            f"造成 {damage:.1f} 伤害，获得能量 {energy_gain:.1f} "
            f"(速度比 {speed_ratio:.2f}, 转化率 {conversion_ratio:.2f})"
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

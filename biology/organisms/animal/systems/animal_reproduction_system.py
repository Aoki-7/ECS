#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁衍系统（重构版）

处理动物的繁殖行为：
    1. 扫描所有处于成熟期的动物实体
    2. 检查能量是否达到繁殖阈值
    3. 检查冷却期是否已过（使用 ReproductionComponent 替代 dict）
    4. 消耗能量并产生后代
    5. 支持怀孕机制（雌性怀孕 → 分娩）

与 AnimalSocialSystem 的关系：
    - SocialSystem 负责配对（设置 mate_id）
    - ReproductionSystem 在配对成功后执行繁殖
"""

import random

from core.system import System
from core.world import World

from biology.organisms.animal.components.animal_component import AnimalComponent
from biology.organisms.animal.components.animal_reproduction_component import AnimalReproductionComponent
from biology.organisms.animal.components.animal_social_component import AnimalSocialComponent
from biology.organisms.animal.animal_factory import AnimalFactory
from biology.components.genome_component import GenomeComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent
from biology.components.phenotype_component import PhenotypeComponent

import logging

logger = logging.getLogger(__name__)


class AnimalReproductionSystem(System):
    tick_interval = 20

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0

    # ── 静态工具方法（供外部调用） ──

    @staticmethod
    def is_ready(repro: AnimalReproductionComponent, current_tick: int) -> bool:
        """检查是否已过冷却期"""
        return (current_tick - repro.last_reproduction_tick) >= repro.cooldown_ticks

    @staticmethod
    def record_reproduction(repro: AnimalReproductionComponent, current_tick: int) -> None:
        """记录一次繁殖"""
        repro.last_reproduction_tick = current_tick
        repro.reproduction_count += 1

    @staticmethod
    def start_pregnancy(repro: AnimalReproductionComponent, current_tick: int, mate_id: int) -> None:
        """开始怀孕"""
        repro.is_pregnant = True
        repro.pregnancy_tick = current_tick
        repro.mate_id = mate_id

    @staticmethod
    def check_birth_ready(repro: AnimalReproductionComponent, current_tick: int) -> bool:
        """检查是否到分娩时间"""
        if not repro.is_pregnant:
            return False
        return (current_tick - repro.pregnancy_tick) >= repro.pregnancy_duration

    @staticmethod
    def give_birth(repro: AnimalReproductionComponent) -> None:
        """分娩后重置状态"""
        repro.is_pregnant = False
        repro.pregnancy_tick = 0
        repro.mate_id = -1

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行动物繁衍更新"""
        self._tick_counter += 1

        for entity, (animal, repro, energy, lifecycle, genome, space) in list(
            world.get_components(
                AnimalComponent,
                AnimalReproductionComponent,
                EnergyComponent,
                LifeCycleComponent,
                GenomeComponent,
                SpaceComponent,
            )
        ):
            from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
            if not LifeCycleSystem.is_mature(lifecycle):
                continue

            # 处理怀孕分娩
            if repro.is_pregnant and animal.gender == "female":
                if AnimalReproductionSystem.check_birth_ready(repro, self._tick_counter):
                    self._give_birth(world, entity, animal, repro, genome, space)
                continue

            # 检查是否可繁殖
            if not self._can_reproduce(entity, repro, energy):
                continue

            # 获取配偶
            mate_id = self._get_mate_id(world, entity, animal, repro)
            if mate_id is None:
                continue

            # 执行繁殖
            self._reproduce(world, entity, animal, repro, energy, genome, space, mate_id)

    def _can_reproduce(
        self, entity, repro: AnimalReproductionComponent, energy: EnergyComponent
    ) -> bool:
        """检查繁殖条件：冷却期 + 能量阈值"""
        if not AnimalReproductionSystem.is_ready(repro, self._tick_counter):
            return False

        # 能量阈值：至少 30% 最大能量
        threshold = getattr(energy, "max_energy", 100.0) * 0.3
        return energy.value >= threshold

    def _get_mate_id(
        self, world: World, entity, animal: AnimalComponent, repro: AnimalReproductionComponent
    ) -> int | None:
        """获取配偶 ID：优先使用社交组件中的配偶"""
        # 从 AnimalSocialComponent 获取（社交系统负责配对）
        social = world.get_component(entity, AnimalSocialComponent)
        if social and social.mate_id != -1:
            mate = world.query_entity(social.mate_id)
            if mate is not None:
                # 验证配偶是否为异性且成熟
                mate_animal = world.get_component(mate, AnimalComponent)
                if mate_animal and mate_animal.gender != animal.gender:
                    return social.mate_id

        # 从 ReproductionComponent 获取（备用）
        if repro.mate_id != -1:
            mate = world.query_entity(repro.mate_id)
            if mate is not None:
                return repro.mate_id

        return None

    def _reproduce(
        self, world: World, entity, animal: AnimalComponent,
        repro: AnimalReproductionComponent, energy: EnergyComponent,
        genome: GenomeComponent, space: SpaceComponent, mate_id: int
    ) -> None:
        """执行繁殖逻辑"""
        # 动态推导繁殖参数
        pheno = world.get_component(entity, PhenotypeComponent)
        growth = PhenotypeSystem.get(pheno, "growth_partition", 0.4) if pheno else 0.4
        metabolism = PhenotypeSystem.get(pheno, "metabolism_rate", 0.02) if pheno else 0.02

        # 能量消耗
        energy_cost = max(0.1, min(0.5, 0.5 - growth * 0.3))
        energy.value *= (1.0 - energy_cost)

        # 更新冷却期
        repro.cooldown_ticks = max(3, int(30.0 / (metabolism * 100 + 0.5)))
        AnimalReproductionSystem.record_reproduction(repro, self._tick_counter)

        if animal.gender == "female":
            # 雌性进入怀孕状态
            AnimalReproductionSystem.start_pregnancy(repro, self._tick_counter, mate_id)
            logger.debug(
                f"[Reproduction] E{entity.id}({animal.species}) 怀孕，"
                f"配偶 E{mate_id}，冷却期 {repro.cooldown_ticks} ticks"
            )
        else:
            # 雄性直接记录（实际繁殖由雌性执行）
            logger.debug(
                f"[Reproduction] E{entity.id}({animal.species}) 与 E{mate_id} 配对"
            )

    def _give_birth(
        self, world: World, entity, animal: AnimalComponent,
        repro: AnimalReproductionComponent, genome: GenomeComponent, space: SpaceComponent
    ) -> None:
        """分娩产生后代，支持性状遗传与变异，自发物种演化"""
        # 获取配偶的性状
        mate_animal = None
        if repro.mate_id != -1:
            mate_animal = world.get_component(repro.mate_id, AnimalComponent)
        
        # 计算后代位置
        child_x = max(0, space.x + self._rng.randint(-2, 2))
        child_y = max(0, space.y + self._rng.randint(-2, 2))

        # 创建后代
        child = AnimalFactory.create_animal_from_genome(
            world, genome, x=child_x, y=child_y,
            parent_species=animal.species,
            parent_generation=repro.reproduction_count,
        )
        
        # 获取后代动物组件
        child_animal = world.get_component(child, AnimalComponent)
        if not child_animal:
            # 更新父母状态
            repro.give_birth()
            return
        
        # === 性状遗传：融合父母双方的性状 ===
        # 优先融合父母性状，没有配偶则完全继承母亲
        if mate_animal:
            # 体型：父母平均值±5%随机
            child_animal.size = (animal.size + mate_animal.size) / 2 * self._rng.uniform(0.95, 1.05)
            # 肉食偏好：父母平均值±0.1随机
            child_animal.carnivore_preference = (animal.carnivore_preference + mate_animal.carnivore_preference) / 2 + self._rng.uniform(-0.1, 0.1)
            # 移动速度：父母平均值±5%随机
            child_animal.movement_speed = (animal.movement_speed + mate_animal.movement_speed) / 2 * self._rng.uniform(0.95, 1.05)
            # 繁殖率：父母平均值±5%随机
            child_animal.reproduction_rate = (animal.reproduction_rate + mate_animal.reproduction_rate) / 2 * self._rng.uniform(0.95, 1.05)
            # 变异率：父母平均值±10%随机
            child_animal.mutation_rate = (animal.mutation_rate + mate_animal.mutation_rate) / 2 * self._rng.uniform(0.9, 1.1)
            # 父代物种记录父母双方
            child_animal.parent_species = f"{animal.species}_{mate_animal.species}"
        else:
            # 无性繁殖，完全继承母亲
            child_animal.size = animal.size * self._rng.uniform(0.95, 1.05)
            child_animal.carnivore_preference = animal.carnivore_preference + self._rng.uniform(-0.1, 0.1)
            child_animal.movement_speed = animal.movement_speed * self._rng.uniform(0.95, 1.05)
            child_animal.reproduction_rate = animal.reproduction_rate * self._rng.uniform(0.95, 1.05)
            child_animal.mutation_rate = animal.mutation_rate * self._rng.uniform(0.9, 1.1)
            child_animal.parent_species = animal.species
        
        # 限制性状范围
        child_animal.size = max(0.1, child_animal.size)
        child_animal.carnivore_preference = max(0.0, min(1.0, child_animal.carnivore_preference))
        child_animal.movement_speed = max(0.1, child_animal.movement_speed)
        child_animal.reproduction_rate = max(0.01, min(1.0, child_animal.reproduction_rate))
        child_animal.mutation_rate = max(0.001, min(0.2, child_animal.mutation_rate))
        
        # === 随机变异 ===
        child_animal.mutate()
        
        # === 新物种形成检测：与原物种性状差异超过阈值则生成新物种 ===
        original_species = animal.species
        # 计算性状差异度：体型差异+食性差异+速度差异
        size_diff = abs(child_animal.size - animal.size) / max(0.1, animal.size)
        diet_diff = abs(child_animal.carnivore_preference - animal.carnivore_preference)
        speed_diff = abs(child_animal.movement_speed - animal.movement_speed) / max(0.1, animal.movement_speed)
        total_diff = size_diff * 0.4 + diet_diff * 0.4 + speed_diff * 0.2
        
        # 总差异度超过50%则形成新物种
        if total_diff >= 0.5:
            # 根据食性和大小生成新物种名
            if child_animal.carnivore_preference < 0.3:
                diet_prefix = "herbivorous_"
            elif child_animal.carnivore_preference > 0.7:
                diet_prefix = "carnivorous_"
            else:
                diet_prefix = "omnivorous_"
            
            size_suffix = "_giant" if child_animal.size > animal.size * 1.5 else "_dwarf" if child_animal.size < animal.size * 0.7 else ""
            new_species_name = f"{diet_prefix}{original_species}{size_suffix}_{self._rng.randint(100,999)}"
            child_animal.species = new_species_name
            logger.info(f"[Evolution] 新物种诞生：{new_species_name}，与原物种{original_species}差异度{total_diff:.1%}")
        else:
            child_animal.species = original_species

        # 更新父母状态
        repro.give_birth()

        # 记录到社交组件
        social = world.get_component(entity, AnimalSocialComponent)
        if social:
            social.add_offspring(child.id)

        logger.info(
            f"[Reproduction] E{entity.id}({animal.species}) 分娩，"
            f"后代 E{child.id}({child_animal.species}) at ({child_x}, {child_y})，"
            f"食性偏好{child_animal.carnivore_preference:.2f}，体型{child_animal.size:.2f}"
        )
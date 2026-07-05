#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物候系统

v3.6 新增 — P0

职责：
    - 根据环境条件驱动植物物候变化
    - 积温计算、需冷量累积、光周期响应
    - 与季节系统联动

设计原则：
    - 纯物理量驱动：温度、光周期、水分
    - 无硬编码物候期时间，由环境自发决定
    - 支持不同物种的物候差异

依赖：
    - PhenologyComponent
    - EnvironmentComponent
    - SeasonComponent
"""

import logging
from typing import Dict, List, Optional

from core.system import System
from core.world import World

from environment.phenology.components.phenology_component import PhenologyComponent
from environment.environment_component import EnvironmentComponent
from environment.season.season_component import SeasonComponent

logger = logging.getLogger(__name__)


class PhenologySystem(System):
    """
    物候系统

    物理原理：
    - 积温（GDD）：驱动春季物候（发芽→开花）
    - 需冷量：打破休眠的必要条件
    - 光周期：驱动秋季物候（落叶→休眠）
    - 水分胁迫：加速衰老

    每帧更新：
    1. 计算当日积温
    2. 累积需冷量
    3. 检查物候转换条件
    4. 执行物候转换
    """

    tick_interval = 10  # 每10帧执行一次（物候变化较慢）

    # 物理常数
    HOURS_PER_TICK = 0.5  # 每 tick 代表的小时数（根据游戏速度调整）


    # === 业务方法（从 PhenologyComponent 迁移） ===
    @staticmethod
    def calculate_gdd(phenology: PhenologyComponent, temperature: float) -> float:
        """计算生长度日"""
        return max(0.0, temperature - phenology.gdd_base)

    @staticmethod
    def accumulate_chill(phenology: PhenologyComponent,
                         temperature: float, hours: float) -> float:
        """累积需冷量，返回本次增加的小时数"""
        if temperature < 7.2:  # 7.2°C 是标准需冷温度
            phenology.chill_hours += hours
            return hours
        return 0.0

    @staticmethod
    def check_transition(phenology: PhenologyComponent, target_stage: str) -> bool:
        """检查是否可以转换到目标阶段"""
        thresholds = {
            "leafing": 150.0,
            "flowering": 300.0,
            "fruiting": 500.0,
            "senescence": 700.0,
        }
        return phenology.gdd_accumulated >= thresholds.get(target_stage, float('inf'))

    def update(self, world: World, dt: float) -> None:
        """更新物候"""
        for entity, (phenology, env) in world.get_components(
            PhenologyComponent, EnvironmentComponent
        ):
            if phenology is None or env is None:
                continue

            # 1. 计算环境驱动因子
            avg_temp = env.air_temperature
            day_length = env.photoperiod
            soil_moisture = env.soil_moisture

            # 2. 更新积温和需冷量
            self._update_thermal_accumulation(phenology, avg_temp, dt)

            # 3. 检查物候转换
            self._check_phenophase_transition(phenology, env, day_length, soil_moisture)

            # 4. 更新植物生理状态（与植物系统联动）
            self._update_plant_physiology(world, entity, phenology)

    def _update_thermal_accumulation(self, phenology: PhenologyComponent,
                                     temperature: float, dt: float) -> None:
        """更新热积累（积温和需冷量）"""
        hours = dt * self.HOURS_PER_TICK

        # 积温累积（生长季）
        if phenology.phenophase != "dormant":
            gdd = PhenologySystem.calculate_gdd(phenology, temperature)
            phenology.gdd_accumulated += gdd * hours / 24.0  # 转换为日积温

        # 需冷量累积（休眠季）
        if phenology.phenophase == "dormant":
            chill = PhenologySystem.accumulate_chill(phenology, temperature, hours)
            phenology.chill_hours += chill

    def _check_phenophase_transition(self, phenology: PhenologyComponent,
                                     env: EnvironmentComponent,
                                     day_length: float,
                                     soil_moisture: float) -> None:
        """检查物候期转换条件"""
        current = phenology.phenophase

        # 定义物候转换图
        transitions = {
            "dormant": ("budding", self._can_bud),
            "budding": ("leafing", self._can_leaf),
            "leafing": ("flowering", self._can_flower),
            "flowering": ("fruiting", self._can_fruit),
            "fruiting": ("senescence", self._can_senesce),
            "senescence": ("leaf_fall", self._can_leaf_fall),
            "leaf_fall": ("dormant", self._can_dormant),
        }

        if current not in transitions:
            return

        next_phase, condition_fn = transitions[current]

        if condition_fn(phenology, env, day_length, soil_moisture):
            self._transition_to(phenology, next_phase)

    def _can_bud(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                 day_length: float, soil_moisture: float) -> bool:
        """萌芽条件：需冷量满足 + 温度适宜"""
        chill_satisfied = phenology.chill_hours >= phenology.chill_requirement
        temp_ok = env.air_temperature > phenology.gdd_base
        return chill_satisfied and temp_ok

    def _can_leaf(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                  day_length: float, soil_moisture: float) -> bool:
        """展叶条件：积温满足"""
        return PhenologySystem.check_transition(phenology, "leafing")

    def _can_flower(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                    day_length: float, soil_moisture: float) -> bool:
        """开花条件：积温满足 + 水分充足"""
        gdd_ok = PhenologySystem.check_transition(phenology, "flowering")
        water_ok = soil_moisture > 0.3
        return gdd_ok and water_ok

    def _can_fruit(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                   day_length: float, soil_moisture: float) -> bool:
        """结果条件：积温满足"""
        return PhenologySystem.check_transition(phenology, "fruiting")

    def _can_senesce(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                     day_length: float, soil_moisture: float) -> bool:
        """衰老条件：积温满足 或 水分胁迫"""
        gdd_ok = PhenologySystem.check_transition(phenology, "senescence")
        water_stress = soil_moisture < 0.2
        return gdd_ok or water_stress

    def _can_leaf_fall(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                       day_length: float, soil_moisture: float) -> bool:
        """落叶条件：积温满足 或 光周期缩短"""
        gdd_ok = PhenologySystem.check_transition(phenology, "leaf_fall")
        # 光周期缩短（秋季）
        day_length_ok = day_length < 12.0 * (1 - phenology.day_length_sensitivity * 0.5)
        return gdd_ok or day_length_ok

    def _can_dormant(self, phenology: PhenologyComponent, env: EnvironmentComponent,
                     day_length: float, soil_moisture: float) -> bool:
        """休眠条件：温度低于基准"""
        return env.air_temperature < phenology.gdd_base - 5.0

    def _transition_to(self, phenology: PhenologyComponent, new_phase: str) -> None:
        """执行物候转换"""
        old_phase = phenology.phenophase
        phenology.phenophase = new_phase
        phenology.last_transition_tick = 0  # 由外部更新

        # 重置相关累积量
        if new_phase == "dormant":
            phenology.gdd_accumulated = 0.0
            phenology.chill_hours = 0.0

        logger.info(f"[Phenology] 物候转换: {old_phase} → {new_phase}")

    def _update_plant_physiology(self, world: World, entity: int,
                                 phenology: PhenologyComponent) -> None:
        """更新植物生理状态（与植物系统联动）"""
        # 获取植物组件（如果存在）
        from plant.components.plant_component import PlantComponent

        plant = world.get_component(entity, PlantComponent)
        if plant is None:
            return

        # 根据物候期调整植物生理参数
        phase_effects = {
            "dormant": {"growth_rate": 0.0, "photosynthesis": 0.0},
            "budding": {"growth_rate": 0.1, "photosynthesis": 0.2},
            "leafing": {"growth_rate": 0.5, "photosynthesis": 0.6},
            "flowering": {"growth_rate": 0.3, "photosynthesis": 0.8},
            "fruiting": {"growth_rate": 0.2, "photosynthesis": 0.7},
            "senescence": {"growth_rate": 0.0, "photosynthesis": 0.3},
            "leaf_fall": {"growth_rate": 0.0, "photosynthesis": 0.0},
        }

        effects = phase_effects.get(phenology.phenophase, {})

        # 应用效果（如果植物组件支持）
        if hasattr(plant, 'growth_rate'):
            plant.growth_rate = effects.get("growth_rate", plant.growth_rate)
        if hasattr(plant, 'photosynthesis_rate'):
            plant.photosynthesis_rate = effects.get("photosynthesis", plant.photosynthesis_rate)

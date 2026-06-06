#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/nutrient_system.py
@说明:营养代谢系统

从环境吸收 N/P/K 营养，生长消耗营养。
营养缺乏时通过 phenotype 临时降低光合效率。

环境联动：
    - 通过 SpaceComponent 坐标匹配环境网格单元格
    - 环境网格每格 10×10，环境单元格坐标 = 实体坐标 // 10
    - 吸收后环境营养减少，形成资源竞争
"""

from core.system import System
from core.world import World

from biology.components.nutrient_component import NutrientComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.traits.trait import Trait
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent


class NutrientSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    营养代谢系统

    职责：
        1. 从环境单元格吸收 N/P/K
        2. 生长时（growth_pool > 0）消耗营养
        3. 营养缺乏降低光合效率
    """

    # 基础吸收速率
    ABSORPTION_RATE = 0.5
    # 生长消耗系数
    NITROGEN_CONSUMPTION = 0.02
    PHOSPHORUS_CONSUMPTION = 0.01
    POTASSIUM_CONSUMPTION = 0.015

    def __init__(self):
        super().__init__()
        self._env_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行营养代谢更新

        Args:
            world: World 实例
            dt: 时间步长（小时）
        """
        self._build_env_cache(world)

        for entity, (nutrient, pheno, energy, space) in world.get_components(
            NutrientComponent,
            PhenotypeComponent,
            EnergyComponent,
            SpaceComponent,
        ):
            # 吸收营养
            self._absorb_nutrients(nutrient, space, dt)
            # 生长消耗
            self._consume_nutrients(nutrient, energy, dt)
            # 营养缺乏影响
            self._apply_nutrient_stress(nutrient, pheno)

    # -------------------------------------------------
    # 环境缓存
    # -------------------------------------------------

    def _build_env_cache(self, world: World):
        """建立坐标 -> 环境组件的映射（每帧刷新）"""
        self._env_cache = {}
        for _, (env, space) in world.get_components(
            EnvironmentComponent, SpaceComponent
        ):
            # 使用 10x10 网格索引对齐
            gx = int(space.x) // 10
            gy = int(space.y) // 10
            self._env_cache[(gx, gy)] = env

    def _get_env_at(self, space: SpaceComponent):
        """获取指定坐标的环境组件"""
        env_x = int(space.x) // 10
        env_y = int(space.y) // 10
        return self._env_cache.get((env_x, env_y))

    # -------------------------------------------------
    # 吸收
    # -------------------------------------------------

    def _absorb_nutrients(
        self,
        nutrient: NutrientComponent,
        space: SpaceComponent,
        dt: float,
    ):
        """从环境吸收 N/P/K"""
        env = self._get_env_at(space)
        if env is None:
            return

        # 氮
        n_absorb = min(
            env.nitrogen * self.ABSORPTION_RATE * dt * 0.01,
            nutrient.max_nitrogen - nutrient.nitrogen,
        )
        nutrient.nitrogen = min(
            nutrient.max_nitrogen, nutrient.nitrogen + n_absorb
        )
        env.nitrogen = max(0.0, env.nitrogen - n_absorb * 10)

        # 磷
        p_absorb = min(
            env.phosphorus * self.ABSORPTION_RATE * dt * 0.01,
            nutrient.max_phosphorus - nutrient.phosphorus,
        )
        nutrient.phosphorus = min(
            nutrient.max_phosphorus, nutrient.phosphorus + p_absorb
        )
        env.phosphorus = max(0.0, env.phosphorus - p_absorb * 10)

        # 钾
        k_absorb = min(
            env.potassium * self.ABSORPTION_RATE * dt * 0.01,
            nutrient.max_potassium - nutrient.potassium,
        )
        nutrient.potassium = min(
            nutrient.max_potassium, nutrient.potassium + k_absorb
        )
        env.potassium = max(0.0, env.potassium - k_absorb * 10)

    # -------------------------------------------------
    # 消耗
    # -------------------------------------------------

    def _consume_nutrients(
        self,
        nutrient: NutrientComponent,
        energy: EnergyComponent,
        dt: float,
    ):
        """生长消耗营养"""
        growth = energy.growth_pool
        if growth <= 0:
            return

        n_cost = growth * self.NITROGEN_CONSUMPTION
        p_cost = growth * self.PHOSPHORUS_CONSUMPTION
        k_cost = growth * self.POTASSIUM_CONSUMPTION

        # 营养不足时只消耗可用部分
        n_cost = min(n_cost, nutrient.nitrogen)
        p_cost = min(p_cost, nutrient.phosphorus)
        k_cost = min(k_cost, nutrient.potassium)

        nutrient.nitrogen -= n_cost
        nutrient.phosphorus -= p_cost
        nutrient.potassium -= k_cost

    # -------------------------------------------------
    # 胁迫影响
    # -------------------------------------------------

    def _apply_nutrient_stress(
        self,
        nutrient: NutrientComponent,
        pheno: PhenotypeComponent,
    ):
        """营养缺乏降低光合效率"""
        stress = max(
            nutrient.nitrogen_stress,
            nutrient.phosphorus_stress * 0.5,
            nutrient.potassium_stress * 0.3,
        )

        if stress > 0:
            current_photo = pheno.get("max_photosynthesis_rate", 20.0)
            pheno.set_trait(
                Trait(
                    name="max_photosynthesis_rate",
                    value=current_photo * (1.0 - stress * 0.5),
                    source="nutrient_stress",
                )
            )

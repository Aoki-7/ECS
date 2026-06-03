#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物根系吸水系统

通过 RootComponent 从环境网格的 SoilComponent 中吸收水分，
计算植物的水分胁迫并写入 PhenotypeComponent，供 GrowthSystem 使用。

与 GrowthSystem 的配合：
    GrowthSystem 优先读取 phenotype.get("plant_water_stress")，
    若不存在则回退到全局 EnvironmentComponent.water_stress_index。
"""

from core.system import System
from core.world import World

from plant.components.root_component import RootComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent


class PlantWaterUptakeSystem(System):
    tick_interval = 20
    """
    植物根系吸水系统

    职责：
        1. 建立坐标 → SoilComponent 的缓存映射
        2. 遍历带 RootComponent 的植物，查找对应土壤
        3. 根据根系吸水能力从土壤吸收水分
        4. 计算水分胁迫并写入 PhenotypeComponent
    """

    def __init__(self):
        super().__init__()
        self._soil_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行吸水更新

        Args:
            world: World 实例
            dt: 时间步长（小时）
        """
        self._build_soil_cache(world)

        for entity, (root, space, pheno) in world.get_components(
            RootComponent,
            SpaceComponent,
            PhenotypeComponent,
        ):
            soil = self._get_soil_at(space)
            if soil is None:
                continue

            # ---- 吸水 ----
            available = max(0.0, soil.moisture - soil.wilting_point)
            max_uptake = available * root.water_absorption_rate * dt * 0.05
            uptake = min(max_uptake, available)

            soil.moisture = max(soil.wilting_point, soil.moisture - uptake)
            root.current_water_uptake = uptake

            # ---- 水分胁迫计算 ----
            if soil.moisture <= soil.wilting_point:
                stress = 1.0
            elif soil.moisture >= soil.field_capacity:
                stress = 0.0
            else:
                stress = (soil.field_capacity - soil.moisture) / (
                    soil.field_capacity - soil.wilting_point
                )

            # 写入 phenotype，供 GrowthSystem 使用
            pheno.set_trait(
                Trait(
                    name="plant_water_stress",
                    value=min(1.0, stress),
                    source="plant_water_uptake",
                )
            )

    # -------------------------------------------------
    # 土壤缓存
    # -------------------------------------------------

    def _build_soil_cache(self, world: World):
        """建立网格坐标 -> SoilComponent 的映射"""
        self._soil_cache = {}
        for _, (soil, space) in world.get_components(
            SoilComponent, SpaceComponent
        ):
            # 环境网格实体的坐标本身就是网格索引
            gx = int(space.x)
            gy = int(space.y)
            self._soil_cache[(gx, gy)] = soil

    def _get_soil_at(self, space: SpaceComponent):
        """获取植物坐标对应的土壤组件"""
        gx = int(space.x) // 10
        gy = int(space.y) // 10
        return self._soil_cache.get((gx, gy))

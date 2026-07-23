#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物地形适应性系统

根据植物所在位置的地形类型，调整其表型性状中的生长相关参数。

配合模块：
    - environment/terrain/：读取 TerrainComponent
    - plant/：读取 PlantComponent，修改 PhenotypeComponent
"""

from core.system import System
from core.world import World

from biology.organisms.plant.components.plant_component import PlantComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.systems.phenotype_system import PhenotypeSystem
from biology.traits.trait import Trait
from space.space_component import SpaceComponent
from environment.terrain.components.terrain_component import TerrainComponent


class TerrainAdaptationSystem(System):
    tick_interval = 20
    """
    地形适应性系统

    职责：
        1. 建立地形网格缓存
        2. 遍历所有植物，查找对应地形
        3. 根据地形类型计算生长修正因子
        4. 将修正写入 PhenotypeComponent（临时 trait）
    """

    # 地形 → 生长修正因子（乘到 max_photosynthesis_rate 上）
    TERRAIN_GROWTH_MODIFIERS = {
        "plain": 1.0,
        "hill": 0.9,
        "mountain": 0.6,
        "valley": 1.1,
        "forest": 0.85,      # 林下光竞争
        "grassland": 1.05,
        "jungle": 0.8,
        "desert": 0.4,
        "swamp": 0.75,       # 厌氧限制
        "tundra": 0.5,
        "water": 0.0,        # 非水生植物无法生长
        "lake": 0.0,
        "river": 0.0,
        "ocean": 0.0,
    }

    def __init__(self):
        super().__init__()
        self._terrain_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        self._build_terrain_cache(world)

        for entity, (plant, space, pheno) in world.get_components(
            PlantComponent,
            SpaceComponent,
            PhenotypeComponent,
        ):
            terrain = self._get_terrain_at(space)
            if terrain is None:
                continue

            terrain_type = getattr(terrain, "terrain_type", None)
            if terrain_type is None:
                continue

            type_key = str(terrain_type.value)
            modifier = self.TERRAIN_GROWTH_MODIFIERS.get(type_key, 1.0)

            # 坡度额外惩罚（>15° 开始显著影响）
            slope_penalty = 1.0
            if terrain.slope > 15.0:
                slope_penalty = max(0.3, 1.0 - (terrain.slope - 15.0) / 50.0)

            final_modifier = modifier * slope_penalty

            # 读取当前光合速率并修正
            current_photo = PhenotypeSystem.get(pheno, "max_photosynthesis_rate", 20.0)
            adjusted = current_photo * final_modifier

            PhenotypeSystem.set_trait(pheno, 
                Trait(
                    name="max_photosynthesis_rate",
                    value=adjusted,
                    source="terrain_adaptation",
                )
            )

            # 同时写入水分胁迫修正（湿地降低、沙漠增加）
            water_stress_bonus = 0.0
            if type_key in ("desert",):
                water_stress_bonus = 0.3
            elif type_key in ("swamp", "lake", "river"):
                water_stress_bonus = -0.2

            if water_stress_bonus != 0.0:
                current_stress = PhenotypeSystem.get(pheno, "plant_water_stress", 0.0)
                PhenotypeSystem.set_trait(pheno, 
                    Trait(
                        name="plant_water_stress",
                        value=max(0.0, min(1.0, current_stress + water_stress_bonus)),
                        source="terrain_adaptation",
                    )
                )

    # -------------------------------------------------
    # 地形缓存
    # -------------------------------------------------

    def _build_terrain_cache(self, world: World):
        self._terrain_cache = {}
        for _, (terrain, space) in world.get_components(
            TerrainComponent, SpaceComponent
        ):
            # 使用 10x10 网格索引与环境系统对齐
            gx = int(space.x) // 10
            gy = int(space.y) // 10
            self._terrain_cache[(gx, gy)] = terrain

    def _get_terrain_at(self, space: SpaceComponent):
        gx = int(space.x) // 10
        gy = int(space.y) // 10
        return self._terrain_cache.get((gx, gy))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物-环境耦合系统 — 生物活动影响环境连续统

v4.0 实现 — Phase 3

物理模型:
    1. 植被影响热扩散:
       - 植被覆盖率高 → 热扩散阻尼 (已有 VEGETATION_THERMAL_DAMPING)
       - 植被蒸腾 → 局部湿度增加
    2. 动物活动影响土壤:
       - 踩踏 → 土壤紧实度增加 → 渗透降低
       - 挖掘 → 土壤扰动 → 侵蚀增加
    3. 人类建筑影响风场:
       - 建筑挡风 → 风速降低
       - 狭管效应 → 风速增加
    4. 农业活动影响养分:
       - 施肥 → 局部 N/P/K 增加
       - 收割 → 植被覆盖降低

实现细节:
    - 通过 world.get_components() 查询 animal/human 组件
    - 使用 SpaceComponent 定位生物位置
    - 修改环境组件的扩散系数或添加源/汇

参数:
    TRAMPLING_COMPACTION = 0.01 /h (踩踏紧实度增加)
    BUILDING_WIND_SHIELD = 0.5 (建筑挡风系数)
    FERTILIZER_N_BOOST = 10.0 mg/kg (氮肥增量)

与其他模块的关系:
    - continuum/: 修改扩散系数 (植被/建筑影响)
    - animal/: 读取 AnimalComponent (位置/数量)
    - human/: 读取 HumanComponent/ActionComponent (建筑/农业)
    - plant/: 读取植被覆盖 (蒸腾/燃料)

版本: v4.0
"""

import logging
from typing import Dict, Tuple, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    clamp,
    get_neighbor_offsets,
)

from biology.organisms.animal.components.animal_component import AnimalComponent
from human.components.basic.human_component import HumanComponent
from human.components.action.action_component import ActionComponent
from human.components.interaction.gathering_component import GatheringComponent

logger = logging.getLogger(__name__)


class BioEnvironmentCouplingSystem(System):
    """
    生物-环境耦合系统

    调整连续统参数以反映生物活动影响:
    1. 植被影响热扩散和湿度 (蒸腾)
    2. 动物活动影响土壤紧实度 (踩踏)
    3. 人类建筑影响风场 (挡风/狭管)
    4. 农业活动影响养分 (施肥)

    在管线中应运行在 EnvironmentalContinuumSystem 之前，
    作为参数调整步骤。
    """

    tick_interval = 20  # 每20帧执行一次

    # 生物影响参数
    TRAMPLING_COMPACTION = 0.01  # 踩踏紧实度增加 (1/h)
    BUILDING_WIND_SHIELD = 0.5  # 建筑挡风系数
    FERTILIZER_N_BOOST = 10.0   # 氮肥增量 (mg/kg)
    FERTILIZER_P_BOOST = 5.0    # 磷肥增量 (mg/kg)
    FERTILIZER_K_BOOST = 15.0   # 钾肥增量 (mg/kg)
    TRANSPIRATION_RATE = 0.005  # 蒸腾速率 (湿度/h)

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新生物-环境耦合"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 1. 植被影响 (蒸腾/热阻尼)
        self._process_vegetation_effects(world, grid, dt, bounds)

        # 2. 动物活动影响 (土壤紧实度)
        self._process_animal_effects(world, grid, dt, bounds)

        # 3. 人类建筑影响 (风场)
        self._process_human_effects(world, grid, dt, bounds)

        # 4. 农业活动影响 (养分)
        self._process_agriculture_effects(world, grid, dt, bounds)

    def _process_vegetation_effects(self, world: World, grid: Dict, dt: float,
                                     bounds: Optional[Tuple]) -> None:
        """植被影响: 蒸腾增加湿度，热阻尼降低扩散

        实现:
            - 读取 TerrainComponent.vegetation_cover
            - 蒸腾增加局部湿度
            - 热阻尼已在 ThermalDiffusionProcessor 中处理
        """
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None or terrain is None:
                continue

            # 植被蒸腾 → 局部湿度增加
            if terrain.vegetation_cover > 0:
                transpiration = terrain.vegetation_cover * self.TRANSPIRATION_RATE * dt
                env.air_humidity = min(1.0, env.air_humidity + transpiration)

                logger.debug(f"Vegetation effect at {key}: "
                           f"cover={terrain.vegetation_cover:.2f}, "
                           f"humidity+={transpiration:.4f}")

    def _process_animal_effects(self, world: World, grid: Dict, dt: float,
                                bounds: Optional[Tuple]) -> None:
        """动物活动影响: 踩踏增加土壤紧实度

        实现:
            - 查询所有有 AnimalComponent 的实体
            - 根据动物数量和体重增加土壤紧实度
            - 紧实度增加 → 渗透降低 (在 WaterCycleSystem 中处理)
        """
        # 统计每个网格的动物数量
        animal_counts = self._count_animals_per_grid(world, grid)

        for key, count in animal_counts.items():
            if key not in grid:
                continue

            soil = world.get_component(grid[key], SoilComponent)
            if soil is None:
                continue

            # 踩踏增加紧实度
            compaction = count * self.TRAMPLING_COMPACTION * dt
            if hasattr(soil, 'compaction'):
                soil.compaction = min(1.0, soil.compaction + compaction)
            elif hasattr(soil, 'soil_type'):
                # 如果土壤类型是 sand，踩踏后变为 loam
                if soil.soil_type == "sand" and compaction > 0.1:
                    soil.soil_type = "loam"

            logger.debug(f"Animal effect at {key}: "
                       f"count={count}, compaction+={compaction:.4f}")

    def _count_animals_per_grid(self, world: World, grid: Dict) -> Dict[Tuple[int, int], int]:
        """统计每个网格的动物数量

        通过查询所有有 AnimalComponent 的实体，
        使用 SpaceComponent 定位到网格。
        """
        counts = {key: 0 for key in grid.keys()}

        # 查询所有动物实体
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
                continue

            # 检查是否有 AnimalComponent
            animal_comp = world.get_component(entity, AnimalComponent)
            if animal_comp is None:
                continue

            # 定位到网格
            key = (int(space.x), int(space.y))
            if key in counts:
                counts[key] += 1

        return counts

    def _process_human_effects(self, world: World, grid: Dict, dt: float,
                                bounds: Optional[Tuple]) -> None:
        """人类建筑影响: 挡风/狭管效应

        实现:
            - 查询所有有 HumanComponent 的实体
            - 检查是否有建筑活动 (ActionComponent.BUILD)
            - 建筑挡风 → 风速降低
            - 建筑之间的狭管 → 风速增加
        """
        # 统计每个网格的人类数量和建筑活动
        human_data = self._analyze_human_activities(world, grid)

        for key, (count, has_building) in human_data.items():
            if key not in grid:
                continue

            env = world.get_component(grid[key], EnvironmentComponent)
            if env is None:
                continue

            if has_building:
                # 建筑挡风
                env.wind_speed = max(0.0, env.wind_speed * (1.0 - self.BUILDING_WIND_SHIELD))

                # 狭管效应 (检查邻居是否有建筑)
                self._apply_venturi_effect(world, grid, key, env, dt)

            logger.debug(f"Human effect at {key}: "
                       f"count={count}, building={has_building}, "
                       f"wind_speed={env.wind_speed:.2f}")

    def _analyze_human_activities(self, world: World, grid: Dict) -> Dict[Tuple[int, int], Tuple[int, bool]]:
        """分析人类活动

        返回: {grid_key: (human_count, has_building)}
        """
        data = {key: (0, False) for key in grid.keys()}

        # 查询所有人类实体
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
                continue

            # 检查是否有 HumanComponent
            human_comp = world.get_component(entity, HumanComponent)
            if human_comp is None:
                continue

            key = (int(space.x), int(space.y))
            if key not in data:
                continue

            count, has_building = data[key]
            count += 1

            # 检查是否有建筑活动
            action_comp = world.get_component(entity, ActionComponent)
            if action_comp is not None and hasattr(action_comp, 'current_action'):
                if action_comp.current_action.name == "BUILD":
                    has_building = True

            data[key] = (count, has_building)

        return data

    def _apply_venturi_effect(self, world: World, grid: Dict, key: Tuple[int, int],
                              env: EnvironmentComponent, dt: float) -> None:
        """应用狭管效应

        当两个建筑之间的通道变窄时，风速增加。
        简化实现: 检查邻居是否有建筑，如果有则增加风速。
        """
        building_neighbors = 0

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nk = (key[0] + dx, key[1] + dy)
            if nk not in grid:
                continue

            # 检查邻居是否有建筑
            _, has_building = self._analyze_human_activities(world, grid).get(nk, (0, False))
            if has_building:
                building_neighbors += 1

        # 两侧都有建筑 → 狭管效应
        if building_neighbors >= 2:
            venturi_boost = 1.5  # 风速增加 50%
            env.wind_speed *= venturi_boost
            env.wind_speed = min(20.0, env.wind_speed)  # 限制最大风速

    def _process_agriculture_effects(self, world: World, grid: Dict, dt: float,
                                     bounds: Optional[Tuple]) -> None:
        """农业活动影响: 施肥增加养分

        实现:
            - 查询所有有 GatheringComponent 的实体 (采集/农业)
            - 施肥 → 局部 N/P/K 增加
            - 收割 → 植被覆盖降低
        """
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 检查是否有农业活动
            gathering = world.get_component(eid, GatheringComponent)
            if gathering is not None and gathering.resource_type in ["crop", "farm"]:
                # 施肥效果
                env.nitrogen = min(200.0, env.nitrogen + self.FERTILIZER_N_BOOST * dt)
                env.phosphorus = min(100.0, env.phosphorus + self.FERTILIZER_P_BOOST * dt)
                env.potassium = min(200.0, env.potassium + self.FERTILIZER_K_BOOST * dt)

                logger.debug(f"Agriculture effect at {key}: "
                           f"N+={self.FERTILIZER_N_BOOST * dt:.2f}, "
                           f"P+={self.FERTILIZER_P_BOOST * dt:.2f}, "
                           f"K+={self.FERTILIZER_K_BOOST * dt:.2f}")

            # 收割降低植被覆盖
            if gathering is not None and gathering.amount > 0:
                if terrain is not None:
                    harvest_reduction = min(terrain.vegetation_cover, gathering.amount * 0.01)
                    terrain.vegetation_cover = max(0.0, terrain.vegetation_cover - harvest_reduction)

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引"""
        grid = {}
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
                continue
            key = (int(space.x), int(space.y))
            grid[key] = entity
        return grid

    def _compute_bounds(self, grid: Dict) -> Optional[Tuple[int, int, int, int]]:
        """计算网格边界"""
        if not grid:
            return None
        xs = [k[0] for k in grid.keys()]
        ys = [k[1] for k in grid.keys()]
        return min(xs), max(xs), min(ys), max(ys)
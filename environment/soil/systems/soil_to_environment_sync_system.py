#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
土壤-环境养分同步系统

解决 NutrientSystem 与 DecomposerSystem 之间的养分流断裂：
    - DecomposerSystem 向 SoilComponent（土壤网格）释放 N/P/K/有机质
    - NutrientSystem 从 EnvironmentComponent（环境网格）吸收 N/P/K
    - 两者使用不同的组件，导致分解产生的养分无法被植物吸收

本系统每 tick 将 SoilComponent 的养分同步到同网格的 EnvironmentComponent，
打通分解 → 土壤 → 环境 → 植物的完整营养闭环。
"""

import logging

from core.system import System
from core.world import World

from environment.soil.components.soil_component import SoilComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class SoilToEnvironmentSyncSystem(System):
    tick_interval = 5
    """
    土壤-环境养分同步系统

    职责：
        1. 建立土壤网格坐标缓存
        2. 将 SoilComponent 的 N/P/K 同步到同位置的 EnvironmentComponent
        3. 有机质暂存到 EnvironmentComponent.extra["organic_matter"]（供后续扩展）
    """

    # 同步比例（允许部分保留在土壤中，模拟缓释）
    SYNC_RATIO = 0.8

    def __init__(self):
        super().__init__()
        self._env_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        self._build_env_cache(world)

        for _, (soil, space) in world.get_components(SoilComponent, SpaceComponent):
            env = self._get_env_at(space)
            if env is None:
                continue

            # 将土壤养分按比例同步到环境
            env.nitrogen += soil.nitrogen * self.SYNC_RATIO * 0.1
            env.phosphorus += soil.phosphorus * self.SYNC_RATIO * 0.1
            env.potassium += soil.potassium * self.SYNC_RATIO * 0.1

            # 有机质存入 extra（EnvironmentComponent 没有有机质字段）
            env.extra["organic_matter"] = env.extra.get("organic_matter", 0.0) + soil.organic_matter * self.SYNC_RATIO * 0.1

            # 土壤养分相应减少（防止无限累积）
            soil.nitrogen *= (1.0 - self.SYNC_RATIO * 0.1)
            soil.phosphorus *= (1.0 - self.SYNC_RATIO * 0.1)
            soil.potassium *= (1.0 - self.SYNC_RATIO * 0.1)
            soil.organic_matter *= (1.0 - self.SYNC_RATIO * 0.1)

    def _build_env_cache(self, world: World):
        """建立网格坐标 -> EnvironmentComponent 的映射"""
        self._env_cache = {}
        for _, (env, space) in world.get_components(EnvironmentComponent, SpaceComponent):
            self._env_cache[(int(space.x), int(space.y))] = env

    def _get_env_at(self, space: SpaceComponent):
        """获取坐标对应的环境组件"""
        return self._env_cache.get((int(space.x), int(space.y)))
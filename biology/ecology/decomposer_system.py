#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
微生物分解系统

将尸体实体（CorpseComponent）分解为土壤养分，完成生态闭环：
    尸体 → 氮/磷/钾/有机质 → 土壤 → 植物吸收 → 生长

与 CorpseSystem 的关系：
    - CorpseSystem 负责推进 decay_progress（受温度影响）
    - DecomposerSystem 负责根据 decay_progress 释放养分到土壤
    - 两者协同工作：CorpseSystem "腐败"，DecomposerSystem "分解"

注意：
    本系统不创建独立的"微生物实体"，而是将分解过程建模为环境化学过程。
    如需独立的微生物实体，可后续扩展。
"""

import logging

from core.system import System
from core.world import World

from biology.lifecycle.corpse.components.corpse_component import CorpseComponent
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent

logger = logging.getLogger(__name__)


class DecomposerSystem(System):
    tick_interval = 10
    """
    微生物分解系统

    职责：
        1. 扫描所有尸体实体（CorpseComponent）
        2. 查找尸体所在位置的土壤
        3. 根据腐败进度（decay_progress）和尸体类型释放养分
        4. 腐败完全后（decay_progress >= 1.0）销毁尸体实体
    """

    # 各类尸体的基础养分含量（单位：mg/kg）
    NUTRIENT_BASE = {
        "plant": {
            "nitrogen": 20.0,
            "phosphorus": 8.0,
            "potassium": 15.0,
            "organic_matter": 3.0,
        },
        "animal": {
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 30.0,
            "organic_matter": 5.0,
        },
        "human": {
            "nitrogen": 45.0,
            "phosphorus": 18.0,
            "potassium": 30.0,
            "organic_matter": 5.0,
        },
        "unknown": {
            "nitrogen": 30.0,
            "phosphorus": 12.0,
            "potassium": 20.0,
            "organic_matter": 4.0,
        },
    }

    # 每次释放的养分比例（decay_progress 每增加 0.1，释放 10% 的剩余养分）
    RELEASE_RATIO = 0.1

    def __init__(self):
        super().__init__()
        self._soil_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行分解更新

        Args:
            world: World 实例
            dt: 时间步长（预留）
        """
        self._build_soil_cache(world)

        for entity, (corpse, space) in list(
            world.get_components(CorpseComponent, SpaceComponent)
        ):
            if not world.has_entity(entity):
                continue

            # 查找尸体所在位置的土壤
            soil = self._get_soil_at(space)
            if soil is None:
                continue

            # 根据腐败进度计算本次释放的养分
            base_nutrients = self.NUTRIENT_BASE.get(
                corpse.original_type, self.NUTRIENT_BASE["unknown"]
            )

            # 释放量与 decay_progress 成正比
            release_factor = corpse.decay_rate * self.RELEASE_RATIO * 10.0

            # 增加土壤养分
            soil.nitrogen += base_nutrients["nitrogen"] * release_factor
            soil.phosphorus += base_nutrients["phosphorus"] * release_factor
            soil.potassium += base_nutrients["potassium"] * release_factor
            soil.organic_matter += base_nutrients["organic_matter"] * release_factor

            # 腐败完全后销毁尸体
            if corpse.decay_progress >= 1.0:
                world.remove_entity(entity)
                logger.debug(
                    f"[Decomposer] 尸体 E{corpse.original_entity_id}({corpse.original_type}) "
                    f"完全分解，释放养分到土壤 ({int(space.x)}, {int(space.y)})"
                )

    # -------------------------------------------------
    # 土壤缓存
    # -------------------------------------------------

    def _build_soil_cache(self, world: World):
        """建立网格坐标 -> SoilComponent 的映射"""
        self._soil_cache = {}
        for _, (soil, space) in world.get_components(SoilComponent, SpaceComponent):
            gx = int(space.x) // 10
            gy = int(space.y) // 10
            self._soil_cache[(gx, gy)] = soil

    def _get_soil_at(self, space: SpaceComponent):
        """获取尸体坐标对应的土壤组件"""
        gx = int(space.x) // 10
        gy = int(space.y) // 10
        return self._soil_cache.get((gx, gy))

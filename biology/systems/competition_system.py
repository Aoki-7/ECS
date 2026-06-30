#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/competition_system.py
@说明:生态竞争系统

模拟植物间的资源竞争：
    1. 光照竞争：高大植株遮阴，降低周围植株的光响应
    2. 水分竞争：根系范围重叠的植株争夺水分
    3. 密度抑制：过密区域生长受限

竞争结果通过 phenotype 临时 trait 影响后续 GrowthSystem 的计算。
"""

import math
from typing import List, Dict

from core.system import System
from core.world import World

from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait
from space.space_component import SpaceComponent
from core.sqrt_cache import cached_sqrt


class CompetitionSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    生态竞争系统

    职责：
        1. 收集所有竞争者
        2. 两两比较光照与水分竞争
        3. 将竞争结果写入 phenotype（临时 trait）
    """

    def __init__(self):
        super().__init__()

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行竞争计算

        Args:
            world: World 实例
            dt: 时间步长（当前模型与时间无关，预留参数）
        """
        competitors = self._collect_competitors(world)
        self._reset_scores(competitors)
        self._run_competition(competitors)
        self._apply_competition_effects(competitors)

    def _reset_scores(self, competitors: List[Dict]) -> None:
        """重置竞争分数"""
        for c in competitors:
            c["morph"].light_competition_score = 0.0
            c["morph"].water_competition_score = 0.0

    def _run_competition(self, competitors: List[Dict]) -> None:
        """执行两两竞争"""
        for i, c1 in enumerate(competitors):
            for c2 in competitors[i + 1 :]:
                self._compete_pair(c1, c2)

    # -------------------------------------------------
    # 数据收集
    # -------------------------------------------------

    def _collect_competitors(self, world: World) -> List[Dict]:
        """收集所有带竞争组件的实体"""
        competitors = []
        for entity, (morph, pheno, space) in world.get_components(
            MorphologyComponent,
            PhenotypeComponent,
            SpaceComponent,
        ):
            competitors.append(
                {
                    "entity": entity,
                    "morph": morph,
                    "pheno": pheno,
                    "space": space,
                }
            )
        return competitors

    # -------------------------------------------------
    # 竞争逻辑
    # -------------------------------------------------

    def _compete_pair(self, c1: Dict, c2: Dict):
        """两个实体之间的资源竞争"""
        dx = abs(c1["space"].x - c2["space"].x)
        dy = abs(c1["space"].y - c2["space"].y)
        distance = cached_sqrt(dx * dx + dy * dy)
        if distance < 0.1:
            distance = 0.1

        # --- 光照竞争（冠层遮阴）---
        canopy1 = c1["morph"].height * c1["morph"].canopy_radius * 0.1
        canopy2 = c2["morph"].height * c2["morph"].canopy_radius * 0.1
        max_canopy = max(canopy1, canopy2)

        if distance < max_canopy:
            h1 = c1["morph"].height
            h2 = c2["morph"].height

            if h1 > h2:
                # c1 赢，c2 受遮阴
                c1["morph"].light_competition_score += 0.1 * c1[
                    "morph"
                ].competitive_ability
                c2["morph"].light_competition_score += 0.3 * (
                    h2 / max(h1, 1.0)
                )
            elif h2 > h1:
                c2["morph"].light_competition_score += 0.1 * c2[
                    "morph"
                ].competitive_ability
                c1["morph"].light_competition_score += 0.3 * (
                    h1 / max(h2, 1.0)
                )
            else:
                # 高度相同，互相抑制
                c1["morph"].light_competition_score += 0.2
                c2["morph"].light_competition_score += 0.2

        # --- 水分竞争（根系重叠）---
        root1 = c1["morph"].root_radius
        root2 = c2["morph"].root_radius
        max_root = max(root1, root2)

        if distance < max_root:
            if root1 > root2:
                c1["morph"].water_competition_score += 0.1
                c2["morph"].water_competition_score += 0.2
            elif root2 > root1:
                c2["morph"].water_competition_score += 0.1
                c1["morph"].water_competition_score += 0.2
            else:
                c1["morph"].water_competition_score += 0.15
                c2["morph"].water_competition_score += 0.15

    # -------------------------------------------------
    # 竞争结果应用
    # -------------------------------------------------

    def _apply_competition_effects(self, competitors: List[Dict]):
        """将竞争分数转换为 phenotype 的临时惩罚"""
        for c in competitors:
            morph = c["morph"]
            pheno = c["pheno"]

            # 光照竞争失败 → 降低光合速率
            if morph.light_competition_score > 0:
                shade_penalty = min(0.7, morph.light_competition_score * 0.3)
                current_photo = pheno.get("max_photosynthesis_rate", 20.0)
                pheno.set_trait(
                    Trait(
                        name="max_photosynthesis_rate",
                        value=current_photo * (1.0 - shade_penalty),
                        source="competition",
                    )
                )

            # 水分竞争失败 → 降低水分利用效率
            if morph.water_competition_score > 0:
                current_wue = pheno.get("water_use_efficiency", 0.05)
                pheno.set_trait(
                    Trait(
                        name="water_use_efficiency",
                        value=current_wue
                        * (1.0 - min(0.5, morph.water_competition_score * 0.2)),
                        source="competition",
                    )
                )

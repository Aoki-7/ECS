#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
生态平衡监控系统

持续监控生态系统的关键指标：
    - 生物多样性指数（Shannon 指数）
    - 能量金字塔稳定性
    - 种群波动幅度
    - 物质循环效率

当检测到严重失衡时发出警报，供外部系统或人工干预。
"""

import logging
import math
from collections import defaultdict
from core.system import System
from core.world import World

from biology.ecology.components.food_chain_component import FoodChainComponent
from biology.ecology.components.population_component import PopulationComponent
from space.space_component import SpaceComponent
from core.sqrt_cache import cached_sqrt

logger = logging.getLogger(__name__)


class EcologyBalanceSystem(System):
    tick_interval = 100
    """
    生态平衡监控系统

    职责：
        1. 计算生物多样性指数
        2. 监控能量金字塔形状
        3. 检测种群崩溃/爆发
        4. 输出生态健康报告
    """

    # 健康阈值
    MIN_BIODIVERSITY = 0.5   # Shannon 指数最低值
    MAX_POPULATION_VARIANCE = 0.5  # 种群波动最大允许方差

    def __init__(self):
        super().__init__()
        # 历史种群数量，用于计算波动
        self._population_history: list[dict[int, int]] = []
        self._max_history = 10

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行生态平衡评估
        """
        # 1. 统计各物种/营养级数量
        counts = self._count_by_trophic_level(world)
        total = sum(counts.values())

        if total == 0:
            logger.warning("[EcoBalance] 生态系统中无生命体！")
            return

        # 2. 计算 Shannon 多样性指数
        shannon = self._shannon_index(counts, total)

        # 3. 检查能量金字塔
        pyramid_ok = self._check_pyramid(counts)

        # 4. 计算种群波动
        variance = self._calculate_variance(counts)

        # 5. 综合评估
        health_score = self._calculate_health_score(shannon, pyramid_ok, variance)

        # 记录历史
        self._population_history.append(counts)
        if len(self._population_history) > self._max_history:
            self._population_history.pop(0)

        # 输出报告
        level_info = ", ".join(f"L{k}={v}" for k, v in sorted(counts.items()))
        logger.info(
            f"[EcoBalance] 生态健康评分: {health_score:.1f}/100 | "
            f"多样性: {shannon:.2f} | 金字塔: {'✓' if pyramid_ok else '✗'} | "
            f"波动: {variance:.2f} | {level_info}"
        )

        # 告警
        if health_score < 30:
            logger.warning("[EcoBalance] ⚠️ 生态系统严重失衡！需要人工干预")
        elif health_score < 60:
            logger.warning("[EcoBalance] ⚡ 生态系统轻度失衡，建议关注")

    def _count_by_trophic_level(self, world: World) -> dict[int, int]:
        """按营养级统计实体数量"""
        counts = defaultdict(int)
        for entity, (fc,) in world.get_components(FoodChainComponent):
            if not world.has_entity(entity):
                continue
            counts[fc.trophic_level] += 1
        return dict(counts)

    def _shannon_index(self, counts: dict[int, int], total: int) -> float:
        """计算 Shannon 多样性指数"""
        if total <= 1:
            return 0.0
        h = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                h -= p * math.log(p)
        return h

    def _check_pyramid(self, counts: dict[int, int]) -> bool:
        """检查能量金字塔是否为正金字塔（底宽顶窄）"""
        levels = sorted(counts.keys())
        if len(levels) < 2:
            return True
        for i in range(len(levels) - 1):
            lower = counts.get(levels[i], 0)
            upper = counts.get(levels[i + 1], 0)
            # 正常情况下，低营养级数量应多于高营养级
            if lower < upper * 0.5:
                return False
        return True

    def _calculate_variance(self, counts: dict[int, int]) -> float:
        """计算种群数量波动方差"""
        if len(self._population_history) < 2:
            return 0.0

        # 计算各营养级数量的变异系数平均值
        total_var = 0.0
        all_levels = set()
        for hist in self._population_history:
            all_levels.update(hist.keys())

        for level in all_levels:
            series = [h.get(level, 0) for h in self._population_history]
            mean = sum(series) / len(series)
            if mean > 0:
                variance = sum((x - mean) ** 2 for x in series) / len(series)
                cv = cached_sqrt(variance) / mean
                total_var += cv

        return total_var / max(len(all_levels), 1)

    def _calculate_health_score(
        self, shannon: float, pyramid_ok: bool, variance: float
    ) -> float:
        """计算综合健康评分 (0-100)"""
        score = 0.0

        # 多样性得分 (0-40)
        score += min(40, shannon * 20)

        # 金字塔得分 (0-30)
        score += 30 if pyramid_ok else 0

        # 稳定性得分 (0-30)
        if variance < 0.1:
            score += 30
        elif variance < 0.3:
            score += 20
        elif variance < 0.5:
            score += 10
        else:
            score += 0

        return min(100, score)

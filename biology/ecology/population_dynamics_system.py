#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
种群动态系统

基于 Lotka-Volterra 模型，监控和调节种群动态平衡。

当某种群数量偏离理想值时，通过调节出生率和死亡率
来引导种群回归平衡。

模型公式：
    dN/dt = rN(1 - N/K) - αNP + βMN

其中：
    N: 猎物种群数量
    P: 捕食者种群数量
    r: 猎物内禀增长率
    K: 环境承载力
    α: 捕食压力系数
    β: 捕食者转化效率
"""

import logging
from collections import defaultdict
from core.system import System
from core.world import World

from biology.ecology.components.food_chain_component import FoodChainComponent
from biology.ecology.components.population_component import PopulationComponent
from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class PopulationDynamicsSystem(System):
    tick_interval = 50
    """
    种群动态系统

    职责：
        1. 监控各营养级种群数量
        2. 检测种群失衡（爆发/崩溃）
        3. 通过调节 birth_rate 和 death_rate 施加反馈
    """

    # 理想种群比例（生产者 : 初级消费者 : 次级消费者）
    IDEAL_RATIO = {1: 10.0, 2: 3.0, 3: 1.0}

    # 种群失衡阈值
    IMBALANCE_THRESHOLD = 3.0

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行种群动态分析
        """
        # 统计各营养级种群数量
        counts = self._count_by_trophic_level(world)
        total = sum(counts.values())
        if total == 0:
            return

        # 计算各营养级密度
        area = self._estimate_area(world)
        densities = {level: count / area for level, count in counts.items()}

        # 为每个实体更新种群密度
        for entity, (pop, fc) in world.get_components(
            PopulationComponent, FoodChainComponent
        ):
            if not world.has_entity(entity):
                continue
            pop.population_density = densities.get(fc.trophic_level, 0.0)

            # 种群密度超过承载力时增加死亡压力
            if pop.population_density > pop.carrying_capacity * 0.8:
                # 密度制约：密度越高，自然死亡率越高
                excess = pop.population_density / pop.carrying_capacity - 0.8
                pop.death_rate = min(0.3, pop.death_rate + excess * 0.01)
            else:
                # 逐渐恢复基础死亡率
                pop.death_rate = max(0.01, pop.death_rate * 0.99)

        # 检测营养级比例失衡
        if len(counts) >= 2 and 1 in counts and 2 in counts:
            producer_count = max(counts.get(1, 0), 1)
            consumer_count = max(counts.get(2, 0), 1)
            actual_ratio = producer_count / consumer_count
            ideal_ratio = self.IDEAL_RATIO[1] / self.IDEAL_RATIO[2]

            imbalance = actual_ratio / ideal_ratio
            if imbalance > self.IMBALANCE_THRESHOLD:
                logger.info(
                    f"[PopDyn] 生产者过剩: P/C={actual_ratio:.1f} "
                    f"(理想={ideal_ratio:.1f})"
                )
            elif imbalance < 1.0 / self.IMBALANCE_THRESHOLD:
                logger.info(
                    f"[PopDyn] 消费者过剩: P/C={actual_ratio:.1f} "
                    f"(理想={ideal_ratio:.1f})"
                )

        # 记录种群统计
        if logger.isEnabledFor(logging.DEBUG):
            stats = ", ".join(f"L{k}={v}" for k, v in sorted(counts.items()))
            if logger.isEnabledFor(logging.DEBUG):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"[PopDyn] 种群统计: {stats}, 总面积≈{area:.0f}")

    def _count_by_trophic_level(self, world: World) -> dict[int, int]:
        """按营养级统计实体数量"""
        counts = defaultdict(int)
        for entity, (fc,) in world.get_components(FoodChainComponent):
            if not world.has_entity(entity):
                continue
            counts[fc.trophic_level] += 1
        return dict(counts)

    def _estimate_area(self, world: World) -> float:
        """估算生态空间面积（基于实体坐标范围）"""
        coords = []
        for entity, (space,) in world.get_components(SpaceComponent):
            if not world.has_entity(entity):
                continue
            coords.append((space.x, space.y))

        if len(coords) < 2:
            return 1000.0  # 默认面积

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        width = max(xs) - min(xs) + 50
        height = max(ys) - min(ys) + 50
        return width * height

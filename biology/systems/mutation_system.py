#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/mutation_system.py
@说明:变异系统

遍历所有包含 GenomeComponent 的实体，
按每个基因自身的 mutation_rate 概率触发 strength 的随机波动。

与 GenomeComponent.mutate() 的区别：
    - GenomeComponent.mutate() 由外部调用（如繁殖时一次性突变）
    - MutationSystem 作为 ECS 系统每帧运行，模拟持续的环境诱变
"""

import random

from core.system import System
from core.world import World

from biology.components.genome_component import GenomeComponent


class MutationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    变异系统

    职责：
        - 每帧遍历所有含 GenomeComponent 的实体
        - 按基因突变率概率对 strength 做随机扰动

    随机数策略：
        使用局部 random.Random 实例，避免污染全局 random 状态。
        可通过构造函数传入种子以获得可复现的变异序列。
    """

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行变异

        Args:
            world: World 实例
            dt: 时间步长（当前变异模型与时间无关，预留参数）
        """
        for entity, [genome] in world.get_components(GenomeComponent):
            genome: GenomeComponent

            for gene in genome.genes:
                if self._rng.random() < gene.mutation_rate:
                    gene.strength *= self._rng.uniform(0.9, 1.1)

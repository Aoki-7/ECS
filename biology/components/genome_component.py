#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:genome_component.py
@说明:基因组组件，负责存储基因
@时间:2026/05/28
@版本:2.0
'''

import random
from dataclasses import dataclass, field
from typing import Optional

from core.component import Component
from biology.genetics.gene import Gene


@dataclass
class GenomeComponent(Component):
    genes: list = field(default_factory=list)

    def add_gene(self, gene: Gene):
        self.genes.append(gene)

    # ------------------------------------------------
    # 复制（用于繁殖遗传）
    # ------------------------------------------------

    def copy(self) -> "GenomeComponent":
        """
        深度复制整个基因组，每个基因独立复制
        """
        return GenomeComponent(
            genes=[g.copy() for g in self.genes]
        )

    # ------------------------------------------------
    # 变异（用于繁殖时的子代变异）
    # ------------------------------------------------

    def mutate(self, mutation_rate: Optional[float] = None):
        """
        对基因组中所有基因按突变率进行变异

        参数：
            mutation_rate: 覆盖基因自身的 mutation_rate，传入则统一使用该值
        """
        for gene in self.genes:
            effective_rate = mutation_rate if mutation_rate is not None else gene.mutation_rate
            if random.random() < effective_rate:
                # 基因强度波动 (±20%)
                delta = gene.strength * random.uniform(-0.2, 0.2)
                gene.strength += delta
                gene.strength = gene.clamp(gene.strength)

    # ------------------------------------------------
    # 基因交叉（用于有性繁殖）
    # ------------------------------------------------

    def crossover(self, other: "GenomeComponent") -> "GenomeComponent":
        """
        简单单点交叉：在两个基因组的同位置基因之间随机选择

        参数：
            other: 另一个亲本基因组

        返回：
            新的子代基因组
        """
        child = GenomeComponent()

        min_len = min(len(self.genes), len(other.genes))

        for i in range(min_len):
            # 随机选择父本或母本的基因副本
            if random.random() < 0.5:
                child.add_gene(self.genes[i].copy())
            else:
                child.add_gene(other.genes[i].copy())

        # 如果有剩余基因，也复制过来
        for i in range(min_len, len(self.genes)):
            child.add_gene(self.genes[i].copy())

        for i in range(min_len, len(other.genes)):
            child.add_gene(other.genes[i].copy())

        return child

    # ------------------------------------------------
    # 工具方法
    # ------------------------------------------------

    def __len__(self):
        return len(self.genes)

    def __getitem__(self, index):
        return self.genes[index]

    def __repr__(self):
        return f"GenomeComponent(genes={len(self.genes)})"

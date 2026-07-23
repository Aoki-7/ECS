#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
基因组系统

v3.9 新增 — 从 GenomeComponent 迁移业务逻辑。

职责：
    - 基因添加
    - 基因组复制（深拷贝）
    - 基因变异
    - 基因交叉（有性繁殖）
"""

import random
from typing import Optional

from biology.components.genome_component import GenomeComponent
from biology.genetics.gene import Gene


class GenomeSystem:
    """基因组系统 — 静态工具类"""

    @staticmethod
    def add_gene(genome: GenomeComponent, gene: Gene) -> None:
        """添加基因"""
        genome.genes.append(gene)

    @staticmethod
    def copy(genome: GenomeComponent) -> GenomeComponent:
        """深度复制整个基因组"""
        return GenomeComponent(
            genes=[g.copy() for g in genome.genes]
        )

    @staticmethod
    def mutate(genome: GenomeComponent, mutation_rate: Optional[float] = None) -> None:
        """对基因组中所有基因按突变率进行变异"""
        for gene in genome.genes:
            effective_rate = mutation_rate if mutation_rate is not None else gene.mutation_rate
            if random.random() < effective_rate:
                # 基因强度波动 (±20%)
                delta = gene.strength * random.uniform(-0.2, 0.2)
                gene.strength += delta
                gene.strength = gene.clamp(gene.strength)

    @staticmethod
    def crossover(genome_a: GenomeComponent, genome_b: GenomeComponent) -> GenomeComponent:
        """简单单点交叉：在两个基因组的同位置基因之间随机选择"""
        child = GenomeComponent()

        min_len = min(len(genome_a.genes), len(genome_b.genes))

        for i in range(min_len):
            # 随机选择父本或母本的基因副本
            if random.random() < 0.5:
                child.genes.append(genome_a.genes[i].copy())
            else:
                child.genes.append(genome_b.genes[i].copy())

        # 如果有剩余基因，也复制过来
        for i in range(min_len, len(genome_a.genes)):
            child.genes.append(genome_a.genes[i].copy())

        for i in range(min_len, len(genome_b.genes)):
            child.genes.append(genome_b.genes[i].copy())

        return child
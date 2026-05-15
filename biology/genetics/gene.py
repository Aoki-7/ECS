#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gene.py
@说明:基因原子基类
@时间:2026/03/09 13:40:06
@作者:Sherry
@版本:1.0
'''





from dataclasses import dataclass, field
from typing import Dict, Callable
import random


@dataclass
class Gene:
    """
    基因原子

    Attributes
    ----------
    name : str
        基因名称

    expression_target : str
        影响的表型 trait 名称

    strength : float
        基因表达强度

    dominance : float
        显性系数

    mutation_rate : float
        突变概率

    min_value : float
        表达最小值

    max_value : float
        表达最大值

    regulators : dict[str, float]
        调控因子 (其他trait或gene)

    metadata : dict
        扩展字段
    """

    name: str
    expression_target: str

    strength: float
    dominance: float = 1.0
    mutation_rate: float = 0.01

    min_value: float = -float("inf")
    max_value: float = float("inf")

    regulators: Dict[str, float] = field(default_factory=dict)

    metadata: Dict = field(default_factory=dict)

    # 可选表达函数
    expression_fn: Callable[[float], float] | None = None

    # ------------------------------------------------
    # 基因表达
    # ------------------------------------------------

    def express(self) -> float:
        """
        计算基因表达值
        """
        value = self.strength * self.dominance

        if self.expression_fn:
            value = self.expression_fn(value)

        return self.clamp(value)

    # ------------------------------------------------
    # 范围限制
    # ------------------------------------------------

    def clamp(self, value: float) -> float:
        if value < self.min_value:
            return self.min_value
        if value > self.max_value:
            return self.max_value
        return value

    # ------------------------------------------------
    # 突变
    # ------------------------------------------------

    def mutate(self):
        """
        基因突变
        """
        if random.random() > self.mutation_rate:
            return

        # strength 突变
        delta = random.gauss(0, 0.1)
        self.strength += delta

        self.strength = self.clamp(self.strength)

    # ------------------------------------------------
    # 复制（遗传）
    # ------------------------------------------------

    def copy(self) -> "Gene":
        """
        创建基因副本（用于繁殖）
        """
        return Gene(
            name=self.name,
            expression_target=self.expression_target,
            strength=self.strength,
            dominance=self.dominance,
            mutation_rate=self.mutation_rate,
            min_value=self.min_value,
            max_value=self.max_value,
            regulators=self.regulators.copy(),
            metadata=self.metadata.copy(),
            expression_fn=self.expression_fn
        )
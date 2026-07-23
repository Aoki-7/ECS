#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/genetics/gene.py
@说明:基因原子基类

Gene 是遗传信息的最小单位，包含表达目标、表达强度、
显性系数、突变率等属性。由 GenomeComponent 聚合存储，
通过 GeneExpressionSystem 计算表达值后写入 PhenotypeComponent。
"""

from dataclasses import dataclass, field
from typing import Dict, Callable, Optional
import random


@dataclass(slots=True)
class Gene:
    """
    基因原子

    Attributes:
        name: 基因名称，通常用于调试和日志。
        expression_target: 影响的表型 trait 名称，
                           如 "max_photosynthesis_rate", "metabolism_rate"。
        strength: 基因表达强度，是计算 trait 值的核心参数。
        dominance: 显性系数，strength * dominance 为实际表达值。
        mutation_rate: 单次突变概率 (0~1)。
        min_value: 表达最小值约束（默认 -inf）。
        max_value: 表达最大值约束（默认 +inf）。
        regulators: 调控因子，其他 trait/gene 对该基因的影响权重。
        metadata: 扩展字段，供外部系统附加自定义数据。
        expression_fn: 可选的非线性表达函数，对 (strength * dominance) 做变换。
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

        公式：value = strength * dominance
        若配置了 expression_fn，则对结果做非线性变换。
        最后通过 clamp 限制在 [min_value, max_value] 范围内。
        """
        value = self.strength * self.dominance

        if self.expression_fn:
            value = self.expression_fn(value)

        return self.clamp(value)

    # ------------------------------------------------
    # 范围限制
    # ------------------------------------------------

    def clamp(self, value: float) -> float:
        """将值限制在 [min_value, max_value] 范围内"""
        if value < self.min_value:
            return self.min_value
        if value > self.max_value:
            return self.max_value
        return value

    # ------------------------------------------------
    # 突变
    # ------------------------------------------------

    def mutate(self, rng: Optional[random.Random] = None) -> bool:
        """
        基因突变

        以 mutation_rate 的概率触发 strength 的随机波动。
        波动量服从均值为 0、标准差为 0.1 的正态分布。

        Args:
            rng: 可选的局部随机数生成器。传入时可避免污染全局 random 状态。

        Returns:
            是否发生了突变。
        """
        _rng = rng if rng is not None else random

        if _rng.random() > self.mutation_rate:
            return False

        # strength 突变
        delta = _rng.gauss(0, 0.1)
        self.strength += delta

        self.strength = self.clamp(self.strength)
        return True

    # ------------------------------------------------
    # 复制（遗传）
    # ------------------------------------------------

    def copy(self) -> "Gene":
        """
        创建基因副本（用于繁殖）

        深拷贝所有可变字段（regulators, metadata），
        expression_fn 引用保持不变（假设为纯函数或不可变）。
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
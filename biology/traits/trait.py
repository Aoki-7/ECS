#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/traits/trait.py
@说明:性状基类

Trait 表示基因表达后的数值性状，是 Genome → Gene 表达之后的中间层结果。
由 GeneExpressionSystem 写入 PhenotypeComponent，
被 GrowthSystem、EnvironmentSystem、SenescenceSystem 等系统读取。

注意：
    - Trait 不是基因本身，而是"当前表达状态"
    - 每一帧都可能被重新计算
    - 来源标记 (source) 用于区分基因表达、环境调制、系统动态修改等不同来源
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Trait:
    """
    数值性状

    Attributes:
        name: 性状名称（例如: growth_rate, leaf_size）
        value: 当前表达值
        min_value: 可选下界约束（防止出现物理不合理值）
        max_value: 可选上界约束
        source: 来源标记，如 "gene", "environment", "mutation", "system", "senescence"
        auto_clamp: 是否启用自动约束
        weight: 表达权重（用于后期做 dominance / 环境调制）
        mutable: 是否允许被系统修改（用于区分遗传性状和临时性状）
    """

    name: str
    value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    source: str = "gene"
    auto_clamp: bool = True
    weight: float = 1.0
    mutable: bool = True

    def apply_delta(self, delta: float):
        """
        对 Trait 进行增量修改

        常用于：
            - 环境调制
            - 突变叠加
            - 系统动态影响
        """
        if not self.mutable:
            return

        self.value += delta

        if self.auto_clamp:
            self.clamp()

    def clamp(self):
        """
        将 value 限制在 [min_value, max_value] 范围内

        用于防止：
            - 负生长率
            - 无限增长
            - 非物理数值
        """
        if self.min_value is not None:
            self.value = max(self.min_value, self.value)

        if self.max_value is not None:
            self.value = min(self.max_value, self.value)

    def reset(self, new_value: float):
        """重置数值（通常在每帧基因重新表达时使用）"""
        self.value = new_value
        if self.auto_clamp:
            self.clamp()

    def copy(self) -> "Trait":
        """
        返回 Trait 的深拷贝

        用于：
            - 代际遗传快照
            - 状态回溯
        """
        return Trait(
            name=self.name,
            value=self.value,
            min_value=self.min_value,
            max_value=self.max_value,
            source=self.source,
            auto_clamp=self.auto_clamp,
            weight=self.weight,
            mutable=self.mutable
        )

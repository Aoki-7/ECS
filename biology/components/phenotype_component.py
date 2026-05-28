#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/phenotype_component.py
@说明:基因表达组件

作为基因型 (GenomeComponent) 与生理系统之间的中间层，
存储所有 Trait（性状）的当前表达值。
每一帧由 GeneExpressionSystem 根据基因重新计算并写入。

数据结构：
    Entity
    └── PhenotypeComponent
        └── traits: dict[str, Trait]
            ├── max_photosynthesis_rate -> Trait
            ├── metabolism_rate -> Trait
            └── ...
"""

from dataclasses import dataclass

from core.component import Component
from biology.traits.trait import Trait


@dataclass
class PhenotypeComponent(Component):
    """
    表型组件

    存储基因表达后的数值性状集合，供各生理系统读取。
    traits 字典的键为性状名，值为 Trait 对象。
    """

    traits: dict[str, Trait] = None

    def __post_init__(self):
        if self.traits is None:
            self.traits = {}

    def set_trait(self, trait: Trait):
        """设置或覆盖指定性状"""
        self.traits[trait.name] = trait

    def get(self, name: str, default: float = 0.0) -> float:
        """
        获取指定性状的表达值

        Args:
            name: 性状名称
            default: 若性状不存在时返回的默认值

        Returns:
            当前表达值，或 default
        """
        t = self.traits.get(name)
        return t.value if t else default

    def remove_by_source(self, source: str):
        """
        按来源移除性状

        常用于 GeneExpressionSystem 每帧清理旧 gene trait，
        再重新写入新计算结果。

        Args:
            source: 来源标记，如 "gene", "environment", "senescence"
        """
        self.traits = {
            k: v for k, v in self.traits.items()
            if v.source != source
        }

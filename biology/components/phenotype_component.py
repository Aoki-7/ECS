#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/phenotype_component.py
@说明:基因表达组件 - 纯数据版

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
    表型组件 - 纯数据

    存储基因表达后的数值性状集合，供各生理系统读取。
    traits 字典的键为性状名，值为 Trait 对象。
    """

    traits: dict[str, Trait] = None

    def __post_init__(self):
        if self.traits is None:
            self.traits = {}
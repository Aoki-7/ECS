#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物基础标记组件

用于标识动物实体及其基本生态属性。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class AnimalComponent(Component):
    """
    动物组件

    属性:
        species: 物种标识名
        diet: 食性 ("herbivore" 食草, "carnivore" 食肉, "omnivore" 杂食)
        grazing_range: 觅食范围 (cm)
    """
    species: str = "basic"
    diet: str = "herbivore"
    grazing_range: float = 5.0

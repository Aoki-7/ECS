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
        gender: 性别 ("male" 雄性, "female" 雌性)
        age: 当前年龄 (小时)
        max_age: 最大寿命 (小时)
        is_adult: 是否成年
        social_group_id: 所属社交群体 ID (-1 表示独行)
        territory_id: 领地 ID (-1 表示无领地)
    """
    species: str = "basic"
    diet: str = "herbivore"
    grazing_range: float = 5.0
    gender: str = "male"
    age: float = 0.0
    max_age: float = 8760.0  # 默认 1 年
    is_adult: bool = False
    social_group_id: int = -1
    territory_id: int = -1

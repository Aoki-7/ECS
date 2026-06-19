#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
实体分类枚举

v3.9 迁移：从 core/ 移回 identity/，保持 core 层纯粹性。
"""

from enum import Enum, auto


class EntityCategory(Enum):
    """实体主分类枚举"""
    UNKNOWN = auto()
    HUMAN = auto()
    ANIMAL = auto()
    PLANT = auto()
    MICROBE = auto()
    CORPSE = auto()
    FOOD = auto()
    WATER = auto()
    RESOURCE = auto()
    ITEM = auto()
    EQUIPMENT = auto()
    WEATHER = auto()
    TERRAIN = auto()
    SOIL = auto()
    ORG = auto()
    LOCATION = auto()
    BUILDING = auto()
    GARBAGE = auto()
    SYSTEM = auto()
    EVENT = auto()

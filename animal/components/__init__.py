#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Animal 组件包

提供动物实体所需的所有组件类型。
"""

from .animal_component import AnimalComponent
from .animal_needs_component import AnimalNeedsComponent
from .animal_social_component import AnimalSocialComponent
from .animal_memory_component import AnimalMemoryComponent
from .animal_territory_component import AnimalTerritoryComponent
from .animal_reproduction_component import AnimalReproductionComponent
from .animal_perception_component import AnimalPerceptionComponent
from .animal_learning_component import AnimalLearningComponent

__all__ = [
    "AnimalComponent",
    "AnimalNeedsComponent",
    "AnimalSocialComponent",
    "AnimalMemoryComponent",
    "AnimalTerritoryComponent",
    "AnimalReproductionComponent",
    "AnimalPerceptionComponent",
    "AnimalLearningComponent",
]

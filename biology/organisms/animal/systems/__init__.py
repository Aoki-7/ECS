"""
动物系统包 — 觅食、捕食、社交、记忆、领地、迁徙、感知、学习

依赖:
    - animal/
    - core/
    - biology/
    - space/
    - environment/
    - plant/
    - resource/

版本: v4.0
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Animal 系统包

提供动物实体行为的所有系统类型。
"""

from .grazing_system import GrazingSystem
from .predation_system import PredationSystem
from .animal_reproduction_system import AnimalReproductionSystem
from .animal_needs_system import AnimalNeedsSystem
from .animal_social_system import AnimalSocialSystem
from .animal_memory_system import AnimalMemorySystem
from .animal_territory_system import AnimalTerritorySystem
from .animal_migration_system import AnimalMigrationSystem
from .animal_perception_system import AnimalPerceptionSystem
from .animal_learning_system import AnimalLearningSystem

__all__ = [
    "GrazingSystem",
    "PredationSystem",
    "AnimalReproductionSystem",
    "AnimalNeedsSystem",
    "AnimalSocialSystem",
    "AnimalMemorySystem",
    "AnimalTerritorySystem",
    "AnimalMigrationSystem",
    "AnimalPerceptionSystem",
    "AnimalLearningSystem",
]


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
表型系统

提供 PhenotypeComponent 的静态操作方法。
"""

from core.system import System
from core.world import World
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait


class PhenotypeSystem(System):
    """表型系统 - ECS System 版本"""
    tick_interval = 20
    priority = 50

    def update(self, world: World, dt: float = 1.0) -> None:
        """遍历所有带 PhenotypeComponent 的实体，确保 traits 字典已初始化"""
        for entity, (pheno,) in world.get_components(PhenotypeComponent):
            if pheno.traits is None:
                pheno.traits = {}

    @staticmethod
    def set_trait(phenotype: PhenotypeComponent, trait: Trait) -> None:
        """设置或覆盖指定性状"""
        phenotype.traits[trait.name] = trait

    @staticmethod
    def get(phenotype: PhenotypeComponent, name: str, default: float = 0.0) -> float:
        """获取指定性状的表达值"""
        t = phenotype.traits.get(name)
        return t.value if t else default

    @staticmethod
    def remove_by_source(phenotype: PhenotypeComponent, source: str) -> None:
        """按来源移除性状"""
        phenotype.traits = {
            k: v for k, v in phenotype.traits.items()
            if v.source != source
        }

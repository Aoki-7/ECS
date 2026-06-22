#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
表型系统静态方法

提供 PhenotypeComponent 的静态操作方法，供其他系统使用。
"""

from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait


class PhenotypeSystem:
    """表型系统 - 静态方法版本"""

    @staticmethod
    def set_trait(phenotype: PhenotypeComponent, trait: Trait) -> None:
        """设置或覆盖指定性状"""
        if phenotype.traits is None:
            phenotype.traits = {}
        phenotype.traits[trait.name] = trait

    @staticmethod
    def get(phenotype: PhenotypeComponent, name: str, default: float = 0.0) -> float:
        """获取指定性状的表达值"""
        if phenotype.traits is None:
            return default
        t = phenotype.traits.get(name)
        return t.value if t else default

    @staticmethod
    def remove_by_source(phenotype: PhenotypeComponent, source: str) -> None:
        """按来源移除性状"""
        if phenotype.traits is None:
            return
        phenotype.traits = {
            k: v for k, v in phenotype.traits.items()
            if v.source != source
        }

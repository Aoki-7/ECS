
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:phenotype.py
@说明:基因表达组件
@时间:2026/02/27 17:00:04
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component
from biology.traits.trait import Trait


# Entity
#  └── PhenotypeComponent
#       └── traits
#            ├── strength
#            ├── intelligence
#            └── aggression

@dataclass
class PhenotypeComponent(Component):
    traits: dict[str, Trait] = None
    
    def __post_init__(self):
        if self.traits is None:
            self.traits = {}

    def set_trait(self, trait: Trait):
        """设置特征值"""
        self.traits[trait.name] = trait

    def get(self, name: str, default=0.0):
        """获取指定特征的值，如果特征不存在则返回默认值"""
        t = self.traits.get(name)
        return t.value if t else default
    
    def remove_by_source(self, source: str):
        self.traits = {
            k: v for k, v in self.traits.items()
            if v.source != source
        }
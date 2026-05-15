
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:genome_component.py
@说明:基因组组件，负责存储基因
@时间:2026/03/09 13:42:04
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field

from core.component import Component
from biology.genetics.gene import Gene


@dataclass
class GenomeComponent(Component):
    genes: list = field(default_factory=list)

    def add_gene(self, gene: Gene):
        self.genes.append(gene)
    
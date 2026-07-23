#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
基因组组件 — 纯数据版

v3.9 迁移：移除所有业务逻辑方法，迁移到 GenomeSystem。
'''

import random
from dataclasses import dataclass, field
from typing import Optional

from core.component import Component
from biology.genetics.gene import Gene


@dataclass(slots=True)
class GenomeComponent(Component):
    """基因组组件 — 纯数据"""
    genes: list = field(default_factory=list)
    parent_id: Optional[int] = None  # 亲代实体ID

    def __repr__(self):
        return f"GenomeComponent(genes={len(self.genes)})"
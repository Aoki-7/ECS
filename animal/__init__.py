#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:动物实体层
@时间:2026/05/28
'''

from .animal_factory import AnimalFactory
from .presets import SPECIES_PRESETS

__all__ = ["AnimalFactory", "SPECIES_PRESETS"]
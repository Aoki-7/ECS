
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_fertility_component.py
@说明:土壤肥力组件
@时间:2026/03/09 09:30:00
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

@dataclass
class SoilFertilityComponent(Component):
    """
    表示综合养分水平
    （氮磷钾等的抽象）
    """

    fertility: float = 0.7   # 肥力指数 0-1
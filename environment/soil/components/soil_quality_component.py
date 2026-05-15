

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_quality_component.py
@说明:土壤质量组件
@时间:2026/03/09 09:32:21
@作者:Sherry
@版本:1.0
'''


from dataclasses import dataclass

from core.component import Component

@dataclass
class SoilQualityComponent(Component):
    """
    土壤质量组件
    表示：
    - 土壤结构
    - 有机质
    - 污染影响
    影响：
    - 水分保持能力
    - 植物适宜度
    """
    quality: float = 0.8   # 土壤质量 0-1
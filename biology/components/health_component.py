
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:health_component.py
@说明:生命状态组件
@时间:2026/03/13 11:12:40
@作者:Sherry
@版本:1.0
'''
# 已从 human/components/physiological/health_component.py 迁移至此
# 向后兼容导入: from biology.components.health_component import HealthComponent
from dataclasses import dataclass, field
from dataclasses import dataclass

from core.component import Component

@dataclass
class HealthComponent(Component):
    """
        生命状态组件
        Args:
            hp: 当前生命值
            max_hp: 最大生命值
            fatigue: 疲劳值
            injury: 伤害 (疾病 / 损伤 / 中毒)
    """
    hp: float = 100
    max_hp: float = 100
    fatigue: float = 0
    injury: dict = field(default_factory=dict)
    
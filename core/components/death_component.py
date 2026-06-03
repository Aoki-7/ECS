# human/components/death_component.py
#!/usr/bin/env python
# -*- encoding: utf-8 -*-


# 已从 human/components/physiological/death_component.py 迁移至此
# 向后兼容导入: from human.components.physiological.death_component import DeathComponent
from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class DeathComponent(Component):
    """
    死亡状态组件
    用于标记实体的死亡状态
    """
    is_dead: bool = False

# human/components/death_component.py
#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from dataclasses import dataclass

from core.component import Component

@dataclass
class DeathComponent(Component):
    """
    死亡状态组件
    用于标记实体的死亡状态
    """
    is_dead: bool = False

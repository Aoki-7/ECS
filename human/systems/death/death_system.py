#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:death_system.py
@说明:
@时间:2026/03/13 17:01:38
@作者:Sherry
@版本:1.0
'''


from core.system import System
from core.world import World

from biology.components.health_component import HealthComponent
from core.components.death_component import DeathComponent


class DeathSystem(System):
    """
        处理死亡状态的系统。
    """
    def update(self, world: World, dt: float):
        for _, (health, death) in world.get_components(HealthComponent, DeathComponent):
            health: HealthComponent
            death: DeathComponent

            if health.hp <= 0:
                # 标记实体为死亡状态
                death.is_dead = True
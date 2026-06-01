#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_system.py
@说明:
@时间:2026/03/19 16:18:46
@作者:Sherry
@版本:1.0
'''

from core.system import System

from human.components.social.social_component import SocialComponent



class SocialSystem(System):
    tick_interval = 10  # 每10帧执行一次

    def update(self, world, dt: float):

        for entity, [social] in world.get_components(SocialComponent):
            social = social

            # 默认阵营
            if hasattr(social, 'faction'):
                if not social.faction:
                    social.faction = "neutral"

            # 这里可以扩展：
            # - 群体归属
            # - 战争系统
            # - 声望系统
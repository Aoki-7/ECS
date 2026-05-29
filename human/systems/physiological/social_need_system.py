#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_need_system.py
@说明:社交需求系统（拆分自 PhysiologyNeedsSystem）
@时间:2026/05/29
@版本:1.0
'''

from core.system import System
from core.world import World

from biology.components.physiology_needs_component import PhysiologyNeedsComponent


class SocialNeedSystem(System):
    """
    社交需求系统
    只负责社交需求的自然衰减
    """

    SOCIAL_DECAY_RATE = 0.3   # 社交需求衰减 /小时

    def update(self, world: World, dt: float):
        for entity, (needs,) in world.get_components(PhysiologyNeedsComponent):
            needs: PhysiologyNeedsComponent

            needs.social -= self.SOCIAL_DECAY_RATE * dt
            needs.social = max(0.0, min(needs.max_social, needs.social))

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gathering_system.py
@说明:采集系统（已废弃，请使用 human/systems/interaction/gathering_system.py）
@时间:2026/04/15 13:12:18
@作者:Sherry
@版本:1.0
'''

# 注意：此文件已废弃
# 采集系统已移到 human/systems/interaction/gathering_system.py
# 请勿在此文件中进行修改

from core.system import System
from core.world import World

class GatheringSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    已废弃的采集系统
    
    此类仅为向后兼容而保留，实际实现请参考：
    human/systems/interaction/gathering_system.py
    """
    
    def update(self, world: World, dt: float):
        """此系统已移到 interaction 模块，此方法无效"""
        pass


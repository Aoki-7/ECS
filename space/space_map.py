#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:space_map.py
@说明:空间地图
@时间:2026/03/15 20:28:30
@作者:Sherry
@版本:1.0
'''



# ecs/world/space_map.py

class SpaceMap:
    """
    世界空间
    简单的二维空间
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def clamp(self, x: int, y: int):
        """
        防止实体跑出世界
        """
        x = max(0, min(self.width, x))
        y = max(0, min(self.height, y))
        return x, y
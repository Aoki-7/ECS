#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
世界配置组件

集中管理世界级别的硬编码参数，避免魔法值散布在各系统中。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class WorldConfigComponent(Component):
    """
    世界全局配置组件

    挂载到世界实体上，供各系统查询。
    """
    map_width: int = 100       # 地图宽度（x 范围: 0 ~ map_width-1）
    map_height: int = 100      # 地图高度（y 范围: 0 ~ map_height-1）

    def clamp_position(self, x: int, y: int) -> tuple[int, int]:
        """将坐标限制在地图边界内"""
        x = max(0, min(self.map_width - 1, x))
        y = max(0, min(self.map_height - 1, y))
        return x, y

    def random_position(self, margin: int = 0) -> tuple[int, int]:
        """在地图边界内（考虑边距）生成随机坐标"""
        import random
        x = random.randint(margin, self.map_width - 1 - margin)
        y = random.randint(margin, self.map_height - 1 - margin)
        return x, y

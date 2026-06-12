#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldConfigSystem — v4.0 新增

职责：
    - 管理 WorldConfigComponent 的所有业务逻辑
    - 坐标限制、随机位置生成等

设计原则：
    - Component 纯数据，System 处理逻辑
    - 静态工具方法供其他 System 调用
"""

import random
from typing import Tuple

from core.system import System
from core.world import World

from core.components.world_config_component import WorldConfigComponent


class WorldConfigSystem(System):
    """世界配置管理系统"""

    tick_interval = 1  # 每帧执行（可优化为不执行，纯工具类）

    def update(self, world: World, dt: float):
        """配置系统无需每帧更新，但保留接口"""
        pass

    @staticmethod
    def clamp_position(config: WorldConfigComponent, x: int, y: int) -> Tuple[int, int]:
        """将坐标限制在地图边界内"""
        x = max(0, min(config.map_width - 1, x))
        y = max(0, min(config.map_height - 1, y))
        return x, y

    @staticmethod
    def random_position(config: WorldConfigComponent, margin: int = 0) -> Tuple[int, int]:
        """在地图边界内（考虑边距）生成随机坐标"""
        x = random.randint(margin, config.map_width - 1 - margin)
        y = random.randint(margin, config.map_height - 1 - margin)
        return x, y

    @staticmethod
    def is_inside(config: WorldConfigComponent, x: int, y: int) -> bool:
        """检查坐标是否在地图边界内"""
        return 0 <= x < config.map_width and 0 <= y < config.map_height

    @staticmethod
    def get_world_config(world: World) -> WorldConfigComponent:
        """从世界实体获取配置组件"""
        config = world.get_world_component(WorldConfigComponent)
        if config is None:
            # 返回默认配置
            return WorldConfigComponent()
        return config

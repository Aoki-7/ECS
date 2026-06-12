"""
空间系统 — 空间索引、坐标、路径规划、碰撞检测

职责：
    - 均匀网格空间索引（O(1) 插入 / O(k) 查询）
    - A* 路径规划、视线检测、碰撞检测
    - 为所有需要位置信息的系统提供空间查询

依赖：
    - core/

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间系统模块 — 坐标管理与空间索引

职责：
    - SpaceComponent: 为实体赋予二维坐标 (x, y) 和移动速度
    - SpaceSystem: 维护实体位置到稀疏网格的索引，支持高效范围查询
    - SpatialIndex: 基于网格的空间索引，O(1) 更新 + O(覆盖网格数) 范围查询
    - SpaceMap: 地图边界与通行性管理

核心能力：
    - query_radius(x, y, radius): 圆形范围查询，返回范围内所有实体
    - query_rect(x1, y1, x2, y2): 矩形范围查询
    - 自动处理位置 dirty 标记与索引同步

依赖：
    - core/ (Entity, Component, System, World)
    - 被 environment/, human/, biology/ 等几乎所有领域模块依赖
"""

from .space_component import SpaceComponent
from .space_system import SpaceSystem
from .spatial_index import SpatialIndex
from .space_map import SpaceMap

__all__ = [
    "SpaceComponent",
    "SpaceSystem",
    "SpatialIndex",
    "SpaceMap",
]


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空间系统 — 空间索引、坐标、路径规划、碰撞检测

目录结构:
    space/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── space_component.py       # SpaceComponent: 二维坐标 (x, y) + 移动速度
    ├── space_system.py          # SpaceSystem: 空间索引维护 (位置更新/索引同步)
    ├── spatial_index.py         # SpatialIndex: 均匀网格空间索引 (O(1) 插入 / O(k) 查询)
    ├── space_map.py             # SpaceMap: 地图边界与通行性管理
    ├── pathfinding.py           # Pathfinding: A* 路径规划算法
    ├── line_of_sight.py         # LineOfSight: 视线检测 (Bresenham 算法)
    ├── collision_detection.py   # CollisionDetection: 碰撞检测 (网格/圆形)
    └── tests/                   # 空间测试包

核心职责:
    1. 空间索引:
       - SpatialIndex: 均匀网格空间索引
       - O(1) 实体插入/更新 (计算网格坐标 → 直接放入)
       - O(k) 范围查询 (k = 覆盖网格数，与实体总数无关)
       - 自动处理位置 dirty 标记与索引同步

    2. 坐标管理:
       - SpaceComponent: 为实体赋予二维坐标 (x, y) 和移动速度
       - SpaceSystem: 监听位置变化，更新空间索引
       - 支持边界检查 (地图大小限制)

    3. 路径规划:
       - Pathfinding: A* 算法，支持障碍物规避
       - 启发函数: 欧几里得距离
       - 支持地形通行性修正 (山地/水域/森林)

    4. 视线检测:
       - LineOfSight: Bresenham 射线算法
       - 支持障碍物遮挡 (地形/实体)
       - 用于感知系统 (视野计算)

    5. 碰撞检测:
       - CollisionDetection: 网格碰撞 + 圆形碰撞
       - 支持实体间碰撞 (半径重叠检测)
       - 支持实体与地形碰撞 (通行性检查)

    6. 地图管理:
       - SpaceMap: 地图边界、通行性、地形类型
       - 支持动态地图修改 (地形破坏/建造)
       - 与 environment/ 地形系统联动

与其他模块的关系:
    - core/: 依赖 ECS 框架 (Entity/Component/System/World)
    - environment/: 地形数据来自 environment/terrain/
      - 海拔/坡度/地表类型 → 通行性修正
      - 水体/森林/山地 → 移动成本
    - human/: 人类使用 SpaceSystem 进行视野计算、路径规划、移动执行
    - animal/: 动物使用 SpaceSystem 进行领地巡逻、迁徙路径、捕食追踪
    - plant/: 植物使用 SpaceComponent 存储位置 (固定位置)
    - biology/: 生物使用 SpaceComponent 进行位置相关行为 (觅食/繁殖)
    - 几乎所有模块: 任何需要位置信息的系统都依赖 space/

设计原则:
    - O(1) 更新: 空间索引更新必须是常数时间，不能随实体数增长
    - O(k) 查询: 范围查询只遍历覆盖网格，不遍历所有实体
    - 自动同步: 位置变化自动触发索引更新，无需手动调用
    - 边界安全: 所有坐标操作自动检查地图边界

版本: v4.0
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

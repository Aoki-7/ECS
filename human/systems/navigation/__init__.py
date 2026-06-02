#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航系统包 — 路径规划与移动决策

包含：
    - PathfindingSystem : 寻路算法（A* 或类似，考虑地形通行性）
    - NavigationSystem  : 导航决策（目标选择、路径评估、避障）
    - ExplorationSystem : 探索逻辑（未知区域标记、兴趣点生成）

与 space/ 的关系：
    - 使用 SpaceMap 查询地形通行性
    - 使用 SpatialIndex 进行障碍物检测
"""

"""
人类系统 — 最复杂的智能实体（认知、社交、经济、行动流水线） 的 子模块

依赖：
    - human.systems/
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
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


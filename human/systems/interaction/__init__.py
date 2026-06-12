"""
human/systems/interaction 子模块

依赖:
    - human/
    - core/
    - biology/
    - space/
    - environment/
    - memory_layer/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互系统包 — 人类与世界的复杂交互

包含：
    - InteractionSystem : 交互调度（管理交互队列、进度、中断）
    - CraftingSystem    : 制造逻辑（配方检查、材料消耗、产物生成）
    - BuildingSystem    : 建筑逻辑（选址、材料需求、建造进度）

与 civilization/ 的关系：
    - interaction/ 关注个体执行层面的建造/制造
    - civilization/ 关注群体层面的建筑规划和科技发展
"""



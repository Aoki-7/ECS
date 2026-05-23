#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:seek_target_system.py
@说明:通用搜索系统
@时间:2026/03/31 15:18:44
@作者:Sherry
@版本:1.0
'''

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import math

from core.system import System
from core.world import World

from space.space_component import SpaceComponent
from human.components.action.action_component import ActionComponent, ActionType
from human.components.economic.inventory.inventory_component import InventoryComponent

from human.components.abilities.search_component import SearchComponent


class SeekTargetSystem(System):
    """
    通用目标搜索系统

    职责：
    1. 根据 SearchComponent 搜索目标
    2. 只负责“找”和“设目标位置”
    3. 不关心具体是什么（食物/水/人）
    """

    def update(self, world: World, dt):

        seekers = list(world.get_components(
            SpaceComponent,
            ActionComponent,
            InventoryComponent,
            SearchComponent
        ))

        for entity, (space, action, inventory, search) in seekers:
            space: SpaceComponent
            action: ActionComponent
            search: SearchComponent

            # -------------------------
            # 1. 必须处于 SEEK 行为
            # -------------------------
            if action.current_action != ActionType.SEARCH:
                continue

            # -------------------------
            # 2. 获取所有候选目标
            # -------------------------
            candidates = list(world.get_components(
                SpaceComponent,
                search.target_component
            ))

            nearest_entity = None
            nearest_dist = float("inf")
            nearest_pos = None

            # -------------------------
            # 3. 查找最近目标（策略点）
            # -------------------------
            for target_entity, (target_space, target_comp) in candidates:

                dx = target_space.x - space.x
                dy = target_space.y - space.y
                dist = math.hypot(dx, dy)

                if dist > search.max_distance:
                    continue

                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_entity = target_entity
                    nearest_pos = (target_space.x, target_space.y)

            # -------------------------
            # 4. 写回搜索结果
            # -------------------------
            search.result_entity = nearest_entity

            # -------------------------
            # 5. 设置行为（只做最小控制）
            # -------------------------
            if nearest_entity:
                action.current_action = ActionType.MOVE
                action.target = nearest_pos
                action.progress = 0.0
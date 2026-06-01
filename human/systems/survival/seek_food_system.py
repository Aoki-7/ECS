#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:seek_food_system.py
@说明:搜索食物系统
@时间:2026/03/18 15:47:54
@作者:Sherry
@版本:1.0
'''

import math

from core.system import System
from core.world import World

from space.space_component import SpaceComponent
from core.components.action_component import ActionComponent, ActionType
from human.components.economic.inventory.inventory_component import InventoryComponent
from core.components.vision_component import VisionComponent


from resource.food.components.food_component import FoodComponent


class SeekFoodSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    寻找食物系统
    必须组件：空间、行为、物品栏、视野
    1. 必须行为是搜寻食物才会执行
    2. 确定搜到了食物，执行移动行为，和食物的坐标
    """
    def update(self, world: World, dt):

        entities = list(world.get_components(
            SpaceComponent, 
            ActionComponent, 
            InventoryComponent, 
            VisionComponent
        ))

        for entity, (space, action, inventory, vision) in entities:
            space: SpaceComponent
            action: ActionComponent
            inventory: InventoryComponent
            vision: VisionComponent

            # -------------------------
            # 0. 只在行为为SEARCH时触发
            # -------------------------
            if action.current_action != ActionType.SEARCH:
                continue

            # -------------------------
            # 2. 背包有食物 → 停止搜寻（可选）
            # -------------------------
            # if inventory.find(FoodComponent):
            #     action.current_action = ActionType.EAT
            #     action.target = None
            #     action.progress = 0.0
            #     continue

            # -------------------------
            # 3. 寻找最近食物，遍历视野范围内是否有食物
            # -------------------------
            for eid in vision.entity_ids:
                candidate = world.query_entity(eid)
                if candidate is None or not candidate.is_alive():
                    continue
                food = world.get_component(entity=candidate, component_type=FoodComponent)
                
                if food:
                    # -------------------------
                    # 4. 找到食物 → 移动过去
                    # 设定移动的行为，和目标的坐标。
                    # -------------------------
                    food_space = world.get_component(entity=candidate, component_type=SpaceComponent)
                    food_space: SpaceComponent
                    action.current_action = ActionType.MOVE_TO
                    action.target_pos = (food_space.x, food_space.y)
                    action.progress = 0.0
                    break

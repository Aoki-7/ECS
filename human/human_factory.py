#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:human_factory.py
@说明:人类实体工厂
@时间:2026/03/13 13:57:46
@作者:Sherry
@版本:1.1

注意：系统注册由 SimulationLoop 统一管理，
HumanFactory 只负责创建实体和挂载组件。
'''

from core.world import World
from biology.components.gender_component import GenderComponent, Gender
from human.components.economic.inventory.inventory_component import InventoryComponent
from resource.water.water_factory import WaterFactory
from space.space_component import SpaceComponent
import random



class HumanFactory:

    @staticmethod
    def create_human(world: World, name, x, y):
        """
        创建单个Human实体

        Args:
            world: World实例
            name: 实体名称
            x: x坐标
            y: y坐标

        Returns:
            创建的实体
        """
        entity = world.create_entity()

        # 使用HumanEntity模板创建组件
        from human.entities.human_entity import HumanEntity
        HumanEntity.create_components(
            world, 
            entity, 
            name=name,
            x=x, 
            y=y,
            gender=random.choice([Gender.MALE, Gender.FEMALE])
        )

        # 为人类添加初始饮水（小型水源，可放入背包直接饮用）
        # 创建一个纯背包水实体（无 SpaceComponent，不出现在地图上）
        water_bottle = world.create_entity()
        from resource.water.components.water_component import WaterComponent
        water_amount = random.uniform(60, 120)
        world.add_component(water_bottle, WaterComponent(
            amount=water_amount, temperature=20.0, purity=1.0
        ))
        from identity.name_component import NameComponent
        world.add_component(water_bottle, NameComponent(name="淡水", category="water"))
        from resource.components.resource_component import ResourceComponent
        world.add_component(water_bottle, ResourceComponent(
            resource_type="water", amount=water_amount
        ))
        inventory = world.get_component(entity, InventoryComponent)
        if inventory is not None:
            inventory.add(water_bottle)

        # 为人类添加初始食物
        food_ration = world.create_entity()
        from resource.food.components.food_component import FoodComponent
        food_amount = random.uniform(20, 40)
        world.add_component(food_ration, FoodComponent(amount=food_amount))
        world.add_component(food_ration, NameComponent(name="浆果", category="food"))
        world.add_component(food_ration, ResourceComponent(
            resource_type="food", amount=food_amount
        ))
        if inventory is not None:
            inventory.add(food_ration)

        return entity

    @staticmethod
    def create_batch(world: World, count: int, **kwargs):
        """
        批量创建Human实体

        Args:
            world: World实例
            count: 要创建的实体数量
            **kwargs: 组件初始化参数

        Returns:
            List[Entity]: 创建的实体列表
        """
        from human.entities.human_entity import HumanEntity
        return HumanEntity.create_batch(world, count, **kwargs)

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:water_factory.py
@说明:水工厂类
@时间:2026/04/13
@作者:GitHub Copilot
@版本:1.1
'''

from identity.name_component import NameComponent
from resource.water.components.water_component import WaterComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent

from core.world import World
from identity.category_component import CategoryComponent
from identity.category import EntityCategory
from identity.subcategory import WaterSubCategory


class WaterFactory:
    """水工厂类"""

    @staticmethod
    def create_water(world: World, x, y, amount=100.0, temperature: float = 20.0, purity: float = 1.0):
        """
        创建水实体

        Args:
            world: 世界对象
            x: X坐标
            y: Y坐标
            amount: 水量
            temperature: 水温（摄氏度）
            purity: 纯净度 [0,1]

        Returns:
            Entity: 创建的水实体
        """
        entity = world.create_entity()

        space = SpaceComponent(x=x, y=y)
        world.add_component(entity, space)
        # SpaceComponent自动注册到SpaceSystem

        water_component = WaterComponent(amount=amount, temperature=temperature, purity=purity)
        world.add_component(entity, water_component)

        world.add_component(entity, NameComponent(name="水", category="water"))
        world.add_component(entity, ResourceComponent(resource_type="water", amount=amount))

        # 分类组件
        if purity < 0.5:
            subcategory = WaterSubCategory.POLLUTED
        elif temperature > 40:
            subcategory = WaterSubCategory.HOT
        elif temperature < 5:
            subcategory = WaterSubCategory.COLD
        else:
            subcategory = WaterSubCategory.CLEAN
        world.add_component(entity, CategoryComponent(
            category=EntityCategory.WATER,
            subcategory=subcategory,
        ))

        return entity

    @staticmethod
    def create_clean_water(world: World, x, y):
        """创建干净的水"""
        return WaterFactory.create_water(world, x, y, temperature=20.0, purity=1.0)

    @staticmethod
    def create_polluted_water(world: World, x, y):
        """创建污染的水"""
        return WaterFactory.create_water(world, x, y, temperature=25.0, purity=0.3)

    @staticmethod
    def create_hot_water(world: World, x, y):
        """创建热水"""
        return WaterFactory.create_water(world, x, y, temperature=80.0, purity=0.9)

    @staticmethod
    def create_cold_water(world: World, x, y):
        """创建冷水"""
        return WaterFactory.create_water(world, x, y, temperature=5.0, purity=0.95)
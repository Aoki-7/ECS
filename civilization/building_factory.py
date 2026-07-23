#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑工厂

创建建筑实体并挂载组件。

v3.0.1 新增 — 建筑实体化
"""

from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent
from space.collision_system import ColliderComponent, ObstacleComponent
from civilization.components.building_component import (
    BuildingComponent, BuildingInventoryComponent
)


class BuildingFactory:
    """建筑工厂"""

    # 建筑预设
    BUILDING_PRESETS = {
        "hut": {
            "durability": 100.0,
            "capacity": 4,
            "radius": 2.0,
            "blocks_movement": True,
            "blocks_vision": False,
        },
        "workshop": {
            "durability": 150.0,
            "capacity": 2,
            "radius": 2.5,
            "blocks_movement": True,
            "blocks_vision": False,
        },
        "storage": {
            "durability": 200.0,
            "capacity": 0,
            "radius": 2.0,
            "blocks_movement": True,
            "blocks_vision": False,
        },
        "farm": {
            "durability": 80.0,
            "capacity": 0,
            "radius": 3.0,
            "blocks_movement": False,  # 农场不阻挡移动
            "blocks_vision": False,
        },
    }

    @classmethod
    def create_building(
        cls,
        world: World,
        building_type: str,
        x: int,
        y: int,
        owner_id: int = -1,
    ) -> Entity:
        """
        创建建筑实体

        Args:
            world: World 实例
            building_type: 建筑类型 (hut/workshop/storage/farm)
            x, y: 位置坐标
            owner_id: 所有者 ID

        Returns:
            建筑实体
        """
        preset = cls.BUILDING_PRESETS.get(building_type, cls.BUILDING_PRESETS["hut"])

        entity = world.create_entity()

        # 空间组件
        world.add_component(entity, SpaceComponent(x=x, y=y))

        # 碰撞体（建筑占据空间）
        world.add_component(entity, ColliderComponent(
            radius=preset["radius"],
            is_solid=True,
            layer=1,  # 建筑层
            mask=0xFFFFFFFF,
        ))

        # 障碍物（阻挡移动）
        if preset["blocks_movement"]:
            world.add_component(entity, ObstacleComponent(
                obstacle_type=building_type,
                blocks_movement=True,
                blocks_vision=preset["blocks_vision"],
            ))

        # 建筑组件
        world.add_component(entity, BuildingComponent(
            building_type=building_type,
            owner_id=owner_id,
            durability=preset["durability"],
            max_durability=preset["durability"],
            capacity=preset["capacity"],
        ))

        # 存储建筑添加库存组件
        if building_type == "storage":
            world.add_component(entity, BuildingInventoryComponent(max_items=50))

        return entity

    @classmethod
    def create_hut(cls, world: World, x: int, y: int, owner_id: int = -1) -> Entity:
        """创建棚屋"""
        return cls.create_building(world, "hut", x, y, owner_id)

    @classmethod
    def create_workshop(cls, world: World, x: int, y: int, owner_id: int = -1) -> Entity:
        """创建工坊"""
        return cls.create_building(world, "workshop", x, y, owner_id)

    @classmethod
    def create_storage(cls, world: World, x: int, y: int, owner_id: int = -1) -> Entity:
        """创建仓库"""
        return cls.create_building(world, "storage", x, y, owner_id)

    @classmethod
    def create_farm(cls, world: World, x: int, y: int, owner_id: int = -1) -> Entity:
        """创建农场"""
        return cls.create_building(world, "farm", x, y, owner_id)
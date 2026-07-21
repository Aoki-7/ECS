#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石生成系统：在地图上随机生成矿石矿点（新版，支持扩展）
"""
import logging
import random
from core.system import System
from core.world import World
from resource.ore.components.base_ore_component import BaseOreComponent, OreHardness, OreRarity
from resource.ore.components.ore_type_component import OreTypeComponent
from resource.ore.components.ore_property_component import OrePropertyComponent
from resource.ore.ore_registry import ore_registry
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)

class OreGenerationSystem(System):
    """矿石生成系统"""
    tick_interval = 500  # 每500帧生成一次矿石

    def update(self, world: World, dt: float) -> None:
        """更新矿石生成"""
        self._generate_random_ore(world)

    def _generate_random_ore(self, world: World):
        """随机生成一个矿石矿点"""
        # 获取所有已注册的矿石类型
        ore_types = ore_registry.get_all_ore_types()
        if not ore_types:
            return

        # 按生成概率加权选择矿石类型
        weights = []
        for ore_type_id in ore_types:
            config = ore_registry.get_ore_config(ore_type_id)
            weights.append(config.generation_probability if config else 0.1)

        selected_ore_id = random.choices(ore_types, weights=weights)[0]
        config = ore_registry.get_ore_config(selected_ore_id)
        if config is None:
            return

        # 随机生成属性
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        # 根据稀有度生成品质
        if config.rarity == OreRarity.COMMON:
            quality = random.choices([0.5, 0.7, 0.9], weights=[0.5, 0.3, 0.2])[0]
        elif config.rarity == OreRarity.UNCOMMON:
            quality = random.choices([0.6, 0.8, 0.95], weights=[0.3, 0.5, 0.2])[0]
        else:
            quality = random.choices([0.7, 0.9, 1.0], weights=[0.2, 0.5, 0.3])[0]

        # 计算储量和深度
        min_depth, max_depth = config.depth_range
        depth = random.uniform(min_depth, max_depth)
        reserves = config.base_reserve * quality

        # 创建矿石实体
        ore_entity = world.create_entity()
        # 添加基础矿石组件
        world.add_component(ore_entity, BaseOreComponent(
            total_reserves=reserves,
            current_amount=reserves,
            base_harvest_rate=2.0 * quality,
            hardness=config.hardness,
            rarity=config.rarity,
            depth=depth,
        ))
        # 添加矿石类型组件
        world.add_component(ore_entity, OreTypeComponent(ore_type_id=selected_ore_id))
        # 添加矿石属性组件
        world.add_component(ore_entity, OrePropertyComponent(ore_type_id=selected_ore_id))
        # 添加位置组件
        world.add_component(ore_entity, SpaceComponent(x=x, y=y, layer=0))

        logger.info(f"[OreGeneration] 生成矿石: {config.name} (品质:{quality:.2f}, 储量:{reserves:.1f}, 位置:({x:.1f},{y:.1f}))")

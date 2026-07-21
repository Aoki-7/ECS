#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展RL系统测试：测试更多动作元件、动作组合学习和多智能体协作
"""
import pytest
import numpy as np
from core.world import World
from human.rl.action_primitives import ActionPrimitive, ActionSequence, ActionPrimitiveType, get_action_primitive
from human.rl.hierarchical_rl_intent_system import HierarchicalRLIntentSystem
from human.components.cognitive.intent_component import IntentComponent, IntentType
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from core.components.world_config_component import WorldConfigComponent

class TestExtendedActionPrimitives:
    """扩展动作元件测试"""
    def test_equip_action(self):
        """测试装备工具动作"""
        world = World()
        entity_id = world.create_entity()
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
        world.add_component(entity_id, InventoryComponent())
        world.add_component(entity_id, ToolInventoryComponent())
        # 添加工具到库存
        inventory = world.get_component(entity_id, InventoryComponent)
        item_id = hash("axe")
        inventory.items[item_id] = 1.0
        # 创建装备动作
        action = get_action_primitive(ActionPrimitiveType.EQUIP, item_id=item_id)
        assert action is not None
        assert action.type == ActionPrimitiveType.EQUIP
        success = action.execute(world, entity_id)
        assert success

    def test_gather_action(self):
        """测试采集资源动作"""
        world = World()
        entity_id = world.create_entity()
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from resource.components.resource_component import ResourceComponent
        world.add_component(entity_id, InventoryComponent())
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        # 创建资源实体
        resource_entity = world.create_entity()
        world.add_component(resource_entity, ResourceComponent(resource_type="food", amount=10.0))
        world.add_component(resource_entity, SpaceComponent(x=1, y=1))
        # 创建采集动作
        action = get_action_primitive(ActionPrimitiveType.GATHER, target_entity=resource_entity)
        assert action is not None
        assert action.type == ActionPrimitiveType.GATHER
        success = action.execute(world, entity_id)
        assert success
        # 检查资源是否被采集
        resource = world.get_component(resource_entity, ResourceComponent)
        assert resource.amount < 10.0

    def test_cooperate_action(self):
        """测试协作动作"""
        world = World()
        entity1 = world.create_entity()
        entity2 = world.create_entity()
        from human.components.economic.inventory.inventory_component import InventoryComponent
        world.add_component(entity1, InventoryComponent())
        world.add_component(entity2, InventoryComponent())
        world.add_component(entity1, SpaceComponent(x=0, y=0))
        world.add_component(entity2, SpaceComponent(x=2, y=2))
        # 创建协作动作
        action = get_action_primitive(ActionPrimitiveType.COOPERATE, target_entity=entity2, task="gather")
        assert action is not None
        assert action.type == ActionPrimitiveType.COOPERATE
        success = action.execute(world, entity1)
        assert success
        # 检查双方是否都获得资源
        inv1 = world.get_component(entity1, InventoryComponent)
        inv2 = world.get_component(entity2, InventoryComponent)
        assert len(inv1.items) > 0
        assert len(inv2.items) > 0

class TestActionCombinationLearning:
    """动作组合学习测试"""
    def test_hierarchical_rl_system(self):
        """测试分层RL系统自动学习动作组合"""
        world = World()
        # 添加配置，启用RL意图系统
        world_entity = world.get_world_entity()
        world.add_component(world_entity, WorldConfigComponent(use_rl_intent=True, rl_training=True))
        # 创建人类实体
        entity_id = world.create_entity()
        world.add_component(entity_id, HumanComponent())
        world.add_component(entity_id, PhysiologyNeedsComponent(hunger=80, thirst=30, energy=50))
        world.add_component(entity_id, IntentComponent())
        world.add_component(entity_id, SpaceComponent(x=0, y=0))
        world.add_component(entity_id, MemoryComponent())
        # 创建分层RL系统
        rl_system = HierarchicalRLIntentSystem(training=True)
        rl_system.update(world, 1.0)
        # 验证意图已更新
        intent = world.get_component(entity_id, IntentComponent)
        assert intent.intent is not None

class TestMultiAgentCooperation:
    """多智能体协作测试"""
    def test_multi_agent_cooperation(self):
        """测试多个人类协作"""
        world = World()
        # 添加配置，启用RL意图系统
        world_entity = world.get_world_entity()
        world.add_component(world_entity, WorldConfigComponent(use_rl_intent=True, rl_training=True))
        # 创建多个人类实体
        entities = []
        for i in range(3):
            entity_id = world.create_entity()
            world.add_component(entity_id, HumanComponent())
            world.add_component(entity_id, PhysiologyNeedsComponent(hunger=50, thirst=50, energy=80))
            world.add_component(entity_id, IntentComponent())
            world.add_component(entity_id, SpaceComponent(x=i*2, y=i*2))
            world.add_component(entity_id, MemoryComponent())
            entities.append(entity_id)
        # 创建分层RL系统
        rl_system = HierarchicalRLIntentSystem(training=True)
        rl_system.update(world, 1.0)
        # 验证所有实体都有意图
        for entity_id in entities:
            intent = world.get_component(entity_id, IntentComponent)
            assert intent.intent is not None

if __name__ == "__main__":
    pytest.main([__file__])

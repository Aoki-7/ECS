#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动作元件系统：定义最基础的原子动作，可组合成复杂动作
"""
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
import numpy as np
from core.world import World

class ActionPrimitiveType(Enum):
    """动作元件类型"""
    # 移动类
    MOVE_TO = auto()          # 移动到指定位置
    MOVE_TOWARDS = auto()     # 向目标移动
    MOVE_AWAY = auto()        # 远离目标
    # 交互类
    GRAB = auto()             # 抓取实体
    RELEASE = auto()          # 释放实体
    USE = auto()              # 使用物品
    CONSUME = auto()          # 消耗物品（吃/喝）
    # 生存类
    REST = auto()             # 休息
    SLEEP = auto()            # 睡眠
    HEAL = auto()             # 治疗
    # 社交类
    SOCIALIZE = auto()        # 社交
    COMMUNICATE = auto()      # 沟通
    TRADE = auto()            # 交易
    TEACH = auto()            # 教学
    LEARN = auto()            # 学习
    COOPERATE = auto()        # 协作
    # 战斗类
    ATTACK = auto()           # 攻击
    DEFEND = auto()           # 防御
    FLEE = auto()             # 逃跑
    # 建造类
    BUILD = auto()            # 建造
    CRAFT = auto()            # 制作
    GATHER = auto()           # 采集
    PROCESS = auto()          # 加工（将原材料加工成成品）
    REPAIR = auto()           # 修理
    # 工具类
    EQUIP = auto()            # 装备工具
    UNEQUIP = auto()          # 卸下工具
    # 探索类
    EXPLORE = auto()          # 探索
    INVESTIGATE = auto()      # 调查
    MAP = auto()              # 绘制地图
    # 其他
    PLANT = auto()            # 种植
    HARVEST = auto()          # 收获
    FISH = auto()             # 钓鱼
    HUNT = auto()             # 狩猎
    COOK = auto()             # 烹饪

@dataclass
class ActionPrimitive:
    """动作元件：最基础的原子动作"""
    type: ActionPrimitiveType
    target_entity: Optional[int] = None      # 目标实体ID
    target_position: Optional[Tuple[float, float]] = None  # 目标位置
    item_id: Optional[int] = None            # 物品ID
    parameters: Dict[str, Any] = field(default_factory=dict)  # 额外参数
    duration: float = 1.0                    # 动作持续时间
    cost: float = 0.0                        # 动作成本（能量/时间）
    preconditions: List[Callable] = field(default_factory=list)  # 前置条件
    effects: List[Callable] = field(default_factory=list)        # 动作效果

    def can_execute(self, world: World, entity_id: int) -> bool:
        """检查动作是否可以执行"""
        for precondition in self.preconditions:
            if not precondition(world, entity_id, self):
                return False
        return True

    def execute(self, world: World, entity_id: int) -> bool:
        """执行动作"""
        if not self.can_execute(world, entity_id):
            return False
        for effect in self.effects:
            effect(world, entity_id, self)
        return True

    def __hash__(self):
        """用于Q表键的哈希"""
        return hash((self.type, self.target_entity, self.target_position, self.item_id))

@dataclass
class ActionSequence:
    """动作序列：由动作元件组合而成的复杂动作"""
    primitives: List[ActionPrimitive] = field(default_factory=list)
    current_index: int = 0
    is_complete: bool = False
    is_failed: bool = False

    def current_primitive(self) -> Optional[ActionPrimitive]:
        """获取当前要执行的动作元件"""
        if self.current_index < len(self.primitives):
            return self.primitives[self.current_index]
        return None

    def advance(self):
        """前进到下一个动作元件"""
        self.current_index += 1
        if self.current_index >= len(self.primitives):
            self.is_complete = True

    def fail(self):
        """标记动作序列失败"""
        self.is_failed = True

    def reset(self):
        """重置动作序列"""
        self.current_index = 0
        self.is_complete = False
        self.is_failed = False

# 预定义的基础动作元件工厂函数
def create_move_to_action(x: float, y: float) -> ActionPrimitive:
    """创建移动到指定位置的动作"""
    def move_precondition(world, entity_id, action):
        # 检查是否可以移动
        return True

    def move_effect(world, entity_id, action):
        # 执行移动
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        if pos:
            pos.x, pos.y = action.target_position

    return ActionPrimitive(
        type=ActionPrimitiveType.MOVE_TO,
        target_position=(x, y),
        duration=2.0,
        cost=1.0,
        preconditions=[move_precondition],
        effects=[move_effect]
    )

def create_grab_action(target_entity: int) -> ActionPrimitive:
    """创建抓取实体的动作"""
    def grab_precondition(world, entity_id, action):
        # 检查目标是否存在，距离是否足够近
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        target_pos = world.get_component(action.target_entity, SpaceComponent)
        if not pos or not target_pos:
            return False
        distance = ((pos.x - target_pos.x)**2 + (pos.y - target_pos.y)**2)**0.5
        return distance <= 2.0  # 抓取距离

    def grab_effect(world, entity_id, action):
        # 执行抓取
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        if inventory:
            # 将目标加入库存
            item_key = hash(action.target_entity)
            inventory.items[item_key] = inventory.items.get(item_key, 0.0) + 1.0

    return ActionPrimitive(
        type=ActionPrimitiveType.GRAB,
        target_entity=target_entity,
        duration=1.0,
        cost=0.5,
        preconditions=[grab_precondition],
        effects=[grab_effect]
    )

def create_consume_action(item_id: int) -> ActionPrimitive:
    """创建消耗物品的动作"""
    def consume_precondition(world, entity_id, action):
        # 检查库存是否有该物品
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        return inventory and inventory.items.get(action.item_id, 0.0) > 0

    def consume_effect(world, entity_id, action):
        # 执行消耗
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        if inventory and needs:
            # 扣除库存
            inventory.items[action.item_id] = max(0.0, inventory.items.get(action.item_id, 0.0) - 1.0)
            # 恢复需求
            if "food" in str(action.item_id):
                needs.hunger = max(0, needs.hunger - 30)
            elif "water" in str(action.item_id):
                needs.thirst = max(0, needs.thirst - 30)

    return ActionPrimitive(
        type=ActionPrimitiveType.CONSUME,
        item_id=item_id,
        duration=1.0,
        cost=0.2,
        preconditions=[consume_precondition],
        effects=[consume_effect]
    )

def create_rest_action(duration: float = 5.0) -> ActionPrimitive:
    """创建休息动作"""
    def rest_effect(world, entity_id, action):
        # 恢复能量
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        if needs:
            needs.energy = min(100, needs.energy + 10 * action.duration)

    return ActionPrimitive(
        type=ActionPrimitiveType.REST,
        duration=duration,
        cost=0.0,
        preconditions=[],
        effects=[rest_effect]
    )

def create_socialize_action(target_entity: int) -> ActionPrimitive:
    """创建社交动作"""
    def socialize_precondition(world, entity_id, action):
        # 检查目标是否存在，距离是否足够近
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        target_pos = world.get_component(action.target_entity, SpaceComponent)
        if not pos or not target_pos:
            return False
        distance = ((pos.x - target_pos.x)**2 + (pos.y - target_pos.y)**2)**0.5
        return distance <= 3.0  # 社交距离

    def socialize_effect(world, entity_id, action):
        # 恢复社交需求
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        needs = world.get_component(entity_id, PhysiologyNeedsComponent)
        if needs:
            needs.social = min(100, needs.social + 20)

    return ActionPrimitive(
        type=ActionPrimitiveType.SOCIALIZE,
        target_entity=target_entity,
        duration=3.0,
        cost=0.5,
        preconditions=[socialize_precondition],
        effects=[socialize_effect]
    )

def create_flee_action() -> ActionPrimitive:
    """创建逃跑动作"""
    def flee_effect(world, entity_id, action):
        # 随机移动远离危险
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        if pos:
            import random
            pos.x += random.uniform(-5, 5)
            pos.y += random.uniform(-5, 5)

    return ActionPrimitive(
        type=ActionPrimitiveType.FLEE,
        duration=1.0,
        cost=2.0,
        preconditions=[],
        effects=[flee_effect]
    )

def create_equip_action(item_id: int) -> ActionPrimitive:
    """创建装备工具的动作"""
    def equip_precondition(world, entity_id, action):
        # 检查库存是否有该工具
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        return inventory and inventory.items.get(action.item_id, 0.0) > 0

    def equip_effect(world, entity_id, action):
        # 装备工具
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
        from civilization.tools.components.tool_component import ToolComponent
        from civilization.tools.components.tool_type import ToolType
        inventory = world.get_component(entity_id, InventoryComponent)
        tool_inventory = world.get_component(entity_id, ToolInventoryComponent)
        if inventory and tool_inventory:
            # 从库存中取出工具
            inventory.items[action.item_id] = max(0.0, inventory.items.get(action.item_id, 0.0) - 1.0)
            # 创建工具组件并添加到工具栏
            tool = ToolComponent(tool_type=ToolType.AXE)  # 简化：假设是斧头
            tool_inventory.add_tool(tool)
            tool_inventory.equip_tool(ToolType.AXE)

    return ActionPrimitive(
        type=ActionPrimitiveType.EQUIP,
        item_id=item_id,
        duration=0.5,
        cost=0.1,
        preconditions=[equip_precondition],
        effects=[equip_effect]
    )

def create_gather_action(target_entity: int) -> ActionPrimitive:
    """创建采集资源的动作"""
    def gather_precondition(world, entity_id, action):
        # 检查目标是否存在，距离是否足够近
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        target_pos = world.get_component(action.target_entity, SpaceComponent)
        if not pos or not target_pos:
            return False
        distance = ((pos.x - target_pos.x)**2 + (pos.y - target_pos.y)**2)**0.5
        return distance <= 2.0  # 采集距离

    def gather_effect(world, entity_id, action):
        # 采集资源
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from resource.components.resource_component import ResourceComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        resource = world.get_component(action.target_entity, ResourceComponent)
        if inventory and resource and resource.amount > 0:
            # 采集资源
            gather_amount = min(5.0, resource.amount)
            resource.amount -= gather_amount
            # 加入库存
            item_key = hash(resource.resource_type)
            inventory.items[item_key] = inventory.items.get(item_key, 0.0) + gather_amount

    return ActionPrimitive(
        type=ActionPrimitiveType.GATHER,
        target_entity=target_entity,
        duration=2.0,
        cost=1.0,
        preconditions=[gather_precondition],
        effects=[gather_effect]
    )

def create_craft_action(item_id: int) -> ActionPrimitive:
    """创建制作物品的动作"""
    def craft_precondition(world, entity_id, action):
        # 检查是否有足够的材料
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        if not inventory:
            return False
        # 简化：假设制作需要2个材料
        return sum(inventory.items.values()) >= 2

    def craft_effect(world, entity_id, action):
        # 制作物品
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        if inventory:
            # 扣除材料（简化：随机扣除2个材料）
            materials = [k for k, v in inventory.items.items() if v > 0]
            if len(materials) >= 2:
                inventory.items[materials[0]] = max(0.0, inventory.items.get(materials[0], 0.0) - 1.0)
                inventory.items[materials[1]] = max(0.0, inventory.items.get(materials[1], 0.0) - 1.0)
                # 添加成品
                inventory.items[action.item_id] = inventory.items.get(action.item_id, 0.0) + 1.0

    return ActionPrimitive(
        type=ActionPrimitiveType.CRAFT,
        item_id=item_id,
        duration=5.0,
        cost=2.0,
        preconditions=[craft_precondition],
        effects=[craft_effect]
    )

def create_build_action(structure_type: str, position: Tuple[float, float]) -> ActionPrimitive:
    """创建建造建筑的动作"""
    def build_precondition(world, entity_id, action):
        # 检查是否有足够的材料
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        if not inventory:
            return False
        # 简化：假设建造需要5个材料
        return sum(inventory.items.values()) >= 5

    def build_effect(world, entity_id, action):
        # 建造建筑
        from human.components.economic.inventory.inventory_component import InventoryComponent
        from civilization.settlement.components.settlement_component import SettlementComponent
        from space.space_component import SpaceComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        if inventory:
            # 扣除材料（简化：随机扣除5个材料）
            materials = [k for k, v in inventory.items.items() if v > 0]
            for i in range(min(5, len(materials))):
                inventory.items[materials[i]] = max(0.0, inventory.items.get(materials[i], 0.0) - 1.0)
            # 创建建筑实体
            building_entity = world.create_entity()
            world.add_component(building_entity, SpaceComponent(x=action.target_position[0], y=action.target_position[1]))

    return ActionPrimitive(
        type=ActionPrimitiveType.BUILD,
        target_position=position,
        parameters={"structure_type": structure_type},
        duration=10.0,
        cost=5.0,
        preconditions=[build_precondition],
        effects=[build_effect]
    )

def create_teach_action(target_entity: int, skill: str) -> ActionPrimitive:
    """创建教学动作"""
    def teach_precondition(world, entity_id, action):
        # 检查目标是否存在，距离是否足够近
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        target_pos = world.get_component(action.target_entity, SpaceComponent)
        if not pos or not target_pos:
            return False
        distance = ((pos.x - target_pos.x)**2 + (pos.y - target_pos.y)**2)**0.5
        return distance <= 3.0  # 教学距离

    def teach_effect(world, entity_id, action):
        # 教学效果：目标获得技能
        from human.components.abilities.skill_component import SkillComponent
        skill_comp = world.get_component(action.target_entity, SkillComponent)
        if skill_comp:
            # 简化：随机提升技能等级
            import random
            if action.parameters["skill"] in skill_comp.skills:
                skill_comp.skills[action.parameters["skill"]] += random.uniform(0.1, 0.5)
            else:
                skill_comp.skills[action.parameters["skill"]] = random.uniform(0.1, 0.3)

    return ActionPrimitive(
        type=ActionPrimitiveType.TEACH,
        target_entity=target_entity,
        parameters={"skill": skill},
        duration=5.0,
        cost=1.0,
        preconditions=[teach_precondition],
        effects=[teach_effect]
    )

def create_cooperate_action(target_entity: int, task: str) -> ActionPrimitive:
    """创建协作动作"""
    def cooperate_precondition(world, entity_id, action):
        # 检查目标是否存在，距离是否足够近
        from space.space_component import SpaceComponent
        pos = world.get_component(entity_id, SpaceComponent)
        target_pos = world.get_component(action.target_entity, SpaceComponent)
        if not pos or not target_pos:
            return False
        distance = ((pos.x - target_pos.x)**2 + (pos.y - target_pos.y)**2)**0.5
        return distance <= 5.0  # 协作距离

    def cooperate_effect(world, entity_id, action):
        # 协作效果：共同完成任务，提高效率
        from human.components.economic.inventory.inventory_component import InventoryComponent
        inventory = world.get_component(entity_id, InventoryComponent)
        target_inventory = world.get_component(action.target_entity, InventoryComponent)
        if inventory and target_inventory:
            # 简化：双方都获得资源
            item_key = hash(action.parameters["task"])
            inventory.items[item_key] = inventory.items.get(item_key, 0.0) + 2.0
            target_inventory.items[item_key] = target_inventory.items.get(item_key, 0.0) + 2.0

    return ActionPrimitive(
        type=ActionPrimitiveType.COOPERATE,
        target_entity=target_entity,
        parameters={"task": task},
        duration=8.0,
        cost=2.0,
        preconditions=[cooperate_precondition],
        effects=[cooperate_effect]
    )

# 动作元件注册表，支持零代码扩展新动作
_ACTION_PRIMITIVES_REGISTRY: Dict[ActionPrimitiveType, Callable] = {
    ActionPrimitiveType.MOVE_TO: create_move_to_action,
    ActionPrimitiveType.GRAB: create_grab_action,
    ActionPrimitiveType.CONSUME: create_consume_action,
    ActionPrimitiveType.REST: create_rest_action,
    ActionPrimitiveType.SOCIALIZE: create_socialize_action,
    ActionPrimitiveType.FLEE: create_flee_action,
    ActionPrimitiveType.EQUIP: create_equip_action,
    ActionPrimitiveType.GATHER: create_gather_action,
    ActionPrimitiveType.CRAFT: create_craft_action,
    ActionPrimitiveType.BUILD: create_build_action,
    ActionPrimitiveType.TEACH: create_teach_action,
    ActionPrimitiveType.COOPERATE: create_cooperate_action,
}

def register_action_primitive(action_type: ActionPrimitiveType, factory: Callable):
    """注册新的动作元件"""
    _ACTION_PRIMITIVES_REGISTRY[action_type] = factory

def get_action_primitive(action_type: ActionPrimitiveType, **kwargs) -> Optional[ActionPrimitive]:
    """获取动作元件实例"""
    factory = _ACTION_PRIMITIVES_REGISTRY.get(action_type)
    if factory:
        return factory(**kwargs)
    return None
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:trade_system.py
@说明:交易系统 - 人类之间资源交换的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

import logging

from core.system import System
from core.world import World
from typing import List, Tuple, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.social.social_component import SocialComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from space.space_component import SpaceComponent


class TradeType(Enum):
    """交易类型枚举"""
    DIRECT_EXCHANGE = "direct_exchange"  # 直接交换
    BARTER = "barter"                   # 物物交换
    MARKET_TRADE = "market_trade"       # 市场交易


class TradeSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    交易系统

    功能：
    - 人类之间进行资源交换
    - 支持物物交换和市场交易
    - 交易效率受社交技能影响
    - 记录交易历史和关系变化
    """

    def update(self, world: World, dt: float) -> None:
        """更新交易行为"""
        # 先查询最核心的 2 个组件，其余在循环内补查
        for entity, (action, task) in world.get_components(
            ActionComponent, TaskComponent
        ):
            if action.current_action != ActionType.TRADE:
                continue

            if action.status != ActionStatus.IN_PROGRESS:
                continue

            # 补查其他组件
            inventory = world.get_component(entity, InventoryComponent)
            economy = world.get_component(entity, EconomyComponent)
            social = world.get_component(entity, SocialComponent)
            skill = world.get_component(entity, SkillComponent)
            space = world.get_component(entity, SpaceComponent)

            # 查找交易伙伴
            trade_partner = getattr(action, 'trade_partner', None)
            if not trade_partner:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            partner_inv = world.get_component(trade_partner, InventoryComponent)
            partner_eco = world.get_component(trade_partner, EconomyComponent)
            partner_soc = world.get_component(trade_partner, SocialComponent)
            partner_space = world.get_component(trade_partner, SpaceComponent)

            if not (partner_inv and partner_eco and partner_soc and partner_space):
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 执行交易
            self._perform_trade(entity, trade_partner, action, inventory, economy, social, skill,
                              (partner_inv, partner_eco, partner_soc, partner_space), world, dt)

            action.status = ActionStatus.COMPLETED
            task.status = TaskStatus.COMPLETED

    def _perform_trade(self, entity, partner_entity, action: ActionComponent,
                      inventory: InventoryComponent, economy: EconomyComponent,
                      social: SocialComponent, skill: SkillComponent,
                      partner_data: Tuple, world: World, dt: float):
        """执行交易"""
        partner_inventory, partner_economy, partner_social, partner_space = partner_data

        trade_type = getattr(action, 'trade_type', TradeType.BARTER)
        offered_resources = getattr(action, 'offered_resources', {})
        requested_resources = getattr(action, 'requested_resources', {})

        # 计算交易价值
        offer_value = self._calculate_trade_value(offered_resources, inventory)
        request_value = self._calculate_trade_value(requested_resources, partner_inventory)

        if offer_value <= 0 or request_value <= 0:
            return  # 无效交易

        # 计算交易比率（考虑技能和关系）
        trade_ratio = self._calculate_trade_ratio(
            entity, partner_entity, social, partner_social, skill, world
        )

        # 调整交易价值
        adjusted_offer_value = offer_value * trade_ratio
        adjusted_request_value = request_value / trade_ratio

        # 判断交易是否公平
        fairness_ratio = adjusted_offer_value / adjusted_request_value

        if 0.8 <= fairness_ratio <= 1.2:  # 公平交易范围
            self._execute_trade(entity, partner_entity, offered_resources, requested_resources,
                              inventory, partner_inventory, economy, partner_economy,
                              social, partner_social, world)
        else:
            # 不公平交易可能损害关系
            relationship_damage = abs(1.0 - fairness_ratio) * 5.0
            self._update_relationship(entity, partner_entity, -relationship_damage, world)

    def _calculate_trade_value(self, resources: Dict[str, float], inventory: InventoryComponent) -> float:
        """计算资源价值"""
        total_value = 0.0

        # 基础价值表
        value_table = {
            'food': 1.0,
            'water': 1.5,
            'wood': 0.8,
            'stone': 0.6,
            'metal': 3.0
        }

        for resource_type, amount in resources.items():
            if resource_type in value_table:
                total_value += value_table[resource_type] * amount

        return total_value

    def _calculate_trade_ratio(self, entity, partner_entity, social: SocialComponent,
                             partner_social: SocialComponent, skill: SkillComponent,
                             world: World) -> float:
        """计算交易比率"""
        base_ratio = 1.0

        # 社交技能加成
        trade_skill = skill.skills.get('trading', 1.0)
        base_ratio *= (0.8 + trade_skill * 0.2)

        # 关系加成
        relationship = self._get_relationship(entity, partner_entity, world)
        if relationship > 0:
            base_ratio *= (0.9 + relationship * 0.1)
        elif relationship < 0:
            base_ratio *= (1.1 - relationship * 0.1)

        # 社会地位差异
        status_diff = social.social_status - partner_social.social_status
        if status_diff > 0:
            base_ratio *= 0.95  # 地位高的人交易更有利
        elif status_diff < 0:
            base_ratio *= 1.05

        return base_ratio

    def _execute_trade(self, entity, partner_entity, offered: Dict[str, float],
                      requested: Dict[str, float], inventory: InventoryComponent,
                      partner_inventory: InventoryComponent, economy: EconomyComponent,
                      partner_economy: EconomyComponent, social: SocialComponent,
                      partner_social: SocialComponent, world: World):
        """执行交易"""
        # 转移资源
        for resource_type, amount in offered.items():
            self._transfer_resource(inventory, partner_inventory, resource_type, amount)

        for resource_type, amount in requested.items():
            self._transfer_resource(partner_inventory, inventory, resource_type, amount)

        # 更新经济状态
        trade_value = self._calculate_trade_value(offered, inventory)
        economy.wealth += trade_value * 0.1  # 交易经验转化为财富
        partner_economy.wealth += trade_value * 0.1

        # 改善关系
        self._update_relationship(entity, partner_entity, 2.0, world)

        # 记录交易历史
        self._record_trade_history(entity, partner_entity, offered, requested, world)

        logger.info(f"[TradeSystem] Trade completed between {entity.id} and {partner_entity.id}")

    def _transfer_resource(self, from_inventory: InventoryComponent,
                          to_inventory: InventoryComponent, resource_type: str, amount: float):
        """转移资源"""
        if resource_type == 'food':
            from_inventory.food = max(0, from_inventory.food - amount)
            to_inventory.food += amount
        elif resource_type == 'water':
            from_inventory.water = max(0, from_inventory.water - amount)
            to_inventory.water += amount
        elif resource_type == 'wood':
            from_inventory.wood = max(0, from_inventory.wood - amount)
            to_inventory.wood += amount
        elif resource_type == 'stone':
            from_inventory.stone = max(0, from_inventory.stone - amount)
            to_inventory.stone += amount
        elif resource_type == 'metal':
            from_inventory.metal = max(0, from_inventory.metal - amount)
            to_inventory.metal += amount

    def _get_relationship(self, entity, partner_entity, world: World) -> float:
        """获取两个实体之间的关系值"""
        social = world.get_component(entity, SocialComponent)
        if social and partner_entity in social.relationships:
            return social.relationships[partner_entity]
        return 0.0

    def _update_relationship(self, entity, partner_entity, change: float, world: World):
        """更新关系"""
        social = world.get_component(entity, SocialComponent)
        if social:
            if partner_entity not in social.relationships:
                social.relationships[partner_entity] = 0.0
            social.relationships[partner_entity] += change
            social.relationships[partner_entity] = max(-10.0, min(10.0, social.relationships[partner_entity]))

    def _record_trade_history(self, entity, partner_entity, offered: Dict[str, float],
                            requested: Dict[str, float], world: World):
        """记录交易历史"""
        memory = world.get_component(entity, MemoryComponent)
        if memory:
            memory.add_experience({
                'type': 'trade',
                'partner': partner_entity,
                'offered': offered,
                'requested': requested,
                'timestamp': world.get_component(entity, TimeComponent).current_time if world.get_component(entity, TimeComponent) else 0
            })
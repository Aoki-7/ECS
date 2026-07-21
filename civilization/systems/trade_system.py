#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
TradeSystem - 交易系统（最小可用版）

v3.9 修复：
- 使用 ActionStatus.RUNNING / SUCCESS 替换不存在的 IN_PROGRESS / COMPLETED
- 使用 action.target_entity 作为交易伙伴（兼容 ActionPlanner.plan_trade）
- 不再依赖动态属性（trade_partner / offered_resources / requested_resources）
- 不再访问不存在的 InventoryComponent 资源字段（food/water/wood 等）
- 简化为象征性交：增加双方财富、加深关系、记录交易历史

TODO：未来可接入真实物品转移与议价逻辑。
"""

import logging
import math
from typing import Optional

from core.system import System
from core.world import World

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.social.social_component import SocialComponent
from human.components.cognitive.task_component import TaskComponent, TaskStatus
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class TradeSystem(System):
    """交易系统：在附近人类之间执行简单物物交换。"""

    tick_interval = 20  # 每 20 帧执行一次

    # 交易距离阈值（单位：世界坐标）
    TRADE_DISTANCE = 2.0
    # 每次交易增加的财富值
    TRADE_WEALTH_DELTA = 1.0
    # 每次交易增加的关系强度
    RELATIONSHIP_BONUS = 1.0
    RELATIONSHIP_CAP = 10.0

    def update(self, world: World, dt: float) -> None:
        """处理所有处于 TRADE 行为且状态为 RUNNING 的实体。"""
        for entity, (action, task) in world.get_components(ActionComponent, TaskComponent):
            if action.current_action != ActionType.TRADE:
                continue
            if action.status != ActionStatus.RUNNING:
                continue

            partner = action.target_entity
            if partner is None or partner not in world.entities:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 补查必要组件
            space = world.get_component(entity, SpaceComponent)
            partner_space = world.get_component(partner, SpaceComponent)
            economy = world.get_component(entity, EconomyComponent)
            partner_economy = world.get_component(partner, EconomyComponent)
            social = world.get_component(entity, SocialComponent)
            partner_social = world.get_component(partner, SocialComponent)
            inventory = world.get_component(entity, InventoryComponent)
            partner_inventory = world.get_component(partner, InventoryComponent)

            if not all((space, partner_space, economy, partner_economy,
                        social, partner_social, inventory, partner_inventory)):
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            dist = math.hypot(space.x - partner_space.x, space.y - partner_space.y)
            if dist > self.TRADE_DISTANCE:
                action.status = ActionStatus.FAILED
                task.status = TaskStatus.FAILED
                continue

            # 执行交易
            self._execute_trade(entity, partner,
                                economy, partner_economy,
                                social, partner_social,
                                inventory, partner_inventory)

            action.status = ActionStatus.SUCCESS
            task.status = TaskStatus.DONE

    def _execute_trade(self, entity, partner,
                       economy: EconomyComponent, partner_economy: EconomyComponent,
                       social: SocialComponent, partner_social: SocialComponent,
                       inventory: InventoryComponent, partner_inventory: InventoryComponent) -> None:
        """执行一次象征性交易：财富、关系、历史记录。"""
        economy.wealth += self.TRADE_WEALTH_DELTA
        partner_economy.wealth += self.TRADE_WEALTH_DELTA

        self._strengthen_relationship(social, partner)
        self._strengthen_relationship(partner_social, entity.id)

        self._record_trade(inventory, partner, self.TRADE_WEALTH_DELTA)
        self._record_trade(partner_inventory, entity.id, self.TRADE_WEALTH_DELTA)

        logger.info(
            f"[TradeSystem] Trade completed: E{entity.id} <-> E{partner}, "
            f"wealth +{self.TRADE_WEALTH_DELTA}"
        )

    def _strengthen_relationship(self, social: SocialComponent, partner_id: int) -> None:
        """加深与指定实体的社交关系。"""
        if partner_id not in social.relations:
            social.relations[partner_id] = "trading_partner"
        current = social.relation_strength.get(partner_id, 0.0)
        social.relation_strength[partner_id] = min(
            self.RELATIONSHIP_CAP, current + self.RELATIONSHIP_BONUS
        )

    def _record_trade(self, inventory: InventoryComponent, partner_id: int, value: float) -> None:
        """在库存的交易历史中记录一次交易。"""
        inventory.trade_history.append({
            "partner": partner_id,
            "value": value,
            "type": "barter",
        })

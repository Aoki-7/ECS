#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
EconomySystem - 经济系统（ECS 化）

职责：
- 管理 WalletComponent（实体货币余额）
- 管理 MarketPricesComponent（世界市场价格）
- 每 tick 执行物价动态调整

原 MoneySystem 已拆分为：
- WalletComponent（实体级数据）
- MarketPricesComponent（world_entity 级数据）
- EconomySystem（业务逻辑）
"""

import random
import logging
from typing import Dict, Optional

from core.system import System
from core.world import World

from human.components.economic.wallet_component import WalletComponent
from human.components.economic.economy_component import EconomyComponent

logger = logging.getLogger(__name__)


class EconomySystem(System):
    """
    经济系统

    处理货币交易、市场价格动态调整。
    """

    priority = 35  # 在人类核心系统之后

    # 默认市场价格
    DEFAULT_PRICES = {
        "bread": 0.5,
        "meat": 1.2,
        "apple": 0.2,
        "potato": 0.15,
        "water": 0.1,
        "wood": 0.3,
        "stone": 0.4,
        "metal": 1.5,
    }

    # 汇率
    EXCHANGE_RATES = {"gold": 1.0, "silver": 10.0, "copper": 100.0}

    def __init__(self):
        super().__init__()
        self._price_volatility = 0.02  # 每 tick 价格波动幅度

    def on_add(self, world: World):
        """自动挂载 MarketPricesComponent 到 world_entity"""
        from core.event_log_component import EventLogComponent
        we = world.get_world_entity()
        # 使用 EconomyComponent 作为市场价格载体（已存在）
        if world.get_world_component(EconomyComponent) is None:
            world.get_world_entity().add_component(EconomyComponent())

    def update(self, world: World, dt: float = 1.0):
        """
        每 tick 执行：
        1. 动态调整市场价格（随机波动）
        2. 可扩展：供需模型、通胀等
        """
        super().update(world, dt)
        self._update_market_prices(world, dt)

    # ── 市场价格管理 ──

    def _update_market_prices(self, world: World, dt: float):
        """市场价格随机波动（模拟市场变化）"""
        econ = world.get_world_component(EconomyComponent)
        if econ is None:
            return

        # 若 prices 为空，初始化默认值
        if not getattr(econ, 'prices', None):
            econ.prices = dict(self.DEFAULT_PRICES)

        for item in list(econ.prices.keys()):
            # 随机波动 ±2%
            change = 1.0 + random.uniform(-self._price_volatility, self._price_volatility)
            econ.prices[item] = max(0.01, econ.prices[item] * change)

    def get_price(self, world: World, item: str) -> Optional[float]:
        """获取商品当前价格"""
        econ = world.get_world_component(EconomyComponent)
        if econ is None or not getattr(econ, 'prices', None):
            return self.DEFAULT_PRICES.get(item)
        return econ.prices.get(item)

    # ── 钱包操作 ──

    @staticmethod
    def get_wallet(entity) -> WalletComponent:
        """获取或创建实体的钱包"""
        wallet = entity.get_component(WalletComponent)
        if wallet is None:
            wallet = WalletComponent()
            entity.add_component(wallet)
        return wallet

    @staticmethod
    def add_currency(entity, currency: str = "gold", amount: float = 10.0) -> None:
        """为实体添加货币"""
        wallet = EconomySystem.get_wallet(entity)
        if currency == "gold":
            wallet.gold += amount
        elif currency == "silver":
            wallet.silver += amount
        elif currency == "copper":
            wallet.copper += amount

    @staticmethod
    def remove_currency(entity, currency: str, amount: float) -> bool:
        """从实体扣除货币，余额不足返回 False"""
        wallet = EconomySystem.get_wallet(entity)
        if currency == "gold" and wallet.gold >= amount:
            wallet.gold -= amount
            return True
        elif currency == "silver" and wallet.silver >= amount:
            wallet.silver -= amount
            return True
        elif currency == "copper" and wallet.copper >= amount:
            wallet.copper -= amount
            return True
        return False

    def buy(self, world: World, buyer, item: str, quantity: float) -> tuple:
        """
        购买商品

        Returns:
            (success: bool, cost: float)
        """
        price = self.get_price(world, item)
        if price is None:
            return None, 0.0

        total_cost = price * quantity
        if not self.remove_currency(buyer, "gold", total_cost):
            return False, 0.0

        wallet = self.get_wallet(buyer)
        wallet.trade_history.append({
            "type": "buy",
            "item": item,
            "quantity": quantity,
            "price": total_cost,
        })
        return True, total_cost

    def sell(self, world: World, seller, item: str, quantity: float) -> tuple:
        """
        出售商品

        Returns:
            (success: bool, revenue: float)
        """
        price = self.get_price(world, item)
        if price is None:
            return None, 0.0

        total_revenue = price * quantity
        self.add_currency(seller, "gold", total_revenue)

        wallet = self.get_wallet(seller)
        wallet.trade_history.append({
            "type": "sell",
            "item": item,
            "quantity": quantity,
            "price": total_revenue,
        })
        return True, total_revenue

    @staticmethod
    def get_balance_dict(entity) -> Dict[str, float]:
        """获取实体余额字典"""
        wallet = entity.get_component(WalletComponent)
        if wallet is None:
            return {"gold": 0.0, "silver": 0.0, "copper": 0.0}
        return wallet.get_balance_dict()

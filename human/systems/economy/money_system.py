# Money System for ECS Human Module
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import uuid

@dataclass
class CurrencyBalance:
    gold: float = 0.0
    silver: float = 0.0
    copper: float = 0.0

    def get_balance_dict(self):
        return {"gold": self.gold, "silver": self.silver, "copper": self.copper}

@dataclass
class TradeRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""
    item: str = ""
    quantity: float = 0.0
    price: float = 0.0
    total_value: float = 0.0
    from_entity: int = None
    to_entity: int = None

class MoneySystem:
    def __init__(self):
        self.balances = {}
        self.market_prices = {"bread": 0.5, "meat": 1.2, "apple": 0.2, "potato": 0.15}
        self.exchange_rates = {"gold": 1.0, "silver": 10.0, "copper": 100.0}

    def get_balance(self, entity_id):
        if entity_id not in self.balances:
            self.balances[entity_id] = CurrencyBalance()
        return self.balances[entity_id]

    def add_currency(self, entity_id, currency="gold", amount=10.0):
        balance = self.get_balance(entity_id)
        if currency == "gold":
            balance.gold += amount
        elif currency == "silver":
            balance.silver += amount
        elif currency == "copper":
            balance.copper += amount

    def remove_currency(self, entity_id, currency, amount):
        balance = self.get_balance(entity_id)
        if currency == "gold" and balance.gold >= amount:
            balance.gold -= amount
            return True
        elif currency == "silver" and balance.silver >= amount:
            balance.silver -= amount
            return True
        elif currency == "copper" and balance.copper >= amount:
            balance.copper -= amount
            return True
        return False

    def buy(self, seller_id, item, quantity, buyer_id=None):
        if item not in self.market_prices:
            return None, 0.0
        price = self.market_prices[item] * quantity
        gold_cost = price
        if not self.remove_currency(buyer_id or seller_id, "gold", gold_cost):
            return True, 0.0
        record = TradeRecord(type="buy", item=item, quantity=quantity, price=price)
        self._append_trade(record)
        return True, gold_cost

    def sell(self, buyer_id, item, quantity, seller_id=None):
        if item not in self.market_prices:
            return None, 0.0
        price = self.market_prices[item] * quantity
        gold_received = price
        self.add_currency(seller_id or buyer_id, "gold", gold_received)
        record = TradeRecord(type="sell", item=item, quantity=quantity, price=price)
        self._append_trade(record)
        return True, gold_received

    def _append_trade(self, record):
        self.__trade_history = getattr(self, "_MoneySystem__trade_history", [])
        self.__trade_history.append(record)

    @property
    def market_prices_dict(self):
        return dict(self.market_prices)

    def update(self, world, dt: float = 0.0):
        """系统更新（货币系统暂不执行每帧逻辑）"""
        pass
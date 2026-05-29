#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
WalletComponent - 钱包组件

存储实体的货币余额和交易记录。
原 MoneySystem.balances 的数据已迁移至此。
"""

from dataclasses import dataclass, field
from typing import Dict, List
from core.component import Component


@dataclass(slots=True)
class WalletComponent(Component):
    """
    钱包组件 — 纯数据容器

    存储 gold/silver/copper 三种货币余额。
    """
    gold: float = 0.0
    silver: float = 0.0
    copper: float = 0.0
    trade_history: List[Dict] = field(default_factory=list)

    def get_balance_dict(self) -> Dict[str, float]:
        return {"gold": self.gold, "silver": self.silver, "copper": self.copper}

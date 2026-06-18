#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:wallet_component.py
@说明:钱包组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component

@dataclass(slots=True)
class WalletComponent(Component):
    """
    钱包组件 - 纯数据版
    存储货币和资产。
    """
    # 货币余额 {currency_type: amount}
    balance: Dict[str, float] = field(default_factory=dict)
    
    # 交易记录
    transactions: List[Dict] = field(default_factory=list)
    
    # 信用评分
    credit_score: float = 50.0
    
    # 债务
    debts: Dict[str, float] = field(default_factory=dict)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:economy_component.py
@说明:经济组件 - 纯数据版

经济属性：
- currency: 货币数量
- assets: 资产列表（土地/建筑/物品）
- income: 收入来源
- expenses: 支出记录
- debt: 债务
- trade_history: 交易历史
'''

from dataclasses import dataclass, field
from typing import Dict, List, Any

from core.component import Component


@dataclass(slots=True)
class CivilizationEconomyComponent(Component):
    """
    经济组件 - 纯数据版

    Attributes:
        currency: 货币数量
        assets: 资产字典 {asset_id: asset_value}
        income_sources: 收入来源列表
        expense_records: 支出记录列表
        debt: 债务金额
        credit_score: 信用评分 [0.0, 1.0]
        trade_history: 交易历史列表
        market_access: 市场访问权限
    """
    currency: float = 0.0
    assets: Dict[str, float] = field(default_factory=dict)
    income_sources: List[str] = field(default_factory=list)
    expense_records: List[Dict[str, Any]] = field(default_factory=list)
    debt: float = 0.0
    credit_score: float = 0.5
    trade_history: List[Dict[str, Any]] = field(default_factory=list)
    market_access: bool = True

    def __post_init__(self):
        # 限制数值范围
        self.currency = max(0.0, self.currency)
        self.debt = max(0.0, self.debt)
        self.credit_score = max(0.0, min(1.0, self.credit_score))
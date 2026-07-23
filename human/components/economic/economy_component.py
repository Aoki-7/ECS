

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:economy_component.py
@说明:
@时间:2026/03/14 10:54:31
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component

from typing import Dict


@dataclass(slots=True)
class EconomyComponent(Component):
    """
    经济组件（世界级）— 存储全局市场价格

    挂载到 WorldEntity 上，管理模拟世界的经济参数。
    实体级货币余额由 WalletComponent 管理。
    """
    wealth: float = 0.0
    income: float = 0.0
    expenses: float = 0.0
    prices: Dict[str, float] = None  # 市场价格字典
    
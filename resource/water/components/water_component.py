#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:water_component.py
@说明:水组件
@时间:2026/04/13
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict

from core.component import Component


@dataclass
class WaterComponent(Component):
    """
    水组件（可被饮用的资源）

    ===== 核心设计 =====
    - 支持多次饮用
    - 主要影响水分指标
    - 支持污染/纯净度
    - 支持温度影响
    """

    # ===== 基础消耗 =====
    amount: float = 1.0          # 剩余份数（被喝完后销毁）
    sip_size: float = 0.25       # 每次喝掉多少

    # ===== 水分属性 =====
    hydration: float = 50.0      # 水分值（核心）
    temperature: float = 20.0    # 温度（摄氏度）
    purity: float = 1.0          # 纯净度 [0,1]，影响健康

    # ===== 状态属性 =====
    freshness: float = 1.0       # 新鲜度 [0,1]
    evaporation_rate: float = 0.005  # 蒸发速度（每tick）

    is_evaporable: bool = True   # 是否会蒸发

    # ===== 风险属性 =====
    contamination: float = 0.0   # 污染程度（环境影响）
    bacteria: float = 0.0        # 细菌含量（>0 会扣健康）

    # ===== 扩展效果（通用机制）=====
    effects: Dict[str, float] = field(default_factory=dict)
    # 例如：
    # {
    #   "health": -10,  # 污染水会扣健康
    #   "energy": +5    # 凉水可能提神
    # }

    # ===== 行为方法 =====
    def drink(self) -> float:
        """
        被喝一口，返回实际消耗量

        Returns:
            float: 实际喝掉的水量
        """
        actual_amount = min(self.amount, self.sip_size)
        self.amount -= actual_amount
        return actual_amount

    def is_safe_to_drink(self) -> bool:
        """
        检查是否安全饮用

        Returns:
            bool: True如果安全饮用
        """
        return self.purity > 0.5 and self.bacteria < 0.1

    def get_temperature_effect(self) -> float:
        """
        获取温度对饮用效果的影响

        Returns:
            float: 温度修正因子（1.0为最适宜）
        """
        # 最适宜温度20°C，过热或过冷都会降低效果
        optimal_temp = 20.0
        temp_diff = abs(self.temperature - optimal_temp)
        return max(0.5, 1.0 - temp_diff * 0.02)  # 每度差降低2%
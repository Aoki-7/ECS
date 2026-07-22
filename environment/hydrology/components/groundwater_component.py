#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
地下水组件 v4.16.0
存储每个网格单元的地下水状态，参与水循环
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class GroundwaterComponent(Component):
    """
    地下水组件
    每个环境网格单元挂载，存储地下水储量与流动属性
    """
    
    # === 兼容旧API属性 ===
    aquifer_type: str = "unconfined"  # 含水层类型，兼容旧测试
    water_table: float = -5.0  # 地下水位（m，海拔基准，兼容旧API）
    
    # 地下水储量（mm）
    storage: float = 200.0
    # 最大储水量（mm），由土壤类型决定
    max_storage: float = 500.0
    # 地下水位深度（m），储量越大水位越浅
    water_table_depth: float = 5.0
    
    # 禁止dataclass自动生成__init__时覆盖我们的兼容逻辑
    def __init__(self, **kwargs):
        # 先初始化默认值
        self.aquifer_type = kwargs.get('aquifer_type', 'unconfined')
        self.water_table = kwargs.get('water_table', -5.0)
        self.storage = kwargs.get('storage', 200.0)
        self.max_storage = kwargs.get('max_storage', 500.0)
        self.hydraulic_conductivity = kwargs.get('hydraulic_conductivity', 0.1)
        self.porosity = kwargs.get('porosity', 0.4)
        
        # 处理水位关系
        if 'water_table' in kwargs:
            self.water_table_depth = max(0.0, -self.water_table)
        else:
            self.water_table_depth = kwargs.get('water_table_depth', 5.0)
            self.water_table = -self.water_table_depth
    # 水力传导系数（m/h），决定横向流动速度，沙土>壤土>黏土
    hydraulic_conductivity: float = 0.1
    # 孔隙度（0-1），土壤孔隙占比，决定储水能力
    porosity: float = 0.4

    def __post_init__(self):
        # 兼容旧API：用户传入water_table时优先使用，否则从depth计算
        if self.water_table == -5.0:
            # 默认值，使用depth计算
            self.water_table = -self.water_table_depth
        else:
            # 用户自定义water_table，更新depth
            self.water_table_depth = max(0.0, -self.water_table)
    
    def get_available_water(self) -> float:
        """获取可开采/可被植物根系吸收的地下水量"""
        return max(0.0, self.storage - self.max_storage * 0.1)  # 10%为不可用的结合水
    
    def add_water(self, amount: float) -> float:
        """
        补给地下水
        :param amount: 补给量（mm）
        :return: 超出最大储量的溢出量（mm）
        """
        self.storage += amount
        overflow = max(0.0, self.storage - self.max_storage)
        self.storage = min(self.storage, self.max_storage)
        # 更新地下水位深度
        self._update_water_table()
        return overflow
    
    def remove_water(self, amount: float) -> float:
        """
        抽取地下水
        :param amount: 抽取量（mm）
        :return: 实际抽取量
        """
        actual = min(amount, self.get_available_water())
        self.storage -= actual
        self._update_water_table()
        return actual
    
    def _update_water_table(self) -> None:
        """根据储量更新地下水位深度"""
        fill_ratio = self.storage / self.max_storage
        # 储量为0时水位深度3m，满时0.5m
        self.water_table_depth = 3.0 - fill_ratio * 2.5
        # 同步旧API字段
        self.water_table = -self.water_table_depth

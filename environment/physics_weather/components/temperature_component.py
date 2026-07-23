#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
温度组件 v4.16.0
存储网格单元的分层温度数据，参与温度传导
"""

from dataclasses import dataclass, field
from core.component import Component
from typing import List


@dataclass(slots=True)
class TemperatureComponent(Component):
    """
    温度组件
    每个环境网格单元挂载，存储分层温度与热属性
    """
    
    # 分层温度（°C）：索引0是地表，1是10cm深，2是50cm深，3是1m深，4是2m深
    temperatures: List[float] = field(default_factory=lambda: [20.0, 18.0, 16.0, 15.0, 14.0])
    
    # 热属性
    thermal_conductivity: float = 1.5  # 热传导系数 W/(m·K)，沙土>壤土>黏土>泥炭
    heat_capacity: float = 2.0e6  # 体积热容 J/(m³·K)，湿润土壤>干燥土壤
    albedo: float = 0.2  # 反照率 0-1，植被覆盖低反照率高，雪地反照率最高
    
    # 地表状态
    surface_temperature: float = field(init=False)  # 地表温度（索引0的别名）
    surface_heat_flux: float = 0.0  # 地表热通量 W/m²，正为向下，负为向上
    
    def __post_init__(self):
        self.surface_temperature = self.temperatures[0]
    
    def update_temperatures(self, new_temps: List[float]) -> None:
        """更新分层温度，自动同步地表温度"""
        for i in range(min(len(self.temperatures), len(new_temps))):
            self.temperatures[i] = max(-50.0, min(60.0, new_temps[i]))
        self.surface_temperature = self.temperatures[0]
    
    def get_soil_temperature(self, depth: float) -> float:
        """获取指定深度的土壤温度（线性插值）"""
        if depth <= 0:
            return self.surface_temperature
        if depth >= 2.0:
            return self.temperatures[-1]
        
        # 找到相邻层
        depths = [0, 0.1, 0.5, 1.0, 2.0]
        for i in range(len(depths)-1):
            if depths[i] <= depth < depths[i+1]:
                # 线性插值
                ratio = (depth - depths[i]) / (depths[i+1] - depths[i])
                return self.temperatures[i] * (1 - ratio) + self.temperatures[i+1] * ratio
        
        return self.temperatures[-1]
    
    def get_average_soil_temperature(self, max_depth: float = 1.0) -> float:
        """获取指定深度内的平均土壤温度"""
        total = 0.0
        count = 0
        depths = [0, 0.1, 0.5, 1.0, 2.0]
        for i, d in enumerate(depths):
            if d > max_depth:
                break
            total += self.temperatures[i]
            count += 1
        return total / count if count > 0 else self.surface_temperature
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
微生物组件 v4.16.0
定义微生物实体的属性，包括细菌、真菌、病毒等
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from core.component import Component
from typing import Dict, List


class MicrobeType(Enum):
    """微生物类型"""
    BACTERIA = auto()       # 细菌
    FUNGI = auto()          # 真菌
    VIRUS = auto()          # 病毒
    ARCHAEA = auto()        # 古菌
    PROTOZOA = auto()       # 原生生物


class MicrobeFunction(Enum):
    """微生物功能类型"""
    DECOMPOSER = auto()     # 分解者：分解有机质
    NITROGEN_FIXER = auto() # 固氮菌：固定大气氮
    PATHOGEN = auto()       # 致病菌：导致动植物疾病
    SYMBIONT = auto()       # 共生菌：与宿主互利共生
    MYCORRHIZA = auto()     # 菌根真菌：帮助植物吸收养分


@dataclass(slots=True)
class MicrobeComponent(Component):
    """
    微生物组件
    微生物实体挂载此组件
    """
    
    # 基础属性
    microbe_type: MicrobeType = MicrobeType.BACTERIA
    functions: List[MicrobeFunction] = field(default_factory=list)
    species: str = "unknown"  # 物种名称
    
    # 生理属性
    growth_rate: float = 0.1  # 生长速率每小时
    optimal_temperature: float = 25.0  # 最适生长温度
    optimal_moisture: float = 0.6  # 最适生长湿度
    optimal_ph: float = 6.5  # 最适pH
    stress_tolerance: float = 0.3  # 环境胁迫耐受度 0-1
    
    # 种群属性
    population_size: float = 1e6  # 种群数量（CFU/g土壤）
    max_population: float = 1e9  # 最大种群密度
    mortality_rate: float = 0.05  # 死亡率每小时
    
    # 功能属性
    decomposition_efficiency: float = 0.2  # 分解效率，分解者功能有效
    nitrogen_fixation_rate: float = 0.01  # 固氮速率 mg N/g 微生物每小时，固氮菌有效
    pathogenicity: float = 0.0  # 致病性 0-1，致病菌有效
    symbiosis_efficiency: float = 0.3  # 共生效率，共生菌/菌根有效
    
    def is_functional(self, function: MicrobeFunction) -> bool:
        """检查微生物是否具有指定功能"""
        return function in self.functions
    
    def get_growth_factor(self, temperature: float, moisture: float, ph: float) -> float:
        """计算环境条件下的生长因子 0-1"""
        # 温度因子
        if abs(temperature - self.optimal_temperature) > 20:
            temp_factor = 0.01
        else:
            temp_factor = 1.0 - abs(temperature - self.optimal_temperature) / 20.0
        
        # 湿度因子
        if abs(moisture - self.optimal_moisture) > 0.6:
            moisture_factor = 0.01
        else:
            moisture_factor = 1.0 - abs(moisture - self.optimal_moisture) / 0.6
        
        # pH因子
        if abs(ph - self.optimal_ph) > 3:
            ph_factor = 0.01
        else:
            ph_factor = 1.0 - abs(ph - self.optimal_ph) / 3.0
        
        # 总生长因子
        growth_factor = temp_factor * moisture_factor * ph_factor
        return max(0.01, growth_factor)
    
    def update_population(self, growth_factor: float, dt: float, resource_available: float = 1.0) -> None:
        """更新种群数量"""
        if growth_factor <= 0.01:
            # 环境不适，种群减少
            self.population_size *= (1 - self.mortality_rate * 2 * dt / 3600.0)
            return
        
        # 逻辑斯蒂增长
        carrying_capacity = self.max_population * resource_available
        growth = self.growth_rate * growth_factor * self.population_size * (1 - self.population_size / carrying_capacity) * dt / 3600.0
        death = self.mortality_rate * self.population_size * dt / 3600.0
        
        self.population_size = max(1.0, min(carrying_capacity, self.population_size + growth - death))
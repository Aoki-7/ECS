#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:farm_component.py
@说明:农场组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class FarmPlotComponent(Component):
    """
    农田地块组件 - 纯数据版
    """
    # 土壤质量
    soil_quality: float = 0.5
    
    # 作物类型
    crop_type: Optional[str] = None
    
    # 生长阶段
    growth_stage: float = 0.0
    
    # 水分
    moisture: float = 0.5
    
    # 状态
    is_planted: bool = False
    is_harvestable: bool = False
    
    # 历史
    planting_tick: int = 0
    last_harvest_tick: int = 0
    
    # 产量记录
    yield_history: List[Dict] = field(default_factory=list)
    
    # 健康
    health: float = 1.0
    
    # 水分水平
    water_level: float = 0.5
    
    # 灌溉状态
    irrigated_this_cycle: bool = False


@dataclass(slots=True)
class FarmingKnowledgeComponent(Component):
    """
    农业知识组件 - 纯数据版
    """
    # 已知作物
    known_crops: List[str] = field(default_factory=list)
    
    # 种植技术
    planting_techniques: Dict[str, float] = field(default_factory=dict)
    
    # 灌溉知识
    irrigation_knowledge: float = 0.0
    
    # 土壤管理
    soil_management: float = 0.0
    
    # 作物经验
    crop_experience: Dict[str, Dict] = field(default_factory=dict)
    
    # 灌溉实验
    irrigation_experiments: List[Dict] = field(default_factory=list)


@dataclass(slots=True)
class IrrigationComponent(Component):
    """
    灌溉组件 - 纯数据版
    """
    # 水源
    water_source: str = "river"
    
    # 灌溉效率
    efficiency: float = 0.5
    
    # 覆盖范围
    coverage_radius: float = 10.0
    
    # 状态
    is_active: bool = True
    water_level: float = 1.0
    
    # 流量
    flow_rate: float = 0.2
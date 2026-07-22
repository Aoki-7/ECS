#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
尸体组件 v4.16.0
生物死亡后生成的尸体实体组件，参与生态分解循环
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from core.component import Component
from typing import Dict, Optional


class CorpseType(Enum):
    """尸体类型"""
    HUMAN = auto()        # 人类尸体
    ANIMAL = auto()       # 动物尸体
    PLANT = auto()        # 植物残体
    WOOD = auto()         # 木材/木质残体


class DecompositionStage(Enum):
    """分解阶段"""
    FRESH = auto()        # 新鲜：死亡0-24小时
    BLOAT = auto()        # 肿胀：24-72小时，细菌繁殖产生气体
    ACTIVE_DECAY = auto() # 活跃腐烂：3-10天，软组织快速分解
    ADVANCED_DECAY = auto() # 深度腐烂：10-25天，大部分软组织消失
    DRY_REMAINS = auto()  # 干尸/残骸：25天以上，只剩骨骼/毛发/角质


@dataclass(slots=True)
class CorpseComponent(Component):
    """
    尸体组件
    所有死亡生物/植物残体挂载此组件，参与分解循环
    """
    
    # 基础属性
    corpse_type: CorpseType = CorpseType.ANIMAL
    original_entity_type: str = "unknown"  # 原实体类型（如"human"/"deer"/"oak"）
    mass: float = 10.0  # 尸体质量（kg）
    age: float = 0.0  # 死亡时间（小时）
    
    # 分解属性
    decomposition_stage: DecompositionStage = DecompositionStage.FRESH
    decomposition_rate: float = 1.0  # 分解速率系数，受温度/湿度/微生物影响
    remaining_mass: float = field(init=False)  # 剩余质量
    
    # 养分含量（占剩余质量的百分比）
    nutrient_content: Dict[str, float] = field(default_factory=lambda: {
        "nitrogen": 0.03,   # 氮含量 3%
        "phosphorus": 0.01, # 磷含量 1%
        "potassium": 0.02,  # 钾含量 2%
        "carbon": 0.5,      # 碳含量 50%
    })
    
    # 环境影响
    toxic_level: float = 0.0  # 毒性水平 0-1，死亡原因是中毒/瘟疫时会升高
    attracts_scavengers: bool = True  # 是否吸引食腐动物
    
    def __post_init__(self):
        self.remaining_mass = self.mass
    
    def decompose(self, dt: float, environmental_factor: float = 1.0) -> Dict[str, float]:
        """
        执行分解过程
        :param dt: 时间步长（小时）
        :param environmental_factor: 环境综合因子（温度/湿度/微生物活性综合）
        :return: 释放到环境的养分量
        """
        if self.decomposition_stage == DecompositionStage.DRY_REMAINS:
            # 干尸阶段分解极慢
            actual_rate = 0.01 * self.decomposition_rate * environmental_factor
        else:
            actual_rate = self.decomposition_rate * environmental_factor
        
        # 计算分解量
        decompose_mass = min(self.remaining_mass, self.remaining_mass * actual_rate * dt / 100.0)
        self.remaining_mass -= decompose_mass
        self.age += dt
        
        # 更新分解阶段
        self._update_decomposition_stage()
        
        # 计算释放的养分量
        released_nutrients = {}
        for nutrient, percentage in self.nutrient_content.items():
            released_nutrients[nutrient] = decompose_mass * percentage
        
        return released_nutrients
    
    def _update_decomposition_stage(self) -> None:
        """根据死亡时间更新分解阶段"""
        if self.age < 24:
            self.decomposition_stage = DecompositionStage.FRESH
        elif self.age < 72:
            self.decomposition_stage = DecompositionStage.BLOAT
        elif self.age < 240:  # 10天
            self.decomposition_stage = DecompositionStage.ACTIVE_DECAY
        elif self.age < 600:  # 25天
            self.decomposition_stage = DecompositionStage.ADVANCED_DECAY
        else:
            self.decomposition_stage = DecompositionStage.DRY_REMAINS
    
    def is_fully_decomposed(self) -> bool:
        """是否完全分解"""
        return self.remaining_mass <= 0.01 * self.mass
    
    def get_decomposition_description(self) -> str:
        """获取分解状态描述"""
        stage_desc = {
            DecompositionStage.FRESH: "新鲜尸体",
            DecompositionStage.BLOAT: "肿胀腐烂",
            DecompositionStage.ACTIVE_DECAY: "活跃腐烂",
            DecompositionStage.ADVANCED_DECAY: "深度腐烂",
            DecompositionStage.DRY_REMAINS: "干尸残骸",
        }
        
        decomp_percent = (1 - self.remaining_mass / self.mass) * 100
        return f"{stage_desc[self.decomposition_stage]}，已分解{decomp_percent:.1f}%"

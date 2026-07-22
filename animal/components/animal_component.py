#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物基础标记组件

用于标识动物实体及其基本生态属性。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class AnimalComponent(Component):
    """
    动物组件（支持自发演化版本）

    属性:
        species: 物种标识名
        diet: 食性 ("herbivore" 食草, "carnivore" 食肉, "omnivore" 杂食) - 兼容旧API，自动由carnivore_preference计算
        carnivore_preference: 肉食偏好 0-1，0=纯食草，1=纯食肉，中间值为杂食
        size: 体型大小（任意单位，越大越强，需要的食物越多）
        movement_speed: 移动速度，影响觅食和捕食成功率
        reproduction_rate: 繁殖率，越高繁殖越快但寿命越短
        mutation_rate: 变异率，繁殖时产生突变的概率
        grazing_range: 觅食范围 (m)
        gender: 性别 ("male" 雄性, "female" 雌性)
        age: 当前年龄 (小时)
        max_age: 最大寿命 (小时)
        is_adult: 是否成年
        social_group_id: 所属社交群体 ID (-1 表示独行)
        territory_id: 领地 ID (-1 表示无领地)
        parent_species: 父代物种名，用于演化追踪
    """
    species: str = "basic"
    diet: str = "herbivore"  # 保留字段，兼容旧API初始化，运行时由property动态返回
    carnivore_preference: float = 0.0  # 默认纯食草
    size: float = 1.0
    movement_speed: float = 1.0
    reproduction_rate: float = 0.1
    mutation_rate: float = 0.01  # 1%变异概率
    grazing_range: float = 10.0  # 改为米单位
    gender: str = "male"
    age: float = 0.0
    max_age: float = 8760.0  # 默认 1 年
    is_adult: bool = False
    social_group_id: int = -1
    territory_id: int = -1
    parent_species: str = "unknown"
    
    def __post_init__(self):
        """初始化同步食性和肉食偏好"""
        # 旧代码初始化传入diet参数时，同步到carnivore_preference
        if self.diet == "herbivore":
            self.carnivore_preference = 0.0
        elif self.diet == "carnivore":
            self.carnivore_preference = 1.0
        else:
            self.carnivore_preference = 0.5
    
    @property
    def diet(self) -> str:
        """兼容旧API：自动根据肉食偏好返回食性分类"""
        if self.carnivore_preference < 0.3:
            return "herbivore"
        elif self.carnivore_preference > 0.7:
            return "carnivore"
        else:
            return "omnivore"
    
    @diet.setter
    def diet(self, value: str) -> None:
        """兼容旧API：设置食性时自动同步肉食偏好"""
        if value == "herbivore":
            self.carnivore_preference = 0.0
        elif value == "carnivore":
            self.carnivore_preference = 1.0
        else:
            self.carnivore_preference = 0.5
        # 同步存储字段
        object.__setattr__(self, 'diet', value)
    
    def get_trait(self, trait_name: str) -> float:
        """获取性状值，用于演化评估"""
        return getattr(self, trait_name, 0.0)
    
    def mutate(self) -> None:
        """随机变异，调整性状"""
        import random
        # 只有变异率达标才发生变异
        if random.random() > self.mutation_rate:
            return
        
        # 体型变异 ±10%
        if random.random() < 0.3:
            self.size *= random.uniform(0.9, 1.1)
        # 食性偏好变异 ±0.2
        if random.random() < 0.25:
            self.carnivore_preference = max(0.0, min(1.0, self.carnivore_preference + random.uniform(-0.2, 0.2)))
        # 移动速度变异 ±10%
        if random.random() < 0.2:
            self.movement_speed *= random.uniform(0.9, 1.1)
        # 繁殖率变异 ±10%，同时反向影响寿命
        if random.random() < 0.15:
            repro_change = random.uniform(-0.1, 0.1)
            self.reproduction_rate *= (1 + repro_change)
            self.max_age *= (1 - repro_change * 0.5)  # 繁殖率越高寿命越短，权衡机制


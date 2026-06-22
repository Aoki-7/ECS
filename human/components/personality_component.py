#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:personality_component.py
@说明:性格组件 - 纯数据版

基于大五人格模型（OCEAN）：
- Openness: 开放性（好奇心、创造力）
- Conscientiousness: 尽责性（组织性、自律）
- Extraversion: 外向性（社交性、活力）
- Agreeableness: 宜人性（合作性、信任）
- Neuroticism: 神经质（情绪稳定性）
'''

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class PersonalityComponent(Component):
    """
    性格组件 - 纯数据版

    Attributes:
        openness: 开放性 [0.0, 1.0]
        conscientiousness: 尽责性 [0.0, 1.0]
        extraversion: 外向性 [0.0, 1.0]
        agreeableness: 宜人性 [0.0, 1.0]
        neuroticism: 神经质 [0.0, 1.0]
    """
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    def __post_init__(self):
        # 限制所有值在 [0.0, 1.0] 范围内
        for attr in ['openness', 'conscientiousness', 'extraversion', 
                     'agreeableness', 'neuroticism']:
            value = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, value)))

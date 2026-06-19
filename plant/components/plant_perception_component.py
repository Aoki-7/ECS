#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物感知组件

植物虽然没有神经系统，但具有化学感知能力：
- 光感知：向光性（检测光源方向）
- 水感知：向水性（检测土壤水分梯度）
- 重力感知：向地性（根向地/茎背地）
- 化学感知：检测土壤养分、邻近植物化学物质
"""

from dataclasses import dataclass, field
from core.component import Component


@dataclass(slots=True)
class PlantPerceptionComponent(Component):
    """
    植物感知组件

    模拟植物的化学/物理感知能力（非神经感知）。
    """
    # 光感知
    light_sensitivity: float = 1.0  # 光敏感度
    last_light_direction: float = 0.0  # 上次检测到的光源方向（角度）
    last_light_intensity: float = 0.0  # 上次检测到的光强度

    # 水感知
    water_sensitivity: float = 1.0  # 水敏感度
    soil_moisture: float = 0.5  # 当前土壤湿度（0-1）
    water_gradient_x: float = 0.0  # 水分梯度 X 方向
    water_gradient_y: float = 0.0  # 水分梯度 Y 方向

    # 重力感知
    gravity_response: float = 1.0  # 重力响应强度

    # 化学感知
    nutrient_sensitivity: float = 1.0  # 养分敏感度
    detected_nutrients: dict = field(default_factory=dict)  # 检测到的养分 {type: amount}

    # 邻近植物检测（化感作用）
    nearby_plants: list = field(default_factory=list)  # 邻近植物实体ID列表
    allelopathy_detected: bool = False  # 是否检测到化感物质

    # 感知记录（用于记忆形成）
    perception_history: list = field(default_factory=list)  # [(time, type, value)]

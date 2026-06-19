#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
速度组件

v3.9 迁移：从 core/components/ 移回 human/components/abilities/
保持 core 层纯粹性。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class VelocityComponent(Component):
    """空间移动速度"""
    speed: float = 0.0  # 单位 m/s
    vx: float = 0.0
    vy: float = 0.0

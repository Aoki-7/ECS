#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
死亡状态组件

v3.9 迁移：从 core/components/ 移回 human/components/physiological/
保持 core 层纯粹性。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class DeathComponent(Component):
    """死亡状态组件 — 标记实体的死亡状态"""
    is_dead: bool = False
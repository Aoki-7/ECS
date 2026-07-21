#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@文件:reproduction_component.py
@说明:繁衍组件
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from dataclasses import dataclass
from typing import Optional

from core.component import Component


@dataclass(slots=True)
class ReproductionComponent(Component):
    """
    繁衍组件
    处理怀孕和生育。
    """
    is_pregnant: bool = False
    pregnancy_time: float = 0.0  # 怀孕时间（小时）
    pregnancy_duration: float = 7200.0  # 10个月 ≈ 7200小时，符合现实孕育周期

    partner_id: Optional[int] = None  # 生育伴侣ID

    # 生育间隔（避免连续生育）
    last_birth_time: float = 0.0
    birth_cooldown: float = 8760.0  # 1年 ≈ 8760小时，自然生育间隔

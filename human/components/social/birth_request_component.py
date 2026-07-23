#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
BirthRequestComponent — 生育请求组件

由 ReproductionSystem 在怀孕期满时挂载到孕妇实体上，
由 BirthSystem 读取并执行实际的新生儿创建。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class BirthRequestComponent(Component):
    """
    生育请求组件

    数据由 ReproductionSystem 准备，执行由 BirthSystem 处理。
    解耦目的：ReproductionSystem 不直接调用 HumanFactory 或 TribeSystem。
    """
    child_name: str = ""
    child_x: int = 0
    child_y: int = 0
    partner_id: int = 0
"""
组件包 — 纯数据组件定义

依赖：
    - environment.light_field/
    - core/
    - space/
    - time_module/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光场组件模块 — 辐射场的数据定义

包含：
    - LightFieldComponent      : 地表光照状态（直射辐射、散射辐射、总辐射）
    - SolarPositionComponent   : 太阳位置（高度角、方位角）
    - SolarRadiationComponent  : 大气层顶辐射（TOA）
    - LightScatterComponent    : 大气散射参数（气溶胶、云光学厚度）

与 light_field/systems/ 的关系：
    - components/ 存储辐射计算结果
    - systems/ 的 LightFieldSystem 执行辐射传输计算
"""

from .light_field_component import LightFieldComponent

__all__ = ['LightFieldComponent']


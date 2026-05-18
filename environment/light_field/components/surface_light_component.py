#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:surface_light_component.py
@说明:地表光照组件 — 修复 dataclass slots 缺少类型注解的问题
@时间:2026/05/16
@作者:Sherry
@版本:2.0
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class SurfaceLightComponent(Component):
    """
    地表光照组件
    挂在世界实体上，由 LightFieldSystem 更新。
    EnvironmentSyncSystem 据此推演到每个空间单元格。
    """

    direct_light: float = 0.0   # 地表直射光 (W/m²)
    diffuse_light: float = 0.0  # 地表散射光 (W/m²)

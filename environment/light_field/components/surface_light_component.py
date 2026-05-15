#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:surface_light_component.py
@说明:地表光照组件
@时间:2026/03/11 12:08:44
@作者:Sherry
@版本:1.0
'''


from dataclasses import dataclass

from core.component import Component

@dataclass(slots=True)
class SurfaceLightComponent(Component):
    """
    地表光照组件
    挂在space上，空间/地块entity
    """

    direct_light = 0.0
    diffuse_light = 0.0
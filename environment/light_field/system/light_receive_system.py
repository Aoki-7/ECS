#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:light_receive_system.py
@说明:光接受系统
@时间:2026/03/11 14:41:49
@作者:Sherry
@版本:1.0
'''

from core.system import System
from core.world import World

from environment.light_field.components.light_receiver_component import LightReceiverComponent
from environment.light_field.components.surface_light_component import SurfaceLightComponent


class LightReceiverSystem(System):
    """
        分配给所有带有LightReceiverComponent的实体
    """
    def update(self, world: World, delta_hours: float = 0.0):

        surface_light = world._world_entity.get_component(SurfaceLightComponent)
        surface_light: SurfaceLightComponent

        if surface_light is None:
            return

        for entity, [light] in world.get_components(LightReceiverComponent):
            light: LightReceiverComponent

            shade = getattr(light, "shade_ratio", 0.0)

            light.received_direct = (
                surface_light.direct_light * (1 - shade)
            )

            light.received_diffuse = surface_light.diffuse_light

            light.received_total = (
                light.received_direct +
                light.received_diffuse
            )
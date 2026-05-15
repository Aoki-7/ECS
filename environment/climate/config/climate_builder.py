#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:climate_builder.py
@说明:气候系统构建器，负责根据气候配置表创建气候组件并初始化状态
@时间:2026/03/08 11:49:15
@作者:Sherry
@版本:1.0
'''



from core.world import World

from environment.climate.climate_component import ClimateComponent
from environment.climate.climate_system import ClimateSystem


class ClimateBuilder:
    @staticmethod
    def build(world: World, profile = None):
        """
        根据气候配置表创建气候组件并初始化状态
        """
        world._world_entity.add_component(ClimateComponent())

        climate_system = ClimateSystem()

        return [climate_system]






#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:weather_builder.py
@说明:天气系统构建器，负责根据天气配置表创建天气组件并初始化状态
@时间:2026/03/08 11:22:13
@作者:Sherry
@版本:1.0
'''


from core.world import World


from environment.season.season_component import SeasonComponent
from environment.season.season_system import SeasonSystem



class SeasonBuilder:
    @staticmethod
    def build(world: World, profile = None):
        """
        根据季节配置表创建季节组件并初始化状态
        """
        world.get_world_entity().add_component(SeasonComponent())

        systems = [SeasonSystem()]

        return systems
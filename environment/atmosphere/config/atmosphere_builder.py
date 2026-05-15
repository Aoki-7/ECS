

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
大气相关组件和系统构建器
"""

from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.atmosphere.system.atmosphere_system import AtmosphereSystem
from environment.atmosphere.system.pressusre_system import PressureSystem
from environment.atmosphere.system.wind_system import WindSystem
from environment.atmosphere.system.cloud_system import CloudSystem
from environment.atmosphere.system.thermodynamics_system import ThermodynamicsSystem

class AtmosphereBuilder:

    @staticmethod
    def build(world: World, profile = None):
        
        world._world_entity.add_component(AtmosphereComponent())

        # 创建大气系统列表（按执行顺序）
        atmos_systems = [
            AtmosphereSystem(),      # 基础大气物理系统
            PressureSystem(),       # 气压变化
            WindSystem(),           # 风场计算
            CloudSystem(),          # 云层模拟
            ThermodynamicsSystem()   # 热力学过程
        ]

        # 可选：根据 profile 调整子系统的优先级或参数
        if profile:
            atmos_systems = AtmosphereBuilder._apply_profile(atmos_systems, profile)

        return atmos_systems

    @staticmethod
    def _apply_profile(systems, profile):
        """
        根据配置 profile 调整系统参数
        
        Args:
            systems: 系统列表
            profile: 配置文件，包含各系统的定制参数
        
        Returns:
            调整后的系统列表
        """
        # TODO: 实现配置应用逻辑
        return systems
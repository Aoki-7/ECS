

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
大气相关组件和系统构建器
"""

from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.atmosphere.system.atmosphere_system import AtmosphereSystem
from environment.atmosphere.system.pressure_system import PressureSystem
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
        if profile is None:
            return systems

        # 支持 AtmosphereConfig 或 dict 类型的 profile
        subsystems_config = getattr(profile, 'subsystems', None)
        if subsystems_config is None and isinstance(profile, dict):
            subsystems_config = profile.get('subsystems', [])

        if not subsystems_config:
            return systems

        # 构建配置映射：name -> config
        config_map = {}
        for sub in subsystems_config:
            name = getattr(sub, 'name', sub.get('name') if isinstance(sub, dict) else None)
            if name:
                config_map[name] = sub

        filtered_systems = []
        for system in systems:
            sys_name = system.__class__.__name__.lower().replace('system', '')
            config = config_map.get(sys_name)
            if config is None:
                filtered_systems.append(system)
                continue

            enabled = getattr(config, 'enabled', config.get('enabled') if isinstance(config, dict) else True)
            if not enabled:
                continue  # 跳过禁用的子系统

            priority = getattr(config, 'priority', config.get('priority') if isinstance(config, dict) else None)
            if priority is not None:
                system.priority = priority

            params = getattr(config, 'params', config.get('params') if isinstance(config, dict) else {})
            if params:
                for key, value in params.items():
                    if hasattr(system, key):
                        setattr(system, key, value)

            filtered_systems.append(system)

        return filtered_systems
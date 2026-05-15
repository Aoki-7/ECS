#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气系统（核心协调器）[扩展版]

负责协调各子系统、初始化默认值、整体状态更新。
基础物理计算已移至 AtmosphereComponent，这里仅做系统集成。
"""

from typing import List, Dict, Any
from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
<<<<<<< HEAD
=======
from environment.weather.components.weather_component import WeatherComponent
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc

# Atmospheric system priority (lower = runs earlier)
ATMOSPHERE_SYSTEM_PRIORITY = 140


class AtmosphereSystem(System):
    """
    大气系统（核心协调器）
    
    架构层级：
    Climate
      ↓
    Weather (天气现象)
      ↓
    Atmosphere (物理状态)
      ↓
    Wind / Soil / Pollution
    
    职责：
    - 确保 AtmosphereComponent 在 World 中初始化
    - 协调各子系统运行顺序
    - 提供整体状态查询接口
    """

    # Subsystem priorities (lower = runs earlier)
    SUBSYSTEM_PRIORITIES = {
        "pressure": 130,
        "thermodynamics": 130,
        "cloud": 140,
        "wind": 150,
        "convection": 160,
    }

    def on_add(self, world: World):
        """系统被添加到 world 时调用"""
        super().on_add(world)
        
        # 确保 AtmosphereComponent 存在，若不存在则创建默认实例
        if not world.get_component_by_type(AtmosphereComponent):
            atm = AtmosphereComponent()
            world._world_entity.add_component(atm)

    def on_remove(self, world: World):
        """系统从 world 移除时调用"""
        super().on_remove(world)

    def update(self, world: World, delta_hours: float):
        """
        大气系统更新（作为协调器）

        Args:
            world: 世界对象
            delta_hours: 时间步长（小时）
        """
        if not self.is_enabled:
            return

        # 获取所有子系统，按优先级排序
        subsystems = self._get_subsystems(world)
        subsystems.sort(key=lambda s: s.priority)

        # 依次更新各子系统
        for subsystem in subsystems:
            if subsystem.is_enabled:
                subsystem.update(world, delta_hours)

    def _get_subsystems(self, world: World) -> List[System]:
        """获取所有大气相关子系统"""
        subsystems = []
        
        # 尝试导入各子系统，避免硬编码依赖
        from environment.atmosphere.system.pressure_system import PressureSystem as Psys
        from environment.atmosphere.system.thermodynamics_system import ThermodynamicsSystem as Tsys
        from environment.atmosphere.system.cloud_system import CloudSystem as Csys
        from environment.atmosphere.system.wind_system import WindSystem as Wsys
        from environment.atmosphere.system.convection_system import ConvectionSystem as Consy
        
        subsystems.append(Psys())
        subsystems.append(Tsys())
        subsystems.append(Csys())
        subsystems.append(Wsys())
        subsystems.append(Consy())
        
        return subsystems

    def get_atmosphere_state(self, world: World) -> AtmosphereComponent | None:
        """获取当前大气的物理状态"""
        atm = world.get_component_by_type(AtmosphereComponent)
        return atm if atm else None
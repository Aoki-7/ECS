#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大气系统（核心协调器）[v2.0] — 接入物理天气模块

【架构层级】
PhysicalWeatherSystem (物理天气演化)
    ↓
AtmosphereSystem (大气微观物理层)
    ├── PressureSystem        → ISA 气压 + 空气密度
    ├── ThermodynamicsSystem  → 饱和水汽压 + 相对湿度转换
    ├── CloudSystem          → 云密度估算
    ├── WindSystem           → 风场方向微调
    └── ConvectionSystem     → 对流强度 + 湍流
    ↓
LightAtmosphereCouplingSystem (光学散射)

【职责】
- 确保 AtmosphereComponent 在 World 中初始化
- 协调各子系统按顺序运行
- 提供整体状态查询接口
- 不直接计算物理量，由各子系统负责
"""

from typing import List
import logging
from core.system import System
from core.world import World

logger = logging.getLogger(__name__)

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


ATMOSPHERE_SYSTEM_PRIORITY = 140


class AtmosphereSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    大气系统（核心协调器）

    作为 PhysicalWeatherSystem 的下游精细处理层，
    将简化的天气物理量转换为更精细的大气参数。
    """

    # 子系统执行顺序（在此列表中的顺序即为执行顺序）
    SUBSYSTEM_CLASSES = [
        ("pressure", "environment.atmosphere.system.pressure_system", "PressureSystem"),
        ("thermodynamics", "environment.atmosphere.system.thermodynamics_system", "ThermodynamicsSystem"),
        ("cloud", "environment.atmosphere.system.cloud_system", "CloudSystem"),
        ("wind", "environment.atmosphere.system.wind_system", "WindSystem"),
        ("convection", "environment.atmosphere.system.convection_system", "ConvectionSystem"),
    ]

    def __init__(self):
        super().__init__()
        self._subsystems: List[System] = []
        self._init_subsystems()

    def _init_subsystems(self):
        """动态初始化所有子系统"""
        self._subsystems = []
        for name, module_path, class_name in self.SUBSYSTEM_CLASSES:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                subsystem = cls()
                subsystem.priority = ATMOSPHERE_SYSTEM_PRIORITY
                self._subsystems.append(subsystem)
            except (ImportError, AttributeError) as e:
                logger.warning(f"[AtmosphereSystem] 子系统 {name} 加载失败: {e}")

    def on_add(self, world: World):
        """系统被添加到 world 时调用"""
        super().on_add(world)
        if not world.get_world_component(AtmosphereComponent):
            atm = AtmosphereComponent()
            world_entity = world.get_world_entity()
            if world_entity is not None:
                world.add_component(world_entity, atm)
            else:
                world_entity = world.create_entity()
                world.add_component(world_entity, atm)
                world.set_world_entity(world_entity)

    def on_remove(self, world: World):
        """系统移除时清理 AtmosphereComponent"""
        we = world.get_world_entity()
        if we:
            comp = world.get_component(we, AtmosphereComponent)
            if comp:
                we.remove_component(AtmosphereComponent)

    def update(self, world: World, delta_hours: float):
        """
        大气系统更新（协调器）

        依次调用各子系统，将 PhysicalWeatherComponent 的物理量
        转换为 AtmosphereComponent 的精细大气参数。
        """
        if not self.is_enabled:
            return

        for subsystem in self._subsystems:
            if subsystem.is_enabled:
                try:
                    subsystem.update(world, delta_hours)
                except Exception as e:
                    logger.warning(f"[AtmosphereSystem] 子系统 {subsystem.__class__.__name__} 执行失败: {e}")

    def get_atmosphere_state(self, world: World) -> AtmosphereComponent | None:
        """获取当前大气的物理状态"""
        return world.get_world_component(AtmosphereComponent)
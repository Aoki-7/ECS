#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境连续统处理器测试
"""

import pytest
import math

from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType

from environment.continuum.continuum_processors import (
    ThermalDiffusionProcessor,
    HumidityDiffusionProcessor,
    GravityWaterFlowProcessor,
    WindAdvectionProcessor,
    SelfRecoveryProcessor,
)
from environment.continuum.continuum_config import NEIGHBOR_OFFSETS_MOORE


class TestThermalDiffusionProcessor:
    """测试热扩散处理器"""

    def test_temperature_equalizes(self):
        """测试高温向低温扩散"""
        world = World()
        grid = {}

        # 创建两个相邻单元格，温度不同
        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0, soil_temperature=25.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0, soil_temperature=15.0))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        processor = ThermalDiffusionProcessor(NEIGHBOR_OFFSETS_MOORE)
        processor.process(world, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        # 高温降低，低温升高
        assert env1.air_temperature < 30.0
        assert env2.air_temperature > 10.0

    def test_water_buffering(self):
        """测试水域缓冲效果"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.WATER, elevation=0.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        processor = ThermalDiffusionProcessor(NEIGHBOR_OFFSETS_MOORE)
        processor.process(world, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        # 水域温度变化应较小（缓冲效应）
        assert env1.air_temperature <= 30.0


class TestHumidityDiffusionProcessor:
    """测试湿度扩散处理器"""

    def test_humidity_equalizes(self):
        """测试高湿向低湿扩散"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_humidity=0.9, soil_moisture=0.8))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_humidity=0.1, soil_moisture=0.2))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        processor = HumidityDiffusionProcessor(NEIGHBOR_OFFSETS_MOORE)
        processor.process(world, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        assert env1.air_humidity < 0.9
        assert env2.air_humidity > 0.1


class TestGravityWaterFlowProcessor:
    """测试重力水流处理器"""

    def test_water_flows_downhill(self):
        """测试水向低处流"""
        world = World()
        grid = {}

        # 高处
        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(soil_moisture=0.8))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.HILL, elevation=50.0))
        grid[(0, 0)] = e1

        # 低处
        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(soil_moisture=0.2))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        processor = GravityWaterFlowProcessor()
        processor.process(world, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        # 高处失水，低处得水
        assert env1.soil_moisture < 0.8
        assert env2.soil_moisture > 0.2


class TestWindAdvectionProcessor:
    """测试风驱平流处理器"""

    def test_wind_transfers_heat(self):
        """测试风传递热量"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0, wind_speed=5.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0, wind_speed=5.0))
        grid[(1, 0)] = e2

        # 西风（从西向东吹）
        processor = WindAdvectionProcessor(NEIGHBOR_OFFSETS_MOORE, prevailing_wind_deg=270.0)
        processor.process(world, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        # 热量随风传递
        assert env1.air_temperature < 30.0 or env2.air_temperature > 10.0


class TestSelfRecoveryProcessor:
    """测试生态自恢复处理器"""

    def test_recovery_towards_climax(self):
        """测试向顶极状态恢复"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(
            air_temperature=10.0,  # 偏离顶极（平原约20度）
            air_humidity=0.3,
            soil_moisture=0.2,
            nitrogen=10.0,
            phosphorus=5.0,
            potassium=10.0,
        ))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        processor = SelfRecoveryProcessor()
        processor.process(world, grid, 10.0)

        env = world.get_component(e1, EnvironmentComponent)

        # 应向顶极状态恢复（温度升高，湿度增加）
        assert env.air_temperature > 10.0
        assert env.air_humidity > 0.3
        assert env.soil_moisture > 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

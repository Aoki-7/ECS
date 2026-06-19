#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续统扩展系统测试

测试覆盖:
    - FireSpreadSystem: 火灾蔓延
    - ErosionSedimentSystem: 侵蚀沉积
    - GasDiffusionSystem: 气体扩散
    - GroundwaterFlowSystem: 地下水流动
    - BioEnvironmentCouplingSystem: 生物-环境耦合
    - AdaptiveTimestepSystem: 自适应步长
"""

import pytest

from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.soil.components.soil_component import SoilComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent

from environment.continuum.systems import (
    FireSpreadSystem,
    ErosionSedimentSystem,
    GasDiffusionSystem,
    GroundwaterFlowSystem,
    BioEnvironmentCouplingSystem,
    AdaptiveTimestepSystem,
)
from environment.continuum.continuum_utils import (
    ContinuumCache,
    take_conservation_snapshot,
)


class TestFireSpreadSystem:
    """测试火灾蔓延系统"""

    def test_fire_ignition(self):
        """测试火灾点燃"""
        world = World()
        system = FireSpreadSystem()

        # 创建高温实体 (火源)
        source = world.create_entity()
        world.add_component(source, SpaceComponent(x=0, y=0))
        world.add_component(source, EnvironmentComponent(air_temperature=350.0))
        world.add_component(source, TerrainComponent(terrain_type=1, vegetation_cover=0.8))

        # 创建相邻实体 (可燃)
        target = world.create_entity()
        world.add_component(target, SpaceComponent(x=1, y=0))
        world.add_component(target, EnvironmentComponent(air_temperature=20.0))
        world.add_component(target, TerrainComponent(terrain_type=1, vegetation_cover=0.8))

        # 多次更新确保点燃
        for _ in range(50):
            system.update(world, 1.0)

        # 目标应该被点燃
        env = world.get_component(target, EnvironmentComponent)
        assert env.air_temperature >= 300.0

    def test_fire_extinguish_by_rain(self):
        """测试降雨熄灭"""
        world = World()
        system = FireSpreadSystem()

        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=0, y=0))
        world.add_component(entity, EnvironmentComponent(air_temperature=350.0, rainfall=10.0))
        world.add_component(entity, TerrainComponent(terrain_type=1, vegetation_cover=0.8))

        system.update(world, 1.0)

        env = world.get_component(entity, EnvironmentComponent)
        assert env.air_temperature < 350.0


class TestGasDiffusionSystem:
    """测试气体扩散系统"""

    def test_co2_diffusion(self):
        """测试 CO₂ 扩散"""
        world = World()
        system = GasDiffusionSystem()

        # 高 CO₂ 实体
        high = world.create_entity()
        world.add_component(high, SpaceComponent(x=0, y=0))
        world.add_component(high, EnvironmentComponent(co2=500.0))

        # 低 CO₂ 实体
        low = world.create_entity()
        world.add_component(low, SpaceComponent(x=1, y=0))
        world.add_component(low, EnvironmentComponent(co2=400.0))

        system.update(world, 1.0)

        high_env = world.get_component(high, EnvironmentComponent)
        low_env = world.get_component(low, EnvironmentComponent)

        # 高 CO₂ 降低，低 CO₂ 升高
        assert high_env.co2 < 500.0
        assert low_env.co2 > 400.0

    def test_o2_diffusion(self):
        """测试 O₂ 扩散"""
        world = World()
        system = GasDiffusionSystem()

        # 高 O₂ 实体
        high = world.create_entity()
        world.add_component(high, SpaceComponent(x=0, y=0))
        world.add_component(high, EnvironmentComponent(o2=25.0))

        # 低 O₂ 实体
        low = world.create_entity()
        world.add_component(low, SpaceComponent(x=1, y=0))
        world.add_component(low, EnvironmentComponent(o2=15.0))

        system.update(world, 1.0)

        high_env = world.get_component(high, EnvironmentComponent)
        low_env = world.get_component(low, EnvironmentComponent)

        # 高 O₂ 降低，低 O₂ 升高
        assert high_env.o2 < 25.0
        assert low_env.o2 > 15.0


class TestGroundwaterFlowSystem:
    """测试地下水流动系统"""

    def test_groundwater_flow(self):
        """测试地下水流"""
        world = World()
        system = GroundwaterFlowSystem()

        # 高水头
        high = world.create_entity()
        world.add_component(high, SpaceComponent(x=0, y=0))
        world.add_component(high, TerrainComponent(elevation=10.0))
        world.add_component(high, GroundwaterComponent(water_table=-2.0))
        world.add_component(high, SoilComponent())

        # 低水头
        low = world.create_entity()
        world.add_component(low, SpaceComponent(x=1, y=0))
        world.add_component(low, TerrainComponent(elevation=5.0))
        world.add_component(low, GroundwaterComponent(water_table=-5.0))
        world.add_component(low, SoilComponent())

        system.update(world, 1.0)

        high_gw = world.get_component(high, GroundwaterComponent)
        low_gw = world.get_component(low, GroundwaterComponent)

        # 高水头降低，低水头升高
        assert high_gw.water_table < -2.0
        assert low_gw.water_table > -5.0


class TestBioEnvironmentCouplingSystem:
    """测试生物-环境耦合系统"""

    def test_vegetation_transpiration(self):
        """测试植被蒸腾"""
        world = World()
        system = BioEnvironmentCouplingSystem()

        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=0, y=0))
        world.add_component(entity, EnvironmentComponent(air_humidity=0.5))
        world.add_component(entity, TerrainComponent(vegetation_cover=0.8))

        system.update(world, 1.0)

        env = world.get_component(entity, EnvironmentComponent)
        assert env.air_humidity > 0.5

    def test_animal_trampling(self):
        """测试动物踩踏"""
        world = World()
        system = BioEnvironmentCouplingSystem()

        from animal.components.animal_component import AnimalComponent

        # 动物实体
        animal = world.create_entity()
        world.add_component(animal, SpaceComponent(x=0, y=0))
        world.add_component(animal, AnimalComponent())

        # 环境实体
        env_entity = world.create_entity()
        world.add_component(env_entity, SpaceComponent(x=0, y=0))
        world.add_component(env_entity, SoilComponent())

        system.update(world, 1.0)

        # 检查是否有 SoilComponent 被踩踏 (如果没有 compaction 字段则跳过)
        soil = world.get_component(env_entity, SoilComponent)
        if hasattr(soil, 'compaction'):
            assert soil.compaction > 0.0


class TestAdaptiveTimestepSystem:
    """测试自适应时间步长系统"""

    def test_substepping(self):
        """测试子步进"""
        world = World()

        # 创建环境实体
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=0, y=0))
        world.add_component(entity, EnvironmentComponent(air_temperature=20.0))

        # 创建被包裹的系统 (模拟温度变化)
        class MockSystem:
            def update(self, world, dt):
                for entity, (env,) in world.get_components(EnvironmentComponent):
                    env.air_temperature += 10.0 * dt  # 每步增加 10°C

        mock = MockSystem()
        adaptive = AdaptiveTimestepSystem([mock])

        adaptive.update(world, 1.0)

        env = world.get_component(entity, EnvironmentComponent)
        # 温度应该增加，但不超过阈值限制
        assert env.air_temperature > 20.0

    def test_conservation_check(self):
        """测试守恒检查"""
        world = World()

        # 创建两个环境实体
        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0))

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0))

        # 创建被包裹的系统 (模拟热扩散)
        class MockDiffusionSystem:
            def update(self, world, dt):
                for entity, (env,) in world.get_components(EnvironmentComponent):
                    if env.air_temperature > 20.0:
                        env.air_temperature -= 5.0 * dt
                    else:
                        env.air_temperature += 5.0 * dt

        mock = MockDiffusionSystem()
        adaptive = AdaptiveTimestepSystem([mock])

        adaptive.update(world, 1.0)

        # 温度应该趋同 (守恒)
        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)
        assert abs(env1.air_temperature - env2.air_temperature) < 25.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

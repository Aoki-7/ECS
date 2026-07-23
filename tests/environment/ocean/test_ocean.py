#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海洋系统测试

v3.5 新增
"""

import pytest

from core.world import World
from environment.ocean.components.ocean_current_component import OceanCurrentComponent
from environment.ocean.components.tide_component import TideComponent
from environment.ocean.systems.ocean_current_system import OceanCurrentSystem
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent


class TestOceanCurrentComponent:
    """测试洋流组件"""

    def test_default_values(self):
        comp = OceanCurrentComponent()
        assert comp.current_type == "warm"
        assert comp.salinity == 35.0
        assert comp.depth == "surface"

    def test_serialization(self):
        comp = OceanCurrentComponent(
            current_type="cold",
            velocity=(1.5, 2.0),
            temperature=5.0
        )
        data = comp.to_dict()
        restored = OceanCurrentComponent.from_dict(data)
        assert restored.current_type == "cold"
        assert restored.velocity == (1.5, 2.0)
        assert restored.temperature == 5.0


class TestTideComponent:
    """测试潮汐组件"""

    def test_default_values(self):
        comp = TideComponent()
        assert comp.tide_type == "semidiurnal"
        assert comp.tide_range == 4.0

    def test_serialization(self):
        comp = TideComponent(tide_type="diurnal", high_tide_level=3.0)
        data = comp.to_dict()
        restored = TideComponent.from_dict(data)
        assert restored.tide_type == "diurnal"
        assert restored.high_tide_level == 3.0


class TestOceanCurrentSystem:
    """测试洋流系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return OceanCurrentSystem()

    def test_warm_current_heats_air(self, world, system):
        """测试暖流加热空气"""
        # 暖流
        current_entity = world.create_entity()
        current = OceanCurrentComponent(current_type="warm", temperature=25.0)
        current_space = SpaceComponent(x=0, y=0)
        world.add_component(current_entity, current)
        world.add_component(current_entity, current_space)

        # 环境 (相邻单元格，确保影响发生)
        env_entity = world.create_entity()
        env = EnvironmentComponent(air_temperature=15.0)
        env_space = SpaceComponent(x=1, y=0)
        world.add_component(env_entity, env)
        world.add_component(env_entity, env_space)

        initial_temp = env.air_temperature
        system.update(world, 1.0)

        # 温度应该上升
        assert env.air_temperature > initial_temp

    def test_salinity_balance(self, world, system):
        """测试盐度平衡"""
        # 高盐度
        high = world.create_entity()
        high_current = OceanCurrentComponent(salinity=40.0)
        high_space = SpaceComponent(x=0, y=0)
        world.add_component(high, high_current)
        world.add_component(high, high_space)

        # 低盐度 (相邻单元格)
        low = world.create_entity()
        low_current = OceanCurrentComponent(salinity=30.0)
        low_space = SpaceComponent(x=1, y=0)
        world.add_component(low, low_current)
        world.add_component(low, low_space)

        system.update(world, 1.0)

        # 盐度应该趋同
        assert high_current.salinity < 40.0
        assert low_current.salinity > 30.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
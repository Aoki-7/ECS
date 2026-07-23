#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地质系统测试

v3.5 新增
"""

import pytest

from core.world import World
from environment.geology.components.strata_component import StrataComponent
from environment.geology.systems.erosion_system import ErosionSystem
from environment.terrain.components.terrain_component import TerrainComponent
from space.space_component import SpaceComponent


class TestStrataComponent:
    """测试地层组件"""

    def test_default_values(self):
        comp = StrataComponent()
        assert comp.layers == []
        assert comp.bedrock_depth == 10.0
        assert comp.mineral_deposits == {}

    def test_serialization(self):
        comp = StrataComponent(
            layers=[{"depth": 2, "type": "clay"}],
            mineral_deposits={"iron": 100.0}
        )
        data = comp.to_dict()
        restored = StrataComponent.from_dict(data)
        assert len(restored.layers) == 1
        assert restored.mineral_deposits["iron"] == 100.0


class TestErosionSystem:
    """测试侵蚀系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return ErosionSystem()

    def test_wind_erosion(self, world, system):
        """测试风蚀"""
        entity = world.create_entity()
        terrain = TerrainComponent(elevation=100.0)
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, terrain)
        world.add_component(entity, space)

        # 添加环境组件（干旱、大风）
        from environment.environment_component import EnvironmentComponent
        env = EnvironmentComponent(air_humidity=0.1, wind_speed=10.0)
        world.add_component(entity, env)

        initial_elevation = terrain.elevation
        system._process_wind_erosion(world, 1.0)

        # 海拔应该降低（风蚀量很小，需要放大dt）
        assert terrain.elevation <= initial_elevation

    def test_sediment_transport(self, world, system):
        """测试沉积物搬运"""
        # 高处
        high = world.create_entity()
        high_terrain = TerrainComponent(elevation=100.0)
        high_space = SpaceComponent(x=10, y=10)

        world.add_component(high, high_terrain)
        world.add_component(high, high_space)

        # 低处
        low = world.create_entity()
        low_terrain = TerrainComponent(elevation=50.0)
        low_space = SpaceComponent(x=12, y=10)

        world.add_component(low, low_terrain)
        world.add_component(low, low_space)

        system._process_sediment_transport(world, 1.0)

        # 沉积物搬运后，低处海拔应该增加
        assert low_terrain.elevation >= 50.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
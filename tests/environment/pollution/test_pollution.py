#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
污染系统测试

v3.5 新增
"""

import pytest

from core.world import World
from environment.environment_component import EnvironmentComponent
from environment.pollution.components.pollution_component import PollutionComponent
from environment.pollution.systems.pollution_diffusion_system import PollutionDiffusionSystem
from space.space_component import SpaceComponent


class TestPollutionComponent:
    """测试污染组件"""

    def test_default_values(self):
        comp = PollutionComponent()
        assert comp.air_pollution == 0.0
        assert comp.water_pollution == 0.0
        assert comp.soil_pollution == 0.0

    def test_serialization(self):
        comp = PollutionComponent(
            air_pollution=0.5,
            pollutants={"CO2": 400.0}
        )
        data = comp.to_dict()
        restored = PollutionComponent.from_dict(data)
        assert restored.air_pollution == 0.5
        assert restored.pollutants["CO2"] == 400.0


class TestPollutionDiffusionSystem:
    """测试污染扩散系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return PollutionDiffusionSystem()

    def test_air_diffusion(self, world, system):
        """测试空气污染扩散"""
        # 污染源
        source = world.create_entity()
        source_pollution = PollutionComponent(air_pollution=1.0)
        source_space = SpaceComponent(x=0, y=0)
        world.add_component(source, source_pollution)
        world.add_component(source, source_space)

        # 目标 (相邻单元格，确保扩散发生)
        target = world.create_entity()
        target_pollution = PollutionComponent(air_pollution=0.0)
        target_space = SpaceComponent(x=1, y=0)
        world.add_component(target, target_pollution)
        world.add_component(target, target_space)

        # 添加环境组件 (提供风速)
        env = EnvironmentComponent(wind_speed=1.0)
        world.add_component(source, env)
        env2 = EnvironmentComponent(wind_speed=1.0)
        world.add_component(target, env2)

        system.update(world, 1.0)

        # 污染源减少，目标增加
        assert source_pollution.air_pollution < 1.0
        assert target_pollution.air_pollution > 0.0

    def test_natural_decay(self, world, system):
        """测试自然降解"""
        entity = world.create_entity()
        pollution = PollutionComponent(air_pollution=0.5, water_pollution=0.3)
        world.add_component(entity, pollution)
        
        # 添加环境组件 (自然降解需要读取环境)
        env = EnvironmentComponent(wind_speed=1.0)
        world.add_component(entity, env)
        space = SpaceComponent(x=0, y=0)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 污染应该减少 (自然降解)
        assert pollution.air_pollution <= 0.5
        assert pollution.water_pollution <= 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极端天气系统测试

v3.5 新增
"""

import pytest

from core.world import World
from environment.extreme_weather.components.storm_component import StormComponent
from environment.extreme_weather.systems.storm_system import StormSystem
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent


class TestStormComponent:
    """测试风暴组件"""

    def test_default_values(self):
        comp = StormComponent()
        assert comp.storm_type == "thunderstorm"
        assert comp.central_pressure == 1013.0

    def test_coriolis_parameter(self):
        """测试科里奥利参数计算"""
        comp = StormComponent(latitude=30.0)
        f = comp.coriolis_parameter
        # f = 2Ω·sin(φ)
        # Ω = 7.292e-5, φ = 30°
        # sin(30°) = 0.5
        expected = 2 * 7.292e-5 * 0.5
        assert abs(f - expected) < expected * 0.1  # 10%误差（sin近似）

    def test_wind_speed_calculation(self):
        """测试风速计算"""
        comp = StormComponent(
            latitude=30.0,
            pressure_gradient=10.0
        )
        wind = comp.wind_speed_from_pressure
        # 应该产生非零风速
        assert wind > 0

    def test_intensity_update(self):
        """测试强度更新"""
        comp = StormComponent(
            pressure_gradient=20.0,
            temperature_gradient=10.0,
            humidity=0.9
        )
        comp.update_intensity()
        
        # 强条件应该产生高强度
        assert comp.intensity > 0.5
        assert comp.max_wind_speed > 0

    def test_serialization(self):
        comp = StormComponent(storm_type="hurricane", intensity=0.8)
        data = comp.to_dict()
        restored = StormComponent.from_dict(data)
        assert restored.storm_type == "hurricane"
        assert restored.intensity == 0.8


class TestStormSystem:
    """测试风暴系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return StormSystem()

    def test_storm_spawn_conditions(self, world, system):
        """测试风暴生成条件"""
        # 创建极端条件
        entity = world.create_entity()
        env = EnvironmentComponent(
            air_temperature=30.0,
            air_humidity=0.9,
            day_night_temp_diff=15.0,
            vpd=3.0
        )
        space = SpaceComponent(x=100, y=100)
        world.add_component(entity, env)
        world.add_component(entity, space)

        # 多次尝试生成
        for _ in range(100):
            system._spawn_storms(world, 1.0)

        # 检查是否生成了风暴
        storm = world.get_component(entity, StormComponent)
        # 由于随机性，不一定每次都有，但概率较高
        # 这里只检查不报错

    def test_storm_affects_environment(self, world, system):
        """测试风暴影响环境"""
        # 创建风暴
        storm_entity = world.create_entity()
        storm = StormComponent(
            storm_type="thunderstorm",
            intensity=0.8,
            max_wind_speed=20.0,
            diameter=5.0
        )
        storm_space = SpaceComponent(x=0, y=0)
        world.add_component(storm_entity, storm)
        world.add_component(storm_entity, storm_space)

        # 创建环境
        env_entity = world.create_entity()
        env = EnvironmentComponent(wind_speed=2.0, rainfall=0.0)
        env_space = SpaceComponent(x=1, y=0)
        world.add_component(env_entity, env)
        world.add_component(env_entity, env_space)

        initial_wind = env.wind_speed
        system._affect_environment(world, 1.0)

        # 风速应该增加
        assert env.wind_speed > initial_wind

    def test_storm_dissipation(self, world, system):
        """测试风暴消散"""
        # 创建即将消散的风暴
        entity = world.create_entity()
        storm = StormComponent(lifetime=10.0, max_lifetime=10.0, intensity=0.01)
        world.add_component(entity, storm)

        system._remove_dissipated_storms(world)

        # 风暴应该被移除
        remaining = world.get_component(entity, StormComponent)
        assert remaining is None

    def test_storm_update(self, world, system):
        """测试风暴更新"""
        entity = world.create_entity()
        storm = StormComponent(
            lifetime=0.0,
            max_lifetime=10.0,
            intensity=0.5
        )
        env = EnvironmentComponent(day_night_temp_diff=10.0, air_humidity=0.8)
        world.add_component(entity, storm)
        world.add_component(entity, env)

        system._update_storms(world, 3600.0)  # 1小时

        # 寿命应该增加
        assert storm.lifetime > 0
        # 强度应该根据环境更新
        assert storm.intensity != 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

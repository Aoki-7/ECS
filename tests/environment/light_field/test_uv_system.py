#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紫外线系统测试

v3.6 新增
"""

import pytest

from core.world import World
from environment.light_field.components.light_field_component import LightFieldComponent
from environment.light_field.systems.uv_system import UVSystem
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


class TestUVSystem:
    """测试紫外线系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return UVSystem()

    def test_base_uv_calculation(self, world, system):
        """测试基础 UV 计算"""
        entity = world.create_entity()
        light = LightFieldComponent(sun_elevation=45.0)
        
        world.add_component(entity, light)
        
        system._calculate_base_uv(light)
        
        # 正午应该有 UV
        assert light.uva > 0
        assert light.uvb > 0
        assert light.uvc > 0
        # UV-A > UV-B > UV-C
        assert light.uva > light.uvb
        assert light.uvb > light.uvc

    def test_night_no_uv(self, world, system):
        """测试夜间无 UV"""
        entity = world.create_entity()
        light = LightFieldComponent(sun_elevation=-10.0)
        
        world.add_component(entity, light)
        
        system._calculate_base_uv(light)
        
        # 夜间 UV 应该为 0
        assert light.uva == 0.0
        assert light.uvb == 0.0
        assert light.uvc == 0.0

    def test_ozone_absorption(self, world, system):
        """测试臭氧吸收"""
        entity = world.create_entity()
        light = LightFieldComponent(uva=20.0, uvb=2.0, uvc=0.1)
        atmos = AtmosphereComponent(o3_ppm=0.1)
        
        world.add_component(entity, light)
        world.add_component(entity, atmos)
        
        initial_uvb = light.uvb
        system._apply_ozone_absorption(light, atmos)
        
        # UV-B 应该被大量吸收
        assert light.uvb < initial_uvb
        # UV-C 应该几乎为 0
        assert light.uvc < 0.01

    def test_altitude_correction(self, world, system):
        """测试海拔修正"""
        entity = world.create_entity()
        light = LightFieldComponent(uva=20.0, uvb=2.0)
        atmos = AtmosphereComponent(altitude=3000.0)
        
        world.add_component(entity, light)
        world.add_component(entity, atmos)
        
        initial_uva = light.uva
        system._apply_altitude_correction(light, atmos)
        
        # 高海拔 UV 应该增强
        assert light.uva > initial_uva

    def test_uv_index_calculation(self, world, system):
        """测试 UV 指数计算"""
        entity = world.create_entity()
        light = LightFieldComponent(uva=20.0, uvb=2.0)
        
        world.add_component(entity, light)
        
        system._calculate_uv_index(light)
        
        # UV 指数应该为正
        assert light.uv_index > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
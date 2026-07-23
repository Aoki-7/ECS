#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天文系统测试

v3.5 新增
"""

import pytest

from core.world import World
from environment.astronomy.components.celestial_body_component import CelestialBodyComponent
from environment.astronomy.systems.tidal_system import TidalSystem
from environment.ocean.components.tide_component import TideComponent
from space.space_component import SpaceComponent


class TestCelestialBodyComponent:
    """测试天体组件"""

    def test_default_values(self):
        comp = CelestialBodyComponent()
        assert comp.body_name == "moon"
        assert comp.mass == 7.342e22
        assert comp.orbital_period == 27.32

    def test_tidal_force_calculation(self):
        """测试潮汐力计算（物理公式）"""
        comp = CelestialBodyComponent(mass=7.342e22, distance=3.844e8)
        force = TidalSystem.tidal_force(comp)
        # F_tidal = M / d³
        expected = 7.342e22 / (3.844e8 ** 3)
        assert abs(force - expected) < expected * 0.01  # 1%误差

    def test_orbital_distance_variation(self):
        """测试轨道距离随相位变化"""
        comp = CelestialBodyComponent(
            distance=3.844e8,
            orbital_eccentricity=0.0549,
            current_phase=0.0
        )
        
        # 近地点（phase=0）
        periapsis = TidalSystem.current_distance(comp)
        
        # 远地点（phase=π）
        comp.current_phase = 3.14159
        apoapsis = TidalSystem.current_distance(comp)
        
        # 近地点应该更近
        assert periapsis < apoapsis

    def test_phase_advancement(self):
        """测试相位推进"""
        comp = CelestialBodyComponent(phase_rate=0.229)
        initial_phase = comp.current_phase
        
        TidalSystem.advance_phase(comp, 1.0)  # 推进1天
        
        assert comp.current_phase > initial_phase

    def test_serialization(self):
        comp = CelestialBodyComponent(body_name="sun", mass=1.989e30)
        data = comp.to_dict()
        restored = CelestialBodyComponent.from_dict(data)
        assert restored.body_name == "sun"
        assert restored.mass == 1.989e30


class TestTidalSystem:
    """测试潮汐系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return TidalSystem()

    def test_orbit_advancement(self, world, system):
        """测试轨道推进"""
        body = world.create_entity()
        celestial = CelestialBodyComponent(phase_rate=0.229)
        space = SpaceComponent(x=0, y=0)
        
        world.add_component(body, celestial)
        world.add_component(body, space)
        
        initial_phase = celestial.current_phase
        system._advance_orbits(world, 86400.0)  # 推进1天（秒）
        
        assert celestial.current_phase != initial_phase

    def test_tide_level_changes(self, world, system):
        """测试潮汐水位变化"""
        # 月球
        moon = world.create_entity()
        celestial = CelestialBodyComponent(phase_rate=0.0, current_phase=0.0)
        moon_space = SpaceComponent(x=0, y=0)
        world.add_component(moon, celestial)
        world.add_component(moon, moon_space)
        
        # 潮汐点
        tide_entity = world.create_entity()
        tide = TideComponent(current_level=0.0, high_tide_level=2.0, low_tide_level=-2.0)
        tide_space = SpaceComponent(x=10, y=0)  # 在月球正方向
        world.add_component(tide_entity, tide)
        world.add_component(tide_entity, tide_space)
        
        initial_level = tide.current_level
        system._update_tides(world, 1.0)
        
        # 水位应该变化（物理驱动）
        assert tide.current_level != initial_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
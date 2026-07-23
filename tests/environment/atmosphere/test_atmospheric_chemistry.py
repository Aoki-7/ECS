#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大气化学系统测试

v3.6 新增
"""

import pytest

from core.world import World
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.atmosphere.systems.atmospheric_chemistry_system import AtmosphericChemistrySystem
from environment.pollution.components.pollution_component import PollutionComponent


class TestAtmosphericChemistrySystem:
    """测试大气化学系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return AtmosphericChemistrySystem()

    def test_ozone_formation(self, world, system):
        """测试臭氧生成（光化学反应）"""
        entity = world.create_entity()
        atmos = AtmosphereComponent(no2_ppm=0.1, temperature=30.0)
        pollution = PollutionComponent()
        
        world.add_component(entity, atmos)
        world.add_component(entity, pollution)
        
        initial_o3 = atmos.o3_ppm
        system._photochemical_reactions(atmos, 1.0)
        
        # O3 应该增加
        assert atmos.o3_ppm > initial_o3
        # NO2 应该减少
        assert atmos.no2_ppm < 0.1

    def test_co_oxidation(self, world, system):
        """测试CO氧化"""
        entity = world.create_entity()
        atmos = AtmosphereComponent(co_ppm=10.0, co2_ratio=0.0004)
        
        world.add_component(entity, atmos)
        
        initial_co = atmos.co_ppm
        system._oxidation_reactions(atmos, 1.0)
        
        # CO 应该减少
        assert atmos.co_ppm < initial_co
        # CO2 应该增加
        assert atmos.co2_ratio > 0.0004

    def test_pm_formation(self, world, system):
        """测试PM2.5形成"""
        entity = world.create_entity()
        atmos = AtmosphereComponent(so2_ppm=0.5, no2_ppm=0.3, pm25=0.0)
        pollution = PollutionComponent()
        
        world.add_component(entity, atmos)
        world.add_component(entity, pollution)
        
        system._particulate_dynamics(atmos, pollution, 1.0)
        
        # PM2.5 应该增加
        assert atmos.pm25 > 0.0
        # PM10 应该大于 PM2.5
        assert atmos.pm10 > atmos.pm25

    def test_pollution_sync(self, world, system):
        """测试与污染系统同步"""
        entity = world.create_entity()
        atmos = AtmosphereComponent(pm25=100.0, o3_ppm=0.1)
        pollution = PollutionComponent(air_pollution=0.0)
        
        world.add_component(entity, atmos)
        world.add_component(entity, pollution)
        
        system._sync_with_pollution(atmos, pollution)
        
        # 空气污染度应该更新
        assert pollution.air_pollution > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
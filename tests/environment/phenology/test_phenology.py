#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物候系统测试

v3.6 新增
"""

import pytest

from core.world import World
from environment.phenology.components.phenology_component import PhenologyComponent
from environment.phenology.systems.phenology_system import PhenologySystem
from environment.environment_component import EnvironmentComponent


class TestPhenologyComponent:
    """测试物候组件"""

    def test_default_values(self):
        comp = PhenologyComponent()
        assert comp.phenophase == "dormant"
        assert comp.gdd_base == 5.0
        assert comp.chill_requirement == 1000.0

    def test_gdd_calculation(self):
        """测试积温计算"""
        comp = PhenologyComponent(gdd_base=5.0)
        
        # 温度高于基准
        gdd = PhenologySystem.calculate_gdd(comp, 15.0)
        assert gdd == 10.0  # 15 - 5 = 10
        
        # 温度低于基准
        gdd = PhenologySystem.calculate_gdd(comp, 3.0)
        assert gdd == 0.0

    def test_chill_accumulation(self):
        """测试需冷量累积"""
        comp = PhenologyComponent()
        
        # 低温累积
        chill = PhenologySystem.accumulate_chill(comp, 5.0, 1.0)
        assert chill == 1.0
        
        # 高温不累积
        chill = PhenologySystem.accumulate_chill(comp, 10.0, 1.0)
        assert chill == 0.0

    def test_transition_check(self):
        """测试物候转换检查"""
        comp = PhenologyComponent(gdd_accumulated=200.0)
        
        # 满足 leafing 条件（需要 150）
        assert PhenologySystem.check_transition(comp, "leafing") == True
        
        # 不满足 flowering 条件（需要 300）
        assert PhenologySystem.check_transition(comp, "flowering") == False

    def test_serialization(self):
        comp = PhenologyComponent(
            phenophase="flowering",
            gdd_accumulated=350.0,
            chill_hours=1200.0
        )
        data = comp.to_dict()
        restored = PhenologyComponent.from_dict(data)
        assert restored.phenophase == "flowering"
        assert restored.gdd_accumulated == 350.0
        assert restored.chill_hours == 1200.0


class TestPhenologySystem:
    """测试物候系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return PhenologySystem()

    def test_thermal_accumulation(self, world, system):
        """测试热积累更新"""
        entity = world.create_entity()
        phenology = PhenologyComponent(phenophase="budding", gdd_accumulated=0.0)
        env = EnvironmentComponent(air_temperature=15.0)
        
        world.add_component(entity, phenology)
        world.add_component(entity, env)
        
        system._update_thermal_accumulation(phenology, 15.0, 24.0)
        
        # 积温应该增加
        assert phenology.gdd_accumulated > 0.0

    def test_budding_transition(self, world, system):
        """测试萌芽转换"""
        entity = world.create_entity()
        phenology = PhenologyComponent(
            phenophase="dormant",
            chill_hours=1200.0,  # 满足需冷量
            gdd_base=5.0
        )
        env = EnvironmentComponent(air_temperature=10.0)
        
        world.add_component(entity, phenology)
        world.add_component(entity, env)
        
        # 检查转换
        can_bud = system._can_bud(phenology, env, 12.0, 0.5)
        assert can_bud == True

    def test_leaf_fall_by_day_length(self, world, system):
        """测试光周期驱动的落叶"""
        entity = world.create_entity()
        phenology = PhenologyComponent(
            phenophase="senescence",
            gdd_accumulated=900.0,
            day_length_sensitivity=1.0  # 高敏感度
        )
        env = EnvironmentComponent()
        
        world.add_component(entity, phenology)
        world.add_component(entity, env)
        
        # 短日照（秋季）day_length < 12.0 * (1 - 1.0 * 0.5) = 6.0
        can_fall = system._can_leaf_fall(phenology, env, 5.0, 0.5)
        assert can_fall == True

    def test_dormant_by_temperature(self, world, system):
        """测试低温驱动的休眠"""
        entity = world.create_entity()
        phenology = PhenologyComponent(phenophase="leaf_fall")
        env = EnvironmentComponent(air_temperature=-5.0)
        
        world.add_component(entity, phenology)
        world.add_component(entity, env)
        
        can_dormant = system._can_dormant(phenology, env, 8.0, 0.5)
        assert can_dormant == True

    def test_full_lifecycle(self, world, system):
        """测试完整物候周期"""
        entity = world.create_entity()
        phenology = PhenologyComponent(
            phenophase="dormant",
            chill_hours=0.0,
            gdd_accumulated=0.0
        )
        env = EnvironmentComponent(air_temperature=5.0)
        
        world.add_component(entity, phenology)
        world.add_component(entity, env)
        
        # 阶段1：累积需冷量（冬季）
        env.air_temperature = 2.0
        for _ in range(100):
            system._update_thermal_accumulation(phenology, 2.0, 24.0)
        
        assert phenology.chill_hours > 0
        
        # 阶段2：升温萌芽（春季）
        env.air_temperature = 15.0
        can_bud = system._can_bud(phenology, env, 12.0, 0.5)
        assert can_bud == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

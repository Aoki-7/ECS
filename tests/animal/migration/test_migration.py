#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁徙系统测试

v3.6 新增
"""

import pytest

from core.world import World
from animal.migration.components.migration_component import MigrationComponent
from animal.migration.systems.migration_system import MigrationSystem
from environment.environment_component import EnvironmentComponent
from environment.season.season_component import SeasonComponent
from space.space_component import SpaceComponent


class TestMigrationComponent:
    """测试迁徙组件"""

    def test_default_values(self):
        comp = MigrationComponent()
        assert comp.is_migratory == False
        assert comp.migration_status == "resident"
        assert comp.energy_reserve == 1.0

    def test_spring_departure_conditions(self):
        """测试春季北迁条件"""
        comp = MigrationComponent(
            is_migratory=True,
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        
        # 满足条件
        assert comp.should_depart_spring(15.0, 14.0) == True
        
        # 温度不够
        assert comp.should_depart_spring(5.0, 14.0) == False
        
        # 光周期不够
        assert comp.should_depart_spring(15.0, 10.0) == False
        
        # 能量不够
        comp.energy_reserve = 0.1
        assert comp.should_depart_spring(15.0, 14.0) == False

    def test_autumn_departure_conditions(self):
        """测试秋季南迁条件"""
        comp = MigrationComponent(
            is_migratory=True,
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        
        # 满足条件
        assert comp.should_depart_autumn(5.0, 10.0) == True
        
        # 温度太高
        assert comp.should_depart_autumn(15.0, 10.0) == False

    def test_arrival_condition(self):
        """测试到达条件"""
        comp = MigrationComponent(temperature_threshold_arrive=15.0)
        
        assert comp.can_arrive(20.0) == True
        assert comp.can_arrive(10.0) == False

    def test_serialization(self):
        comp = MigrationComponent(
            is_migratory=True,
            breeding_ground=(100.0, 200.0),
            energy_reserve=0.8
        )
        data = comp.to_dict()
        restored = MigrationComponent.from_dict(data)
        assert restored.is_migratory == True
        assert restored.breeding_ground == (100.0, 200.0)
        assert restored.energy_reserve == 0.8


class TestMigrationSystem:
    """测试迁徙系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return MigrationSystem()

    def test_spring_migration_trigger(self, world, system):
        """测试春季迁徙触发"""
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            breeding_ground=(100.0, 100.0),
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        env = EnvironmentComponent(air_temperature=15.0, photoperiod=14.0)
        space = SpaceComponent(x=0, y=0)
        season = SeasonComponent(year_progress=100.0)  # 春季
        
        world.add_component(entity, migration)
        world.add_component(entity, env)
        world.add_component(entity, space)
        world.add_component(entity, season)
        
        system._check_departure_triggers(world, 1.0)
        
        # 应该开始迁徙
        assert migration.migration_status == "migrating"
        assert migration.current_target == (100.0, 100.0)

    def test_migration_movement(self, world, system):
        """测试迁徙移动"""
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="migrating",
            current_target=(100.0, 0.0),
            energy_reserve=1.0
        )
        space = SpaceComponent(x=0, y=0)
        
        world.add_component(entity, migration)
        world.add_component(entity, space)
        
        system._update_migrating_animals(world, 1.0)
        
        # 位置应该改变
        assert space.x > 0
        # 能量应该消耗
        assert migration.energy_reserve < 1.0

    def test_energy_depletion_stops_migration(self, world, system):
        """测试能量耗尽停止迁徙"""
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="migrating",
            current_target=(1000.0, 0.0),
            energy_reserve=0.01  # 极低能量
        )
        space = SpaceComponent(x=0, y=0)
        
        world.add_component(entity, migration)
        world.add_component(entity, space)
        
        system._update_migrating_animals(world, 10.0)
        
        # 能量耗尽应该停止
        assert migration.migration_status == "resident"

    def test_energy_recovery(self, world, system):
        """测试能量恢复"""
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="resident",
            energy_reserve=0.5
        )
        env = EnvironmentComponent(soil_moisture=0.8, air_humidity=0.8)
        
        world.add_component(entity, migration)
        world.add_component(entity, env)
        
        system._manage_energy(world, 1.0)
        
        # 能量应该恢复
        assert migration.energy_reserve > 0.5

    def test_arrival(self, world, system):
        """测试到达"""
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="arrived",
            temperature_threshold_arrive=15.0
        )
        env = EnvironmentComponent(air_temperature=20.0)
        
        world.add_component(entity, migration)
        world.add_component(entity, env)
        
        system._check_arrivals(world, 1.0)
        
        # 应该转为定居
        assert migration.migration_status == "resident"
        assert migration.current_target is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

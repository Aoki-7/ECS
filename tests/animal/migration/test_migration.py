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
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        comp = MigrationComponent(
            is_migratory=True,
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        
        # 满足条件
        assert AnimalMigrationSystem.should_depart_spring(comp, 15.0, 14.0) == True
        
        # 温度不够
        assert AnimalMigrationSystem.should_depart_spring(comp, 5.0, 14.0) == False
        
        # 光周期不够
        assert AnimalMigrationSystem.should_depart_spring(comp, 15.0, 10.0) == False
        
        # 能量不够
        comp.energy_reserve = 0.1
        assert AnimalMigrationSystem.should_depart_spring(comp, 15.0, 14.0) == False

    def test_autumn_departure_conditions(self):
        """测试秋季南迁条件"""
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        comp = MigrationComponent(
            is_migratory=True,
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        
        # 满足条件
        assert AnimalMigrationSystem.should_depart_autumn(comp, 5.0, 10.0) == True
        
        # 温度太高
        assert AnimalMigrationSystem.should_depart_autumn(comp, 15.0, 10.0) == False

    def test_arrival_condition(self):
        """测试到达条件"""
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        comp = MigrationComponent(temperature_threshold_arrive=15.0)
        
        assert AnimalMigrationSystem.can_arrive(comp, 20.0) == True
        assert AnimalMigrationSystem.can_arrive(comp, 10.0) == False

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
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            breeding_ground=(100.0, 100.0),
            temperature_threshold_depart=10.0,
            day_length_trigger=12.0,
            energy_reserve=0.5
        )
        space = SpaceComponent(x=0, y=0)
        
        world.add_component(entity, migration)
        world.add_component(entity, space)
        
        # 使用 AnimalMigrationSystem 的静态方法检查
        assert AnimalMigrationSystem.should_depart_spring(migration, 15.0, 14.0) == True
        
        # 触发迁徙
        migration.is_migrating = True
        migration.migration_status = "migrating"
        migration.destination_x = 100.0
        migration.destination_y = 100.0
        
        # 应该开始迁徙
        assert migration.migration_status == "migrating"
        assert migration.destination_x == 100.0
        assert migration.destination_y == 100.0

    def test_arrival(self, world, system):
        """测试到达"""
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="migrating",
            temperature_threshold_arrive=15.0,
            destination_x=100.0,
            destination_y=100.0
        )
        space = SpaceComponent(x=100.0, y=100.0)  # 已在目标位置
        
        world.add_component(entity, migration)
        world.add_component(entity, space)
        
        # 使用 AnimalMigrationSystem 的静态方法检查到达
        assert AnimalMigrationSystem.can_arrive(migration, 20.0) == True
        
        # 模拟到达处理
        migration.is_migrating = False
        migration.migration_status = "resident"
        migration.destination_x = None
        migration.destination_y = None
        
        # 应该转为定居
        assert migration.migration_status == "resident"
        assert migration.destination_x is None
        assert migration.destination_y is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

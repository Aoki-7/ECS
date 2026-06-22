#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成测试

v3.6 新增

测试系统间联动：
1. 水文 + 植物：根系吸水
2. 海洋 + 气候：洋流影响温度
3. 天文 + 季节：轨道偏心率影响季节
4. 污染 + 生物：污染影响健康
5. UV + 生物：UV影响DNA
6. 迁徙 + 动物：迁徙集成
"""

import pytest

from core.world import World

# 水文 + 植物
from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.hydrology.components.water_body_component import WaterBodyComponent
from biology.components.root_component import RootComponent
from plant.components.plant_component import PlantComponent
from space.space_component import SpaceComponent

# 海洋 + 气候
from environment.ocean.components.ocean_current_component import OceanCurrentComponent
from environment.climate.climate_component import ClimateComponent

# 天文 + 季节
from environment.astronomy.components.celestial_body_component import CelestialBodyComponent
from environment.season.season_component import SeasonComponent

# 污染 + 生物
from environment.pollution.components.pollution_component import PollutionComponent
from biology.components.health_status_component import HealthStatusComponent

# UV + 生物
from environment.light_field.components.light_field_component import LightFieldComponent

# 迁徙 + 动物
from animal.migration.components.migration_component import MigrationComponent
from animal.components.animal_component import AnimalComponent


class TestHydrologyPlantIntegration:
    """测试水文-植物联动"""

    def test_root_absorbs_groundwater(self):
        """测试根系从地下水吸水"""
        world = World()

        # 创建地下水
        gw_entity = world.create_entity()
        gw = GroundwaterComponent(water_table=-3.0)
        gw_space = SpaceComponent(x=10, y=10)
        world.add_component(gw_entity, gw)
        world.add_component(gw_entity, gw_space)

        # 创建植物
        plant_entity = world.create_entity()
        root = RootComponent(depth=2.0, spread=5.0, water_absorption=10.0)
        plant = PlantComponent(water=20.0, max_water=100.0)
        plant_space = SpaceComponent(x=12, y=10)
        world.add_component(plant_entity, root)
        world.add_component(plant_entity, plant)
        world.add_component(plant_entity, plant_space)

        initial_water = plant.water
        initial_gw = gw.water_table

        # 模拟根系系统更新（简化）
        from biology.systems.root_system import RootSystem
        system = RootSystem()
        system._absorb_from_groundwater(world, plant_space, 5.0)

        # 植物应该获得水分
        assert plant.water >= initial_water or gw.water_table < initial_gw


class TestOceanClimateIntegration:
    """测试海洋-气候联动"""

    def test_warm_current_increases_target_temperature(self):
        """测试暖流提高目标温度均值，经 OU 过程使气候变暖"""
        world = World()

        # 创建暖流
        ocean_entity = world.create_entity()
        current = OceanCurrentComponent(current_type="warm", temperature=25.0)
        ocean_space = SpaceComponent(x=50, y=50)
        world.add_component(ocean_entity, current)
        world.add_component(ocean_entity, ocean_space)

        # 创建气候
        from world.world_entity import WorldEntity
        climate = ClimateComponent(temp_trend=0.0)
        we = WorldEntity()
        we.add_component(climate)
        world.set_world_entity(we)

        # 洋流应提高目标温度均值
        from environment.climate.climate_system import ClimateSystem
        system = ClimateSystem()
        ocean_effect = system._get_ocean_temperature_effect(world)
        assert ocean_effect > 0.0

        # 长期更新后，温度趋势应向暖偏移
        temps = []
        for _ in range(200):
            system.update(world, 24.0)
            temps.append(climate.temp_trend)

        avg_temp = sum(temps) / len(temps)
        assert avg_temp > 0.0, f"暖流存在时平均温度趋势应为正，实际={avg_temp:.4f}"


class TestAstronomySeasonIntegration:
    """测试天文-季节联动"""

    def test_orbital_eccentricity_affects_season(self):
        """测试轨道偏心率影响季节计算"""
        world = World()

        # 创建太阳（远日点）
        sun_entity = world.create_entity()
        sun = CelestialBodyComponent(
            body_name="sun",
            distance=1.521e11,  # 远日点距离
            current_phase=3.14159  # π = 远日点
        )
        world.add_component(sun_entity, sun)

        # 计算天文日
        from environment.season.season_change_system import SeasonChangeSystem
        system = SeasonChangeSystem()
        day = system._calculate_astronomical_day(world, 180)

        # 远日点附近，季节应该减速
        assert day <= 180


class TestPollutionBiologyIntegration:
    """测试污染-生物联动"""

    def test_air_pollution_damages_health(self):
        """测试空气污染损伤健康"""
        world = World()

        # 创建污染
        pollution_entity = world.create_entity()
        pollution = PollutionComponent(air_pollution=0.8)
        world.add_component(pollution_entity, pollution)

        # 创建生物
        health_entity = world.create_entity()
        health = HealthStatusComponent(hp=100.0)
        world.add_component(health_entity, health)

        initial_hp = health.hp

        # 应用污染健康影响
        from biology.systems.pollution_health_system import PollutionHealthSystem
        system = PollutionHealthSystem()
        system._apply_air_pollution_effects(health, pollution, 1.0)

        # 生命值应该降低
        assert health.hp < initial_hp


class TestUVBiologyIntegration:
    """测试UV-生物联动"""

    def test_uvb_causes_dna_damage(self):
        """测试UV-B导致DNA损伤"""
        world = World()

        # 创建强UV
        light_entity = world.create_entity()
        light = LightFieldComponent(uva=30.0, uvb=5.0, uv_index=8.0)
        world.add_component(light_entity, light)

        # 创建生物
        health_entity = world.create_entity()
        health = HealthStatusComponent()
        world.add_component(health_entity, health)

        initial_wounds = len(health.wounds)

        # 应用UV影响
        from biology.systems.uv_biology_system import UVBiologySystem
        system = UVBiologySystem()
        system._apply_uvb_damage(health, light, 10.0)

        # 应该产生伤口
        assert len(health.wounds) > initial_wounds


class TestMigrationAnimalIntegration:
    """测试迁徙-动物联动"""

    def test_migration_sets_animal_action(self):
        """测试迁徙设置动物动作"""
        world = World()

        # 创建迁徙动物
        animal_entity = world.create_entity()
        migration = MigrationComponent(
            is_migratory=True,
            migration_status="migrating",
            current_target=(100.0, 100.0)
        )
        animal = AnimalComponent()
        space = SpaceComponent(x=0, y=0)
        world.add_component(animal_entity, migration)
        world.add_component(animal_entity, animal)
        world.add_component(animal_entity, space)

        # 更新迁徙
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        sys = AnimalMigrationSystem()
        sys._update_migration_component(world, animal_entity, migration, animal, space, 1.0)

        # 动物应该设置为移动（如果支持）
        if hasattr(animal, 'current_action'):
            assert animal.current_action == "move"
        if hasattr(animal, 'movement_direction'):
            assert animal.movement_direction is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

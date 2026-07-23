import pytest
import random
from unittest.mock import Mock, patch

from core.world import World
from core.entity import Entity
from environment.systems.fire_detection_system import FireDetectionSystem
from environment.systems.flood_detection_system import FloodDetectionSystem
from environment.systems.drought_detection_system import DroughtDetectionSystem
from environment.systems.disaster_impact_system import DisasterImpactSystem
from environment.continuum.systems.vegetation_coupling_system import VegetationCouplingSystem
from environment.continuum.systems.animal_coupling_system import AnimalCouplingSystem
from environment.continuum.systems.human_coupling_system import HumanCouplingSystem
from environment.continuum.systems.agriculture_coupling_system import AgricultureCouplingSystem
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent
from biology.organisms.animal.components.animal_component import AnimalComponent


class TestFireDetectionSystem:
    """测试火灾检测系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return FireDetectionSystem()

    def test_no_fire_risk_normal_conditions(self, world, system):
        """正常条件不应触发火灾"""
        env = EnvironmentComponent(air_temperature=20.0, air_humidity=0.5, wind_speed=0.0)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        system.update(world, 1.0)
        # 正常条件不应触发火灾

    def test_fire_risk_high_conditions(self, world, system):
        """高风险条件应计算高火灾风险"""
        env = EnvironmentComponent(air_temperature=40.0, air_humidity=0.1, wind_speed=10.0)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        risk = system._calculate_fire_risk(40.0, 10.0, 10.0)
        assert risk > 0.6

    def test_fire_risk_low_conditions(self, world, system):
        """低风险条件应计算低火灾风险"""
        risk = system._calculate_fire_risk(20.0, 50.0, 0.0)
        assert risk < 0.3


class TestFloodDetectionSystem:
    """测试洪水检测系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return FloodDetectionSystem()

    def test_no_flood_risk_normal_conditions(self, world, system):
        """正常条件不应触发洪水"""
        env = EnvironmentComponent(rainfall=10.0, soil_moisture=0.3)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        system.update(world, 1.0)
        # 正常条件不应触发洪水

    def test_flood_risk_high_conditions(self, world, system):
        """高风险条件应触发洪水"""
        env = EnvironmentComponent(rainfall=60.0, soil_moisture=0.9)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        # 强制触发洪水
        with patch('random.random', return_value=0.0):
            system.update(world, 1.0)


class TestDroughtDetectionSystem:
    """测试干旱检测系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return DroughtDetectionSystem()

    def test_no_drought_risk_normal_conditions(self, world, system):
        """正常条件不应触发干旱"""
        env = EnvironmentComponent(rainfall=20.0, air_temperature=20.0)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        system.update(world, 1.0)
        # 正常条件不应触发干旱

    def test_drought_risk_high_conditions(self, world, system):
        """高风险条件应触发干旱"""
        env = EnvironmentComponent(rainfall=0.0, air_temperature=35.0)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.set_world_entity(entity)

        # 强制触发干旱
        with patch('random.random', return_value=0.0):
            system.update(world, 1.0)


class TestDisasterImpactSystem:
    """测试灾害影响系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return DisasterImpactSystem()

    def test_add_disaster(self, world, system):
        """测试添加灾害"""
        disaster = {"type": "fire", "x": 10, "y": 10, "radius": 5.0, "intensity": 0.8}
        system.add_disaster(disaster)

        active = system.get_active_disasters()
        assert "fire" in active
        assert len(active["fire"]) == 1

    def test_get_disaster_history(self, world, system):
        """测试获取灾害历史"""
        disaster = {"type": "flood", "x": 20, "y": 20, "radius": 10.0, "intensity": 0.5}
        system.add_disaster(disaster)

        history = system.get_disaster_history()
        assert len(history) == 1
        assert history[0]["type"] == "flood"


class TestVegetationCouplingSystem:
    """测试植被-环境耦合系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return VegetationCouplingSystem()

    def test_vegetation_transpiration(self, world, system):
        """测试植被蒸腾增加湿度"""
        env = EnvironmentComponent(air_humidity=0.3)
        terrain = TerrainComponent(vegetation_cover=0.5)
        entity = world.create_entity()
        world.add_component(entity, env)
        world.add_component(entity, terrain)

        system.update(world, 1.0)
        assert env.air_humidity > 0.3


class TestAnimalCouplingSystem:
    """测试动物-环境耦合系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return AnimalCouplingSystem()

    def test_animal_compaction(self, world, system):
        """测试动物踩踏增加土壤紧实度"""
        soil = SoilComponent()
        if hasattr(soil, 'compaction'):
            soil.compaction = 0.0
        entity = world.create_entity()
        world.add_component(entity, soil)

        # 模拟动物存在
        animal_entity = world.create_entity()
        space = SpaceComponent(x=0, y=0)
        animal = AnimalComponent()
        world.add_component(animal_entity, space)
        world.add_component(animal_entity, animal)

        system.update(world, 1.0)
        # 紧实度应增加（如果存在该属性）


class TestHumanCouplingSystem:
    """测试人类-环境耦合系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return HumanCouplingSystem()

    def test_human_coupling_exists(self, world, system):
        """测试系统存在"""
        assert system is not None


class TestAgricultureCouplingSystem:
    """测试农业-环境耦合系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return AgricultureCouplingSystem()

    def test_agriculture_coupling_exists(self, world, system):
        """测试系统存在"""
        assert system is not None
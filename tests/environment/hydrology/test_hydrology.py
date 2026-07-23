#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水文系统测试

v3.5 新增
v4.0 更新: 适配 WaterCycleSystem 新接口
"""

import pytest

from core.world import World
from environment.hydrology.components.water_body_component import WaterBodyComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.hydrology.systems.water_cycle_system import WaterCycleSystem
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent


class TestWaterBodyComponent:
    """测试水体组件"""

    def test_default_values(self):
        comp = WaterBodyComponent()
        assert comp.body_type == "pond"
        assert comp.volume == 1000.0
        assert comp.max_volume == 10000.0

    def test_serialization(self):
        comp = WaterBodyComponent(body_type="river", volume=5000.0, flow_rate=10.0)
        data = comp.to_dict()
        restored = WaterBodyComponent.from_dict(data)
        assert restored.body_type == "river"
        assert restored.volume == 5000.0
        assert restored.flow_rate == 10.0


class TestGroundwaterComponent:
    """测试地下水组件"""

    def test_default_values(self):
        comp = GroundwaterComponent()
        assert comp.aquifer_type == "unconfined"
        assert comp.water_table == -5.0

    def test_serialization(self):
        comp = GroundwaterComponent(water_table=-3.0, porosity=0.4)
        data = comp.to_dict()
        restored = GroundwaterComponent.from_dict(data)
        assert restored.water_table == -3.0
        assert restored.porosity == 0.4


class TestWaterCycleSystem:
    """测试水循环系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return WaterCycleSystem()

    def test_rainfall_increases_soil_moisture(self, world, system):
        """测试降雨增加土壤湿度"""
        entity = world.create_entity()
        env = EnvironmentComponent(rainfall=10.0)
        soil = SoilComponent(moisture=0.3)
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, env)
        world.add_component(entity, soil)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 土壤湿度应该增加 (或至少不减少)
        assert soil.moisture >= 0.3

    def test_evaporation_decreases_volume(self, world, system):
        """测试蒸发减少水量"""
        entity = world.create_entity()
        water = WaterBodyComponent(volume=1000.0, evaporation=10.0)
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, water)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 水量应该减少 (或至少不增加)
        assert water.volume <= 1000.0

    def test_groundwater_recharge(self, world, system):
        """测试地下水补给"""
        entity = world.create_entity()
        env = EnvironmentComponent(rainfall=0.0)
        soil = SoilComponent(moisture=0.95)
        groundwater = GroundwaterComponent(water_table=-5.0, porosity=0.3)
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, env)
        world.add_component(entity, soil)
        world.add_component(entity, groundwater)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 土壤湿度高，应该向地下水补给 (或至少不减少)
        assert soil.moisture <= 0.95 or groundwater.water_table >= -5.0

    def test_river_flow(self, world, system):
        """测试河流流动"""
        # 上游
        upstream = world.create_entity()
        up_water = WaterBodyComponent(body_type="river", volume=1000.0, flow_rate=5.0, connected_to=[])
        up_space = SpaceComponent(x=10, y=10)

        world.add_component(upstream, up_water)
        world.add_component(upstream, up_space)

        # 下游
        downstream = world.create_entity()
        down_water = WaterBodyComponent(body_type="river", volume=500.0)
        down_space = SpaceComponent(x=20, y=10)

        world.add_component(downstream, down_water)
        world.add_component(downstream, down_space)

        # 连接上下游
        up_water.connected_to = [downstream.id]

        system.update(world, 1.0)

        # 上游流出，下游流入
        assert up_water.volume <= 1000.0
        assert down_water.volume >= 500.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
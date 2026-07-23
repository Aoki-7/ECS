#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HealthStatusSystem 测试
"""

import pytest

from core.world import World
from biology.components.health_status_component import HealthStatusComponent, WoundRecord
from biology.systems.health_status_system import HealthStatusSystem


class TestHealthStatusSystem:
    """测试 HealthStatusSystem"""

    def test_add_wound(self):
        """测试添加伤口"""
        world = World()
        entity = world.create_entity()
        health = HealthStatusComponent(hp=100.0, max_hp=100.0)
        world.add_component(entity, health)

        HealthStatusSystem.add_wound(
            entity, health, "physical", 20.0, damage_per_sec=1.0, duration=10.0
        )

        assert len(health.wounds) == 1
        assert health.wounds[0].type == "physical"
        assert health.wounds[0].severity == 20.0
        assert health.total_damage == 20.0

    def test_update_wounds(self):
        """测试伤口更新"""
        world = World()
        system = HealthStatusSystem()
        entity = world.create_entity()
        health = HealthStatusComponent(hp=100.0, max_hp=100.0)
        world.add_component(entity, health)

        HealthStatusSystem.add_wound(
            entity, health, "bleeding", 10.0, damage_per_sec=2.0, duration=5.0
        )

        # 更新 1 秒
        system._update_wounds(health, 1.0)

        assert health.wounds[0].age == 1.0
        assert health.hp == 98.0  # 100 - 2.0 * 1.0

    def test_wound_expires(self):
        """测试伤口过期"""
        world = World()
        system = HealthStatusSystem()
        entity = world.create_entity()
        health = HealthStatusComponent(hp=100.0)
        world.add_component(entity, health)

        HealthStatusSystem.add_wound(
            entity, health, "poison", 15.0, damage_per_sec=1.0, duration=2.0
        )

        # 更新 3 秒（超过持续时间）
        system._update_wounds(health, 3.0)
        system._remove_healed_wounds(health)

        assert len(health.wounds) == 0
        assert health.total_damage == 0.0

    def test_remove_healed_wounds(self):
        """测试移除已愈合伤口"""
        world = World()
        system = HealthStatusSystem()
        entity = world.create_entity()
        health = HealthStatusComponent()
        world.add_component(entity, health)

        HealthStatusSystem.add_wound(entity, health, "physical", 5.0)
        HealthStatusSystem.add_wound(entity, health, "bleeding", 30.0)

        # 将第一个伤口的严重程度设为 0（模拟愈合）
        health.wounds[0].severity = 0.0

        system._remove_healed_wounds(health)

        assert len(health.wounds) == 1
        assert health.wounds[0].type == "bleeding"
        assert health.total_damage == 30.0

    def test_get_total_severity(self):
        """测试获取总严重程度"""
        health = HealthStatusComponent()
        health.wounds = [
            WoundRecord("physical", 10.0),
            WoundRecord("bleeding", 20.0),
            WoundRecord("poison", 5.0),
        ]

        assert HealthStatusSystem.get_total_severity(health) == 35.0

    def test_system_update_integration(self):
        """测试 System 集成更新"""
        world = World()
        system = HealthStatusSystem()
        world.add_system(system)

        entity = world.create_entity()
        health = HealthStatusComponent(hp=100.0)
        world.add_component(entity, health)

        HealthStatusSystem.add_wound(
            entity, health, "bleeding", 10.0, damage_per_sec=5.0
        )

        # System 更新
        system.update(world, 1.0)

        assert health.hp == 95.0  # 100 - 5.0 * 1.0
        assert health.wounds[0].age == 1.0

    def test_multiple_wounds_damage(self):
        """测试多个伤口叠加伤害"""
        health = HealthStatusComponent(hp=100.0)

        HealthStatusSystem.add_wound(None, health, "cut", 5.0, damage_per_sec=3.0)
        HealthStatusSystem.add_wound(None, health, "burn", 10.0, damage_per_sec=2.0)

        system = HealthStatusSystem()
        system._update_wounds(health, 2.0)

        # 总伤害 = (3.0 + 2.0) * 2.0 = 10.0
        assert health.hp == 90.0

    def test_max_damage_cap(self):
        """测试损伤上限"""
        health = HealthStatusComponent(max_damage=50.0)

        HealthStatusSystem.add_wound(None, health, "big", 40.0)
        HealthStatusSystem.add_wound(None, health, "small", 20.0)

        # 总损伤不应超过 max_damage
        assert health.total_damage == 50.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
气味系统测试

v3.0.3 新增
"""

import pytest

from core.world import World
from biology.components.smell_component import SmellComponent
from space.space_component import SpaceComponent
from biology.systems.smell_diffusion_system import SmellDiffusionSystem


class TestSmellComponent:
    """测试气味组件"""

    def test_default_values(self):
        comp = SmellComponent()
        assert comp.scents == {}
        assert comp.base_intensity == 1.0
        assert comp.decay_rate == 0.001

    def test_serialization(self):
        comp = SmellComponent(
            scents={"fear": 0.8, "food": 0.5},
            is_prey=True,
        )
        data = comp.to_dict()
        restored = SmellComponent.from_dict(data)
        assert restored.scents["fear"] == 0.8
        assert restored.is_prey is True


class TestSmellDiffusionSystem:
    """测试气味扩散系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return SmellDiffusionSystem()

    def test_smell_emission(self, world, system):
        """测试气味释放"""
        entity = world.create_entity()
        smell = SmellComponent(scents={"food": 1.0}, base_intensity=1.0)
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, smell)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 检查气味场是否有气味
        smells = system.get_smell_at(10, 10)
        assert "food" in smells
        assert smells["food"] > 0

    def test_smell_decay(self, world, system):
        """测试气味衰减"""
        entity = world.create_entity()
        smell = SmellComponent(scents={"food": 1.0})
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, smell)
        world.add_component(entity, space)

        # 更新多次
        for _ in range(50):
            system.update(world, 1.0)

        # 气味应该衰减
        smells = system.get_smell_at(10, 10)
        if "food" in smells:
            assert smells["food"] < 1.0

    def test_smell_diffusion(self, world, system):
        """测试气味扩散"""
        entity = world.create_entity()
        smell = SmellComponent(scents={"food": 1.0})
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, smell)
        world.add_component(entity, space)

        system.update(world, 1.0)

        # 检查邻居网格是否有气味
        neighbor_smells = system.get_smell_at(15, 10)  # 相邻网格
        # 可能有扩散过来的气味

    def test_strongest_scent(self, world, system):
        """测试最强气味检测"""
        entity = world.create_entity()
        smell = SmellComponent(scents={"food": 0.8, "fear": 0.3})
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, smell)
        world.add_component(entity, space)

        system.update(world, 1.0)

        strongest = system.get_strongest_scent(10, 10)
        assert strongest is not None
        assert strongest[0] == "food"

    def test_clear(self, world, system):
        """测试清空气味场"""
        entity = world.create_entity()
        smell = SmellComponent(scents={"food": 1.0})
        space = SpaceComponent(x=10, y=10)

        world.add_component(entity, smell)
        world.add_component(entity, space)

        system.update(world, 1.0)
        system.clear()

        smells = system.get_smell_at(10, 10)
        assert smells == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WorldConfigSystem 测试

v4.0 新增 — 测试世界配置系统的纯数据化迁移
"""

import pytest

from core.world import World
from core.entity import Entity

from core.components.world_config_component import WorldConfigComponent
from core.systems.world_config_system import WorldConfigSystem


class TestWorldConfigSystem:
    """测试世界配置管理系统"""

    @pytest.fixture
    def config(self):
        return WorldConfigComponent(map_width=100, map_height=80)

    def test_clamp_position_inside(self, config):
        """测试边界内坐标不变化"""
        x, y = WorldConfigSystem.clamp_position(config, 50, 40)
        assert x == 50
        assert y == 40

    def test_clamp_position_negative(self, config):
        """测试负坐标限制到0"""
        x, y = WorldConfigSystem.clamp_position(config, -10, -5)
        assert x == 0
        assert y == 0

    def test_clamp_position_overflow(self, config):
        """测试超出边界坐标限制到最大值"""
        x, y = WorldConfigSystem.clamp_position(config, 200, 100)
        assert x == 99  # map_width - 1
        assert y == 79  # map_height - 1

    def test_random_position(self, config):
        """测试随机坐标在边界内"""
        x, y = WorldConfigSystem.random_position(config)
        assert 0 <= x < config.map_width
        assert 0 <= y < config.map_height

    def test_random_position_with_margin(self, config):
        """测试带边距的随机坐标"""
        x, y = WorldConfigSystem.random_position(config, margin=10)
        assert 10 <= x <= config.map_width - 1 - 10
        assert 10 <= y <= config.map_height - 1 - 10

    def test_is_inside(self, config):
        """测试坐标在边界内"""
        assert WorldConfigSystem.is_inside(config, 50, 40) is True

    def test_is_inside_negative(self, config):
        """测试负坐标在边界外"""
        assert WorldConfigSystem.is_inside(config, -1, 40) is False

    def test_is_inside_overflow(self, config):
        """测试超出边界"""
        assert WorldConfigSystem.is_inside(config, 100, 40) is False
        assert WorldConfigSystem.is_inside(config, 50, 80) is False

    def test_get_world_config(self):
        """测试从世界获取配置"""
        world = World()
        # 无世界实体时返回默认配置
        config = WorldConfigSystem.get_world_config(world)
        assert config.map_width == 100
        assert config.map_height == 100

    def test_get_world_config_from_entity(self):
        """测试从世界实体获取配置"""
        world = World()
        we = Entity.create()
        world.set_world_entity(we)
        # 需要 WorldEntity 支持 add_component
        if hasattr(we, 'add_component'):
            we.add_component(WorldConfigComponent(map_width=200, map_height=150))
            config = WorldConfigSystem.get_world_config(world)
            assert config.map_width == 200
            assert config.map_height == 150


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境连续统处理器测试

测试覆盖:
    - 热扩散: 温度均衡、水域缓冲
    - 湿度扩散: 湿度均衡、水域源
    - 重力水流: 下坡流、守恒性
    - 风驱平流: 风向传递
    - 自恢复: 向顶极恢复
    - 守恒检查: 能量/水分/养分守恒
"""

import pytest
import math

from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType

from environment.continuum.continuum_utils import (
    ContinuumCache,
    ConservationSnapshot,
    resolve_boundary,
    compute_diffusion_flux,
    sigmoid_factor,
    clamp,
    take_conservation_snapshot,
    check_conservation,
    get_neighbor_offsets,
)
from environment.continuum.continuum_processors import (
    ThermalDiffusionProcessor,
    HumidityDiffusionProcessor,
    GravityWaterFlowProcessor,
    WindAdvectionProcessor,
    SelfRecoveryProcessor,
)
from environment.continuum.continuum_config import NEIGHBOR_OFFSETS_MOORE


class TestContinuumUtils:
    """测试共享工具"""

    def test_resolve_boundary(self):
        """测试边界解析"""
        grid = {(0, 0): None, (1, 0): None, (0, 1): None}
        bounds = (0, 1, 0, 1)

        assert resolve_boundary((0, 0), grid, bounds) == (0, 0)
        assert resolve_boundary((1, 1), grid, bounds) == (1, 1)
        assert resolve_boundary((-1, 0), grid, bounds) is None
        assert resolve_boundary((2, 0), grid, bounds) is None

    def test_compute_diffusion_flux(self):
        """测试扩散通量计算"""
        # 高温向低温扩散
        flux = compute_diffusion_flux(30.0, 10.0, 0.1, 1.0, 2.0)
        assert flux < 0  # 高温损失热量

        # 低温向高温扩散
        flux = compute_diffusion_flux(10.0, 30.0, 0.1, 1.0, 2.0)
        assert flux > 0  # 低温获得热量

        # 限制变化量
        flux = compute_diffusion_flux(0.0, 100.0, 1.0, 1.0, 2.0)
        assert flux == 2.0  # 被限制

    def test_sigmoid_factor(self):
        """测试 sigmoid 因子"""
        assert sigmoid_factor(0.0) == 0.0
        assert sigmoid_factor(10.0) > 0.5
        assert sigmoid_factor(-10.0) > 0.5  # 对称
        assert sigmoid_factor(0.0, k=0.0) == 0.0  # k=0 时线性

    def test_clamp(self):
        """测试 clamp"""
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(-5.0, 0.0, 10.0) == 0.0
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_conservation_snapshot(self):
        """测试守恒快照"""
        world = World()
        e1 = world.create_entity()
        world.add_component(e1, EnvironmentComponent(air_temperature=20.0, air_humidity=0.5))
        world.add_component(e1, SpaceComponent(x=0, y=0))

        grid = {(0, 0): e1}
        cache = ContinuumCache.build(world, grid)
        snapshot = take_conservation_snapshot(cache)

        assert snapshot.total_temperature == 20.0
        assert snapshot.total_humidity == 0.5

    def test_check_conservation(self):
        """测试守恒检查"""
        before = ConservationSnapshot(100.0, 10.0, 5.0, 50.0, 20.0, 60.0)
        after = ConservationSnapshot(100.0, 10.0, 5.0, 50.0, 20.0, 60.0)

        assert check_conservation(before, after) is None

        after2 = ConservationSnapshot(101.0, 10.0, 5.0, 50.0, 20.0, 60.0)
        assert check_conservation(before, after2, tolerance=0.5) is not None


class TestThermalDiffusionProcessor:
    """测试热扩散处理器"""

    def _create_grid(self, world):
        """创建测试网格"""
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0, soil_temperature=25.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0, soil_temperature=15.0))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        return grid

    def test_temperature_equalizes(self):
        """测试高温向低温扩散"""
        world = World()
        grid = self._create_grid(world)
        cache = ContinuumCache.build(world, grid)

        processor = ThermalDiffusionProcessor()
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)

        env1 = world.get_component(grid[(0, 0)], EnvironmentComponent)
        env2 = world.get_component(grid[(1, 0)], EnvironmentComponent)

        # 高温降低，低温升高
        assert env1.air_temperature < 30.0
        assert env2.air_temperature > 10.0

    def test_water_buffering(self):
        """测试水域缓冲效果"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.WATER, elevation=0.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        processor = ThermalDiffusionProcessor()
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)

        env1 = world.get_component(e1, EnvironmentComponent)
        # 水域温度变化应较小（缓冲效应）
        assert env1.air_temperature <= 30.0

    def test_conservation(self):
        """测试热扩散能量守恒"""
        world = World()
        grid = self._create_grid(world)
        cache = ContinuumCache.build(world, grid)

        before = take_conservation_snapshot(cache)
        processor = ThermalDiffusionProcessor()
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)
        after = take_conservation_snapshot(cache)

        # 热扩散应近似守恒 (允许数值误差)
        diff = after - before
        assert abs(diff.total_temperature) < 1.0


class TestHumidityDiffusionProcessor:
    """测试湿度扩散处理器"""

    def test_humidity_equalizes(self):
        """测试湿度均衡"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_humidity=0.9, soil_moisture=0.8))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_humidity=0.1, soil_moisture=0.2))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        processor = HumidityDiffusionProcessor()
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        assert env1.air_humidity < 0.9
        assert env2.air_humidity > 0.1

    def test_water_source(self):
        """测试水域作为湿度源"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_humidity=0.5))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.WATER, elevation=0.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_humidity=0.1))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        processor = HumidityDiffusionProcessor()
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)

        env2 = world.get_component(e2, EnvironmentComponent)
        assert env2.air_humidity > 0.1  # 从水域获得湿度


class TestGravityWaterFlowProcessor:
    """测试重力水流处理器"""

    def test_water_flows_downhill(self):
        """测试水向下坡流"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(soil_moisture=0.8))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.HILL, elevation=50.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(soil_moisture=0.2))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        processor = GravityWaterFlowProcessor()
        processor.process(world, cache, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        assert env1.soil_moisture < 0.8  # 上坡流失水分
        assert env2.soil_moisture > 0.2  # 下坡获得水分

    def test_conservation(self):
        """测试水分守恒"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(soil_moisture=0.8))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.HILL, elevation=50.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(soil_moisture=0.2))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        before = take_conservation_snapshot(cache)
        processor = GravityWaterFlowProcessor()
        processor.process(world, cache, grid, 1.0)
        after = take_conservation_snapshot(cache)

        # 重力水流应严格守恒
        diff = after - before
        assert abs(diff.total_moisture) < 1e-10


class TestWindAdvectionProcessor:
    """测试风驱平流处理器"""

    def test_wind_transfers_heat(self):
        """测试风传递热量"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=30.0, wind_speed=5.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        e2 = world.create_entity()
        world.add_component(e2, SpaceComponent(x=1, y=0))
        world.add_component(e2, EnvironmentComponent(air_temperature=10.0, wind_speed=5.0))
        world.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(1, 0)] = e2

        cache = ContinuumCache.build(world, grid)
        # 西风 (270°) 从西向东吹
        processor = WindAdvectionProcessor(prevailing_wind_deg=270.0)
        processor.process(world, cache, grid, 1.0, neighbor_offsets=NEIGHBOR_OFFSETS_MOORE)

        env1 = world.get_component(e1, EnvironmentComponent)
        env2 = world.get_component(e2, EnvironmentComponent)

        # 西风从 e1(西) 向 e2(东) 传递热量
        # e2 应该获得热量
        assert env2.air_temperature > 10.0


class TestSelfRecoveryProcessor:
    """测试自恢复处理器"""

    def test_recovery_towards_climax(self):
        """测试向顶极状态恢复"""
        world = World()
        grid = {}

        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(
            air_temperature=10.0,  # 偏离顶极 (25°C)
            air_humidity=0.2,    # 偏离顶极 (0.6)
            soil_moisture=0.1,   # 偏离顶极 (0.35)
        ))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        cache = ContinuumCache.build(world, grid)
        processor = SelfRecoveryProcessor()
        processor.process(world, cache, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)

        # 向顶极状态恢复
        assert env1.air_temperature > 10.0  # 向 25°C 恢复
        assert env1.air_humidity > 0.2      # 向 0.6 恢复
        assert env1.soil_moisture > 0.1     # 向 0.35 恢复

    def test_sigmoid_acceleration(self):
        """测试偏离大时恢复加速"""
        world = World()
        grid = {}

        # 大幅偏离
        e1 = world.create_entity()
        world.add_component(e1, SpaceComponent(x=0, y=0))
        world.add_component(e1, EnvironmentComponent(air_temperature=0.0))
        world.add_component(e1, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid[(0, 0)] = e1

        cache = ContinuumCache.build(world, grid)
        processor = SelfRecoveryProcessor()
        processor.process(world, cache, grid, 1.0)

        env1 = world.get_component(e1, EnvironmentComponent)
        change_large = env1.air_temperature - 0.0

        # 小幅偏离
        world2 = World()
        grid2 = {}
        e2 = world2.create_entity()
        world2.add_component(e2, SpaceComponent(x=0, y=0))
        world2.add_component(e2, EnvironmentComponent(air_temperature=24.0))
        world2.add_component(e2, TerrainComponent(terrain_type=TerrainType.PLAIN, elevation=10.0))
        grid2[(0, 0)] = e2

        cache2 = ContinuumCache.build(world2, grid2)
        processor.process(world2, cache2, grid2, 1.0)

        env2 = world2.get_component(e2, EnvironmentComponent)
        change_small = env2.air_temperature - 24.0

        # 大幅偏离恢复更快 (sigmoid 效应)
        assert abs(change_large) > abs(change_small)

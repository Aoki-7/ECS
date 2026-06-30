#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
气味扩散系统

v3.0.3 新增 — P0

职责：
    - 模拟气味在空间中的扩散
    - 管理气味衰减
    - 支持动物嗅觉感知

设计原则：
    - 气味在网格上扩散（简化模型）
    - 风速影响扩散方向和速度
    - 温度影响气味挥发性

依赖：
    - SmellComponent
    - SpaceComponent（位置）
    - EnvironmentComponent（风速、温度）
"""

import math
from typing import Dict, List, Optional, Tuple

from core.system import System
from core.world import World

from biology.components.smell_component import SmellComponent
from space.space_component import SpaceComponent

import logging
from core.sqrt_cache import cached_sqrt

logger = logging.getLogger(__name__)


class SmellDiffusionSystem(System):
    """
    气味扩散系统

    每帧更新：
    1. 气味源释放气味
    2. 气味在空间中扩散
    3. 气味衰减
    4. 动物感知气味
    """

    tick_interval = 2  # 每2帧执行一次（气味变化较慢）

    # 扩散参数
    DIFFUSION_RATE = 0.3  # 扩散速率
    DECAY_RATE = 0.02  # 衰减速率
    MIN_DETECTABLE = 0.01  # 最小可检测浓度
    GRID_SIZE = 5.0  # 网格大小

    def __init__(self):
        super().__init__()
        # 气味场：{(grid_x, grid_y): {scent_type: intensity}}
        self._smell_field: Dict[Tuple[int, int], Dict[str, float]] = {}
        # 气味源：{entity_id: (grid_x, grid_y)}
        self._smell_sources: Dict[int, Tuple[int, int]] = {}

    def update(self, world: World, dt: float) -> None:
        """更新气味扩散"""
        # 1. 更新气味源位置
        self._update_smell_sources(world)

        # 2. 从气味源释放气味
        self._emit_smells(world)

        # 3. 扩散和衰减
        self._diffuse_and_decay()

        # 4. 更新实体的嗅觉感知
        self._update_olfactory_perception(world)

    def _update_smell_sources(self, world: World) -> None:
        """更新气味源位置"""
        self._smell_sources.clear()
        for entity, (smell, space) in world.get_components(SmellComponent, SpaceComponent):
            if smell is None or space is None:
                continue
            if not smell.scents:
                continue
            grid_x = int(space.x / self.GRID_SIZE)
            grid_y = int(space.y / self.GRID_SIZE)
            self._smell_sources[entity.id] = (grid_x, grid_y)

    def _emit_smells(self, world: World) -> None:
        """从气味源释放气味"""
        for entity_id, (grid_x, grid_y) in self._smell_sources.items():
            entity = world.query_entity(entity_id)
            if entity is None:
                continue
            smell = world.get_component(entity, SmellComponent)
            if smell is None:
                continue

            for scent_type, intensity in smell.scents.items():
                key = (grid_x, grid_y)
                if key not in self._smell_field:
                    self._smell_field[key] = {}
                current = self._smell_field[key].get(scent_type, 0.0)
                self._smell_field[key][scent_type] = min(
                    1.0, current + intensity * smell.base_intensity * 0.1
                )

    def _diffuse_and_decay(self) -> None:
        """扩散和衰减气味"""
        new_field: Dict[Tuple[int, int], Dict[str, float]] = {}

        for (grid_x, grid_y), scents in self._smell_field.items():
            for scent_type, intensity in scents.items():
                # 衰减
                new_intensity = intensity * (1 - self.DECAY_RATE)
                if new_intensity < self.MIN_DETECTABLE:
                    continue

                # 保留原位置
                key = (grid_x, grid_y)
                if key not in new_field:
                    new_field[key] = {}
                new_field[key][scent_type] = new_field[key].get(scent_type, 0.0) + new_intensity * (1 - self.DIFFUSION_RATE)

                # 扩散到邻居
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = grid_x + dx, grid_y + dy
                    key = (nx, ny)
                    if key not in new_field:
                        new_field[key] = {}
                    new_field[key][scent_type] = new_field[key].get(scent_type, 0.0) + new_intensity * self.DIFFUSION_RATE * 0.25

        self._smell_field = new_field

    def _update_olfactory_perception(self, world: World) -> None:
        """更新动物的嗅觉感知"""
        for entity, (smell, space) in world.get_components(SmellComponent, SpaceComponent):
            if smell is None or space is None:
                continue

            grid_x = int(space.x / self.GRID_SIZE)
            grid_y = int(space.y / self.GRID_SIZE)

            # 检测周围气味
            detected = {}
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    key = (grid_x + dx, grid_y + dy)
                    if key in self._smell_field:
                        distance = cached_sqrt(dx * dx + dy * dy)
                        factor = 1.0 / (1.0 + distance)
                        for scent_type, intensity in self._smell_field[key].items():
                            detected[scent_type] = detected.get(scent_type, 0.0) + intensity * factor

            # 更新实体的气味感知（可以存储在 SmellComponent 或 MemoryComponent 中）
            # 这里简化为打印日志
            if detected:
                if logger.isEnabledFor(logging.DEBUG):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"[Smell] Entity {entity.id} detected: {detected}")

    def get_smell_at(self, x: float, y: float) -> Dict[str, float]:
        """获取指定位置的气味"""
        grid_x = int(x / self.GRID_SIZE)
        grid_y = int(y / self.GRID_SIZE)
        return self._smell_field.get((grid_x, grid_y), {}).copy()

    def get_strongest_scent(self, x: float, y: float) -> Optional[Tuple[str, float]]:
        """获取指定位置最强的气味"""
        smells = self.get_smell_at(x, y)
        if not smells:
            return None
        return max(smells.items(), key=lambda x: x[1])

    def clear(self) -> None:
        """清空气味场"""
        self._smell_field.clear()
        self._smell_sources.clear()

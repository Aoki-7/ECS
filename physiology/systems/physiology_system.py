#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@文件:physiology_system.py
@说明:通用生理系统
@时间:2026/03/21 21:43:17
@作者:Sherry
@版本:1.1
'''

from core.system import System
from core.world import World
from physiology.components.physiology_component import PhysiologyComponent, PhysioStat


class PhysiologySystem(System):
    tick_interval = 20  # 每20帧执行一次

    @staticmethod
    def clamp_stat(stat: PhysioStat) -> None:
        """将生理指标值限制在 [min_value, max_value] 范围内"""
        if stat.value < stat.min_value:
            stat.value = stat.min_value
        elif stat.value > stat.max_value:
            stat.value = stat.max_value

    def update(self, world: World, dt: float):
        """
        通用生理系统（支持耦合）
        """

        for entity, [phys] in world.get_components(PhysiologyComponent):
            phys: PhysiologyComponent

            # --- Step 1: 归一化缓存 ---
            normalized = {
                name: stat.value / stat.max_value
                for name, stat in phys.stats.items()
            }

            # --- Step 2: 计算所有变化量 ---
            deltas = {}

            for name, stat in phys.stats.items():

                # 基础变化
                delta = stat.base_rate

                # 耦合影响
                for other_name, coeff in stat.influences.items():
                    if other_name in normalized:
                        delta += coeff * normalized[other_name]

                deltas[name] = delta

            # --- Step 3: 统一更新（避免顺序影响） ---
            for name, delta in deltas.items():
                stat = phys.stats[name]
                stat.value += delta * dt

            # --- Step 4: clamp ---
            for stat in phys.stats.values():
                self.clamp_stat(stat)

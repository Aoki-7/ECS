#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/immune_system.py
@说明:免疫系统

职责：
    - 管理免疫状态
    - 判断健康/传染/感染状态
    - 处理免疫记忆
"""

from core.system import System
from core.world import World

from biology.components.immune_component import ImmuneComponent


class ImmuneSystem(System):
    """免疫系统"""

    tick_interval = 5

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新免疫状态"""
        for entity, (immune,) in world.get_components(ImmuneComponent):
            # 更新感染持续时间
            if immune.infection_status not in ("healthy", "immune"):
                immune.infection_duration += dt

    def is_healthy(self, immune: ImmuneComponent) -> bool:
        """判断是否健康"""
        return immune.infection_status == "healthy"

    def is_contagious(self, immune: ImmuneComponent) -> bool:
        """判断是否具有传染性"""
        return immune.infection_status in ("infected", "incubating")

    def is_infected(self, immune: ImmuneComponent) -> bool:
        """判断是否已感染"""
        return immune.infection_status == "infected"

    def add_immune_memory(self, immune: ImmuneComponent, pathogen_type: str, strength: float = 1.0) -> None:
        """添加免疫记忆"""
        immune.immune_memory[pathogen_type] = max(
            immune.immune_memory.get(pathogen_type, 0.0),
            strength
        )

    def get_immune_strength(self, immune: ImmuneComponent, pathogen_type: str) -> float:
        """获取对特定病原体的免疫强度"""
        return immune.immune_memory.get(pathogen_type, 0.0)

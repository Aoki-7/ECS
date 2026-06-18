#!/usr/bin/env python3
"""
模拟驱动器

负责主循环执行、单步更新、资源再生、统计信息。
将驱动逻辑从 SimulationLoop 中剥离。
"""

import time
import logging
from typing import Dict, Any, Optional

from core.world import World
from core.components.world_config_component import WorldConfigComponent

logger = logging.getLogger(__name__)


class SimulationDriver:
    """
    模拟驱动器

    职责：
        1. 主循环执行
        2. 单步更新
        3. 资源再生
        4. 统计信息收集
        5. 性能监控
    """

    def __init__(self, world: World):
        self.world = world
        self.step_count = 0
        self.running = False
        self._stats: Dict[str, Any] = {}

    def run(self, max_steps: Optional[int] = None, delta_hours: float = 1.0) -> None:
        """运行模拟循环"""
        self.running = True
        logger.info("[Simulation] 模拟开始")

        try:
            while self.running:
                if max_steps is not None and self.step_count >= max_steps:
                    break
                self.step(delta_hours)
        except KeyboardInterrupt:
            logger.info("[Simulation] 用户中断")
        finally:
            self.running = False
            logger.info("[Simulation] 模拟结束")

    def step(self, delta_hours: float = 1.0) -> None:
        """执行单步更新"""
        self.world._step_count = self.step_count
        self.world.update(delta_hours)
        self.step_count += 1

    def stop(self) -> None:
        """停止模拟"""
        self.running = False

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        from human.components.basic.human_component import HumanComponent
        from animal.components.animal_component import AnimalComponent
        from plant.components.plant_component import PlantComponent

        stats = {
            'step': self.step_count,
            'entities': len(self.world.entities),
            'humans': 0,
            'animals': 0,
            'plants': 0,
        }

        for entity in self.world.entities:
            # 防御：entity 可能是 int 而不是 Entity 对象
            if isinstance(entity, int):
                entity_id = entity
            else:
                entity_id = entity.id
            
            if self.world.get_component(entity_id, HumanComponent):
                stats['humans'] += 1
            elif self.world.get_component(entity_id, AnimalComponent):
                stats['animals'] += 1
            elif self.world.get_component(entity_id, PlantComponent):
                stats['plants'] += 1

        self._stats = stats
        return stats

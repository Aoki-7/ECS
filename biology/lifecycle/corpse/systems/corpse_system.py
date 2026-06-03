#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
CorpseSystem — 尸体腐败与分解系统

职责：
    1. 处理所有挂载了 CorpseComponent 的实体
    2. 根据环境温度/湿度加速或减缓腐败
    3. 腐败完全后（decay_progress >= 1.0）销毁尸体实体
    4. （预留）传染病从尸体传播
    5. （预留）食腐动物被吸引
"""

import logging
from typing import Optional

from core.system import System
from core.world import World

from biology.lifecycle.corpse.components.corpse_component import CorpseComponent
from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent

logger = logging.getLogger(__name__)


class CorpseSystem(System):
    tick_interval = 1
    """
    尸体腐败系统。

    腐败速率受温度影响：
        - 高温（>30°C）：腐败加速 2x
        - 中温（10-30°C）：正常速率
        - 低温（0-10°C）：腐败减速 0.5x
        - 冰冻（<0°C）：腐败几乎停止 0.1x
    """

    def update(self, world: World, dt: float = 1.0) -> None:
        # 获取环境参考温度（简化处理，使用第一个环境单元格的温度）
        env_temp = self._get_ambient_temperature(world)

        temp_multiplier = self._compute_decay_multiplier(env_temp)

        for entity, (corpse,) in list(world.get_components(CorpseComponent)):
            if not world.has_entity(entity):
                continue

            # 检查是否已死亡标记
            if world.get_component(entity, DeadTagComponent) is None:
                continue

            # 累积腐败进度
            corpse.decay_progress += corpse.decay_rate * temp_multiplier * dt

            if corpse.decay_progress >= 1.0:
                # 尸体完全分解
                logger.debug(f"[Corpse] {corpse.original_name} fully decayed")
                world.remove_entity(entity)
                continue

    def _get_ambient_temperature(self, world: World) -> float:
        """获取环境参考温度。简化实现：查找第一个有温度信息的环境实体"""
        try:
            from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
            for _, (atm,) in world.get_components(AtmosphereComponent):
                return getattr(atm, 'air_temperature', 20.0)
        except (AttributeError, TypeError) as e:
            logger.warning(f"Failed to get ambient temperature: {e}")
        return 20.0  # 默认 20°C

    def _compute_decay_multiplier(self, temp: float) -> float:
        """根据温度计算腐败倍率"""
        if temp >= 30.0:
            return 2.0
        elif temp >= 10.0:
            return 1.0
        elif temp >= 0.0:
            return 0.5
        else:
            return 0.1

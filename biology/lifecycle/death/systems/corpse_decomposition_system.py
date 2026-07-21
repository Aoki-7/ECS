#!/usr/bin/env python3
"""
尸体分解系统 — 符合现实逻辑的资源闭环
动物/人类死亡后生成尸体，随时间分解，增加土壤肥力，促进植物生长，形成完整物质循环

触发规则：
1. 实体死亡后生成尸体实体，带有腐烂进度
2. 尸体每tick腐烂，腐烂速度随温度/湿度升高而加快
3. 完全腐烂后消失，对应位置土壤肥力增加
4. 腐烂过程中有概率吸引食腐动物（可选扩展）

版本: v4.16.0
"""
import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
# 生命周期阶段常量（临时替代枚举）
LifeCycleStage = type('LifeCycleStage', (), {
    'MATURE': 3,
    'DEAD': 4,
})()
from biology.components.corpse_component import CorpseComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class CorpseDecompositionSystem(System):
    """
    尸体分解系统
    实现生物 → 尸体 → 土壤肥力 → 植物的物质循环
    """

    tick_interval = 10  # 每10tick执行一次
    priority = 130  # 在DeathSystem之后运行

    # 配置参数
    BASE_DECAY_RATE = 0.01  # 基础腐烂速率 (每tick)
    TEMPERATURE_BONUS = 0.0005  # 每摄氏度额外腐烂速率
    HUMIDITY_BONUS = 0.01  # 每10%湿度额外腐烂速率
    FERTILITY_BONUS_AMOUNT = 0.2  # 完全腐烂后增加的土壤肥力

    def update(self, world: World, dt: float):
        # 获取全局环境温度/湿度
        world_env = world.get_component(world.get_world_entity(), EnvironmentComponent)
        temp = world_env.air_temperature if world_env else 15.0
        humidity = world_env.air_humidity if world_env else 0.5

        # 实际腐烂速率
        actual_decay_rate = self.BASE_DECAY_RATE + self.TEMPERATURE_BONUS * max(0, temp - 10) + self.HUMIDITY_BONUS * (humidity * 10)
        actual_decay_rate = max(0.001, min(0.1, actual_decay_rate))  # 限制范围

        # 处理所有尸体
        for entity, (corpse, space, lc) in world.query(CorpseComponent, SpaceComponent, LifeCycleComponent):
            # 增加腐烂进度
            corpse.decay_progress += actual_decay_rate * dt

            # 完全腐烂
            if corpse.decay_progress >= 1.0:
                # 找到该位置的土壤单元格，增加肥力
                for e, (soil, s) in world.query(SoilComponent, SpaceComponent):
                    if round(s.x) == round(space.x) and round(s.y) == round(space.y):
                        soil.fertility = min(1.0, soil.fertility + self.FERTILITY_BONUS_AMOUNT)
                        logger.debug(f"尸体{entity.id}完全腐烂，增加({space.x:.0f}, {space.y:.0f})土壤肥力至{soil.fertility:.2f}")
                        break
                # 销毁尸体实体
                world.delete_entity(entity)
                continue

            # 半腐烂状态：降低50%碰撞
            if corpse.decay_progress >= 0.5 and not corpse.half_decayed:
                corpse.half_decayed = True
                collider = world.get_component(entity, ColliderComponent)
                if collider:
                    collider.radius *= 0.5
                logger.debug(f"尸体{entity.id}半腐烂，碰撞缩小")

        # 死亡实体生成尸体
        for entity, (lc, space) in world.query(LifeCycleComponent, SpaceComponent):
            if lc.stage == LifeCycleStage.DEAD and not lc.corpse_created:
                # 标记已生成尸体，避免重复
                lc.corpse_created = True

                # 跳过植物（植物死亡直接掉木材，不生成尸体）
                if world.get_component(entity, PlantComponent) is not None:
                    continue

                # 创建尸体实体
                corpse_entity = world.create_entity()
                world.add_component(corpse_entity, SpaceComponent(x=space.x, y=space.y))
                world.add_component(corpse_entity, CorpseComponent(
                    source_entity_id=entity.id,
                    size=1.0 if world.get_component(entity, HumanComponent) is not None else 0.5,
                ))
                world.add_component(corpse_entity, LifeCycleComponent(
                    stage=LifeCycleStage.DEAD,
                    max_age=100.0,
                ))
                world.add_component(corpse_entity, ColliderComponent(radius=0.3))

                # 删除原死亡实体（或者保留？根据现有逻辑）
                # world.delete_entity(entity)
                logger.debug(f"实体{entity.id}死亡，生成尸体{corpse_entity.id}于({space.x:.0f}, {space.y:.0f})")

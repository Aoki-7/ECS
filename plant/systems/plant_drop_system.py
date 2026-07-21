#!/usr/bin/env python3
"""
植物掉落系统 — 符合现实逻辑的资源闭环
植物成熟结果时掉落可食用果实，死亡时掉落木材，补充食物/木材资源

触发规则：
1. 植物结果期（成熟阶段）每20tick 30%概率掉落一个浆果/果实
2. 植物自然死亡/被砍伐时，掉落对应数量的木材/果实
3. 果实有新鲜度，会腐烂消失
4. 掉落位置在植物周围1格范围内

版本: v4.16.0
"""
import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from plant.components.plant_component import PlantComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
# 生命周期阶段常量（临时替代枚举）
LifeCycleStage = type('LifeCycleStage', (), {
    'MATURE': 3,
    'DEAD': 4,
})()
from space.space_component import SpaceComponent
from resource.food.food_factory import FoodFactory
from resource.wood.wood_factory import WoodFactory

logger = logging.getLogger(__name__)


class PlantDropSystem(System):
    """
    植物掉落资源系统
    连接植物生长系统和离散资源实体
    """

    tick_interval = 20  # 每20tick执行一次
    priority = 120  # 在PlantGrowthSystem之后运行

    # 配置参数
    FRUIT_DROP_PROB = 0.3  # 结果期掉落概率
    MAX_FRUIT_PER_PLANT = 3  # 单株植物最多同时掉落3个果实
    WOOD_AMOUNT_PER_PLANT = 2.0  # 死亡后掉落木材量
    FRUIT_AMOUNT = 1.0  # 每个果实食物量

    def __init__(self):
        super().__init__()
        self._food_factory = FoodFactory()
        self._wood_factory = WoodFactory()

    def update(self, world: World, dt: float):
        for entity, plant, lc, space in world.query(PlantComponent, LifeCycleComponent, SpaceComponent):
            # 规则1：成熟期（结果期）掉落果实
            if lc.stage == LifeCycleStage.MATURE and hasattr(plant, 'yield_type'):
                # 统计该植物周围已有多少掉落的果实
                existing_fruits = 0
                from resource.food.components.food_component import FoodComponent
                for e, food, s in world.query(FoodComponent, SpaceComponent):
                    if (
                        round(s.x) in [round(space.x) - 1, round(space.x), round(space.x) + 1]
                        and round(s.y) in [round(space.y) - 1, round(space.y), round(space.y) + 1]
                        and food.food_type == plant.yield_type
                    ):
                        existing_fruits += 1

                if existing_fruits < self.MAX_FRUIT_PER_PLANT and random.random() < self.FRUIT_DROP_PROB:
                    # 随机位置掉落
                    x = space.x + random.uniform(-1.0, 1.0)
                    y = space.y + random.uniform(-1.0, 1.0)
                    # 创建果实
                    self._food_factory.create_food(
                        world,
                        x=x,
                        y=y,
                        food_type=plant.yield_type,
                        amount=self.FRUIT_AMOUNT,
                    )
                    logger.debug(f"植物{entity.id}掉落果实: ({x:.1f}, {y:.1f}), 类型={plant.yield_type}")

            # 规则2：植物死亡掉落木材
            if lc.stage == LifeCycleStage.DEAD and not plant.dropped:
                # 标记已掉落，避免重复掉落
                plant.dropped = True
                # 掉落木材
                x = space.x + random.uniform(-0.5, 0.5)
                y = space.y + random.uniform(-0.5, 0.5)
                self._wood_factory.create_wood(
                    world,
                    x=x,
                    y=y,
                    amount=self.WOOD_AMOUNT_PER_PLANT,
                )
                logger.debug(f"植物{entity.id}死亡掉落木材: ({x:.1f}, {y:.1f}), 量={self.WOOD_AMOUNT_PER_PLANT}")

                # 如果是结果期死亡，额外掉落全部果实
                if lc.stage_prev == LifeCycleStage.MATURE and hasattr(plant, 'yield_amount'):
                    for _ in range(min(3, int(plant.yield_amount))):
                        x_f = space.x + random.uniform(-1.0, 1.0)
                        y_f = space.y + random.uniform(-1.0, 1.0)
                        self._food_factory.create_food(
                            world,
                            x=x_f,
                            y=y_f,
                            food_type=plant.yield_type,
                            amount=self.FRUIT_AMOUNT * 0.5,
                        )

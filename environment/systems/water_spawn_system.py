#!/usr/bin/env python3
"""
水源实体生成系统 — 符合现实逻辑的资源闭环
根据水循环系统的网格含水量，动态生成人类可拾取的水源实体

触发规则：
1. 土壤饱和度 > 90% 且无现有水源 → 生成小型水坑（5份水）
2. 降雨量 > 10mm/h 时 → 10%概率在随机位置生成临时积水（3份水）
3. 河流水位 > 80% → 岸边生成可收集的水源（10份水）
4. 水源实体被喝完后自动销毁

版本: v4.16.0
"""
import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.hydrology.components.water_body_component import WaterBodyComponent
from space.space_component import SpaceComponent
from resource.water.water_factory import WaterFactory
from resource.water.components.water_component import WaterComponent

logger = logging.getLogger(__name__)


class WaterSpawnSystem(System):
    """
    动态生成可拾取水源实体的系统
    连接水循环网格和离散资源实体
    """

    tick_interval = 10  # 每10tick执行一次
    priority = 110  # 在WaterCycleSystem之后运行

    # 配置参数
    SOIL_SATURATION_THRESHOLD = 0.9  # 土壤饱和度阈值，超过则生成水坑
    PIT_AMOUNT = 5.0  # 水坑水量
    RAIN_SPAWN_PROB = 0.1  # 降雨时积水生成概率
    RAIN_AMOUNT_THRESHOLD = 10.0  # 降雨强度阈值（mm/h），超过则可能生成积水
    RIVER_SPAWN_THRESHOLD = 0.8  # 河流水位阈值，超过则岸边生成水源

    def __init__(self):
        super().__init__()
        self._water_factory = WaterFactory()

    def update(self, world: World, dt: float):
        # 获取世界全局降雨强度
        world_env = world.get_world_component(EnvironmentComponent)
        current_rainfall = world_env.rainfall if world_env else 0.0

        # 遍历所有环境网格单元（带SoilComponent + SpaceComponent的）
        for entity, soil, space in world.query(SoilComponent, SpaceComponent):
            # 规则1：土壤饱和生成水坑
            if soil.moisture >= self.SOIL_SATURATION_THRESHOLD:
                # 检查该位置是否已有水源
                has_water = False
                for e, (water, s) in world.query(WaterComponent, SpaceComponent):
                    if round(s.x) == round(space.x) and round(s.y) == round(space.y):
                        has_water = True
                        break
                if not has_water:
                    # 生成水坑
                    self._water_factory.create_water(
                        world,
                        x=space.x,
                        y=space.y,
                        amount=self.PIT_AMOUNT,
                    )
                    logger.debug(f"生成水坑: ({space.x:.0f}, {space.y:.0f}), 水量={self.PIT_AMOUNT}")

            # 规则2：降雨时生成临时积水
            if current_rainfall >= self.RAIN_AMOUNT_THRESHOLD and random.random() < self.RAIN_SPAWN_PROB:
                # 随机生成少量积水
                self._water_factory.create_water(
                    world,
                    x=space.x + random.uniform(-0.5, 0.5),
                    y=space.y + random.uniform(-0.5, 0.5),
                    amount=random.uniform(1.0, 3.0),
                )
                logger.debug(f"降雨生成积水: ({space.x:.0f}, {space.y:.0f})")

        # 规则3：河流/湖泊岸边生成可收集水源
        for entity, (water_body, space) in world.query(WaterBodyComponent, SpaceComponent):
            if water_body.water_level / water_body.max_level >= self.RIVER_SPAWN_THRESHOLD:
                # 岸边随机偏移位置生成水源
                for _ in range(2):
                    x = space.x + random.choice([-1, 0, 1])
                    y = space.y + random.choice([-1, 0, 1])
                    if not (x == space.x and y == space.y):
                        # 检查是否已有水源
                        has_water = False
                        for e, (water, s) in world.query(WaterComponent, SpaceComponent):
                            if round(s.x) == x and round(s.y) == y:
                                has_water = True
                                break
                        if not has_water:
                            self._water_factory.create_water(
                                world,
                                x=x,
                                y=y,
                                amount=random.uniform(5.0, 15.0),
                            )
                            logger.debug(f"河流生成水源: ({x}, {y})")

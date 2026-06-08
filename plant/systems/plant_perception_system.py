#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物感知系统

处理植物的化学/物理感知：
1. 光感知：检测光照强度和方向
2. 水感知：检测土壤水分
3. 邻近植物检测：检测竞争/化感作用
4. 记忆形成：将感知结果记录到统一记忆层
"""

import math
import logging

from core.system import System
from core.world import World

from plant.components.plant_component import PlantComponent
from plant.components.plant_perception_component import PlantPerceptionComponent
from plant.components.canopy_component import CanopyComponent
from space.space_component import SpaceComponent
from environment.light_field.components.light_receiver_component import LightReceiverComponent

logger = logging.getLogger(__name__)


class PlantPerceptionSystem(System):
    """
    植物感知系统

    植物没有神经系统，但具有化学感知能力。
    本系统模拟植物的向光性、向水性等感知行为。
    """
    tick_interval = 30  # 植物感知较慢

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有植物的感知状态"""
        for entity, (plant, perception, space) in world.get_components(
            PlantComponent, PlantPerceptionComponent, SpaceComponent
        ):
            # 1. 光感知
            self._perceive_light(world, entity, perception, space)

            # 2. 水感知
            self._perceive_water(world, entity, perception, space)

            # 3. 邻近植物检测
            self._detect_nearby_plants(world, entity, perception, space)

            # 4. 记录到统一记忆层
            self._record_to_memory_layer(world, entity, perception, space)

    def _perceive_light(
        self, world: World, entity, perception: PlantPerceptionComponent, space: SpaceComponent
    ) -> None:
        """光感知：检测光照强度和方向"""
        light = world.get_component(entity, LightReceiverComponent)
        if light is None:
            return

        # 记录光强度
        perception.last_light_intensity = light.received_total

        # 简化：光源方向假设为上方（90度）
        # 实际实现可结合太阳位置计算
        perception.last_light_direction = 90.0

        # 记录感知历史
        perception.perception_history.append((
            getattr(world, 'time', 0), "light", light.received_total
        ))

    def _perceive_water(
        self, world: World, entity, perception: PlantPerceptionComponent, space: SpaceComponent
    ) -> None:
        """水感知：检测土壤水分"""
        # 简化：从环境组件获取土壤湿度
        env = world.get_environment()
        if env is not None and hasattr(env, 'soil_moisture'):
            perception.soil_moisture = env.soil_moisture
        else:
            # 默认湿度
            perception.soil_moisture = 0.5

        # 简化水分梯度（实际应查询邻近位置）
        perception.water_gradient_x = 0.0
        perception.water_gradient_y = 0.0

        perception.perception_history.append((
            getattr(world, 'time', 0), "water", perception.soil_moisture
        ))

    def _detect_nearby_plants(
        self, world: World, entity, perception: PlantPerceptionComponent, space: SpaceComponent
    ) -> None:
        """检测邻近植物（竞争/化感作用）"""
        from space.space_system import SpaceSystem
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 查询附近实体
        nearby = space_system.query_radius(space.x, space.y, 3.0)
        perception.nearby_plants = []

        for other_id in nearby:
            if other_id == entity.id:
                continue
            other = world.query_entity(other_id)
            if other is None:
                continue
            other_plant = world.get_component(other, PlantComponent)
            if other_plant is not None:
                perception.nearby_plants.append(other_id)

        # 检测化感作用（简化：邻近植物过多时触发）
        perception.allelopathy_detected = len(perception.nearby_plants) > 3

    def _record_to_memory_layer(
        self, world: World, entity, perception: PlantPerceptionComponent, space: SpaceComponent
    ) -> None:
        """将感知结果记录到统一记忆层"""
        memory_layer = world.get_memory_layer()
        if memory_layer is None:
            return

        from memory_layer import SubjectType

        # 记录光感知
        if perception.last_light_intensity > 0:
            # 注册"光"概念（如果不存在）
            concept_id = f"light_at_{space.x:.0f}_{space.y:.0f}"
            if concept_id not in memory_layer._concepts:
                from memory_layer import SensoryDescription
                memory_layer.create_abstract_concept(
                    concept_id=concept_id,
                    name=f"位置({space.x:.0f}, {space.y:.0f})的光照",
                    description=SensoryDescription(
                        shape="无形",
                        color="明亮" if perception.last_light_intensity > 50 else "昏暗",
                        temperature="温暖" if perception.last_light_intensity > 50 else "凉爽",
                    ),
                    concept_type="abstract",
                )

            memory_layer.record_contact(
                subject_id=entity.id,
                subject_type=SubjectType.ANIMAL,  # 植物暂用 ANIMAL 类型
                entity_id=-1,  # 抽象概念无实体ID
                contact_type="chemical",
                intensity=min(1.0, perception.last_light_intensity / 100.0),
                context=f"感知到光照强度 {perception.last_light_intensity:.1f}",
            )

        # 记录水感知
        if perception.soil_moisture < 0.3:
            # 缺水警告
            memory_layer.record_contact(
                subject_id=entity.id,
                subject_type=SubjectType.ANIMAL,
                entity_id=-1,
                contact_type="chemical",
                intensity=0.8,
                context=f"土壤湿度低: {perception.soil_moisture:.2f}",
            )

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
BirthSystem — 生育执行系统

职责：
    1. 扫描所有挂载了 BirthRequestComponent 的实体
    2. 调用 HumanFactory 创建新生儿
    3. 分配部落（通过 TribeSystem）
    4. 重置孕妇的 ReproductionComponent 状态
    5. 移除 BirthRequestComponent

设计原则：
    - ReproductionSystem 只负责怀孕判定与进度推进
    - BirthSystem 统一处理实体创建、部落分配等"副作用"
    - 消除 ReproductionSystem 对 HumanFactory 和 TribeSystem 的直接依赖
"""

import logging
from core.system import System
from core.world import World
from identity.event_log_system import EventLog

from human.components.social.birth_request_component import BirthRequestComponent
from human.components.social.reproduction_component import ReproductionComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

logger = logging.getLogger(__name__)


class BirthSystem(System):
    tick_interval = 1  # 每帧执行，确保 BirthRequestComponent 被及时处理

    def update(self, world: World, dt: float):
        current_time = world.get_time().total_hours if world.get_time() else 0.0

        for entity, (birth_req,) in list(world.get_components(BirthRequestComponent)):
            if not world.has_entity(entity):
                continue

            # 1. 创建新生儿
            from human.human_factory import HumanFactory
            child = HumanFactory.create_human(
                world, birth_req.child_name, birth_req.child_x, birth_req.child_y
            )

            # 2. 修正新生儿年龄为0
            age_comp = world.get_component(child, LifeCycleComponent)
            if age_comp:
                age_comp.age = 0

            # 3. 分配部落（继承母亲部落）
            from human.systems.social.tribe_system import TribeSystem
            tribe_system = world.get_system(TribeSystem)
            if tribe_system:
                tribe_system.assign_birth_tribe(world, child, entity, current_time)

            # 4. 重置孕妇的繁衍状态
            repro = world.get_component(entity, ReproductionComponent)
            if repro:
                repro.is_pregnant = False
                repro.pregnancy_time = 0.0
                repro.last_birth_time = current_time
                repro.partner_id = None

            # 5. 移除生育请求组件
            world.remove_component(entity, BirthRequestComponent)

            # 6. 记录日志
            logger.debug(
                f"[生育成功] 实体 {entity} 生育了新生儿 {child}"
                f"（名字：{birth_req.child_name}，时间：{current_time}）"
            )
            EventLog.log(
                world,
                event_type="birth",
                description=f"{birth_req.child_name} 出生",
                entity_id=child.id,
                target_id=entity.id,
                location=(birth_req.child_x, birth_req.child_y),
                data={"child_name": birth_req.child_name, "parent_id": entity.id},
                severity="milestone",
            )

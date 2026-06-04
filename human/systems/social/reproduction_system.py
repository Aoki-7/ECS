#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reproduction_system.py
@说明:繁衍系统
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

import logging
import random

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

logger = logging.getLogger(__name__)

from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.social.reproduction_component import ReproductionComponent
from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.gender_component import GenderComponent, Gender
from space.space_component import SpaceComponent


class ReproductionSystem(System):
    """
    繁衍系统
    处理怀孕判定与怀孕进度推进。
    
    核心流程：
    1. 检查配偶条件（已婚、生育年龄、伴侣存活）
    2. 随机触发怀孕事件
    3. 更新怀孕时间
    4. 怀孕期满后挂载 BirthRequestComponent，由 BirthSystem 执行实际生育
    """

    tick_interval = 5  # 每5帧执行一次，降低 EventLog 写入频率

    # 每 tick 基础怀孕概率（女性、已婚/恋爱中、可生育年龄）
    BIRTH_CHANCE_PER_TICK = 0.015

    def update(self, world: World, dt):
        """
        每个时间步的更新
        
        Args:
            world: World实例
            dt: 时间增量（小时）
        """
        current_time = world.get_time().total_hours

        for entity, (relation, repro, age, gender) in list(world.get_components(
            RelationshipComponent, ReproductionComponent, LifeCycleComponent, GenderComponent
        )):
            if not relation or not repro or not age or not gender:
                continue
            
            relation: RelationshipComponent
            repro: ReproductionComponent
            age: LifeCycleComponent
            gender: GenderComponent

            # 检查是否具备怀孕条件（仅限女性）
            partner_alive = (relation.partner_id is not None and
                             world.query_entity(relation.partner_id) is not None)
            if (gender.gender == Gender.FEMALE and
                relation.status in (RelationshipStatus.MARRIED, RelationshipStatus.DATING) and
                partner_alive and
                age.is_reproductive_age()):
                # 检查是否可以生育（不在怀孕、冷却期已过）
                if not repro.is_pregnant and current_time - repro.last_birth_time > repro.birth_cooldown:
                    # 随机生育几率（基于dt，适度提高）
                    if random.random() < self.BIRTH_CHANCE_PER_TICK * dt:
                        self.start_pregnancy(world, entity, relation, repro)

            # 处理怀孕进度
            if repro.is_pregnant:
                repro.pregnancy_time += dt
                if repro.pregnancy_time >= repro.pregnancy_duration:
                    self._request_birth(world, entity, repro)

    def start_pregnancy(self, world: World, entity, relation: RelationshipComponent, repro: ReproductionComponent):
        """
        开始怀孕
        
        Args:
            world: World实例
            entity: 孕妇entity
            relation: 关系组件
            repro: 繁衍组件
        """
        repro.is_pregnant = True
        repro.pregnancy_time = 0.0
        repro.partner_id = relation.partner_id
        logger.debug(f"[生育] 实体 {entity} 开始怀孕（伴侣：{relation.partner_id}）")
        EventLog.log(
            world, event_type="pregnancy_start",
            description=f"实体 {entity.id} 开始怀孕",
            entity_id=entity.id,
            target_id=relation.partner_id,
            severity="info"
        )

    def _request_birth(self, world: World, entity, repro: ReproductionComponent):
        """
        准备生育请求：计算新生儿名字和位置，挂载 BirthRequestComponent。
        实际的实体创建、部落分配由 BirthSystem 统一处理。
        
        Args:
            world: World实例
            entity: 生育者entity
            repro: 繁衍组件
        """
        from human.components.social.birth_request_component import BirthRequestComponent

        parent_space = world.get_component(entity, SpaceComponent)
        parent_identity = None
        try:
            from human.components.basic.identity_component import IdentityComponent
            parent_identity = world.get_component(entity, IdentityComponent)
        except (ImportError, AttributeError):
            parent_identity = None
        
        # 生成新人类的名字（简化，避免无限叠加 _Child）
        if parent_identity:
            base_name = parent_identity.name
            if "_Child" in base_name:
                base_name = base_name.split("_Child")[0]
            child_name = f"{base_name}_Child"
        else:
            child_name = f"Child_{entity.id}"
        
        # 计算新生儿的位置（在父母附近，随机偏移1格）
        child_x = (parent_space.x + random.randint(-1, 1)) if parent_space else 0
        child_y = (parent_space.y + random.randint(-1, 1)) if parent_space else 0
        from core.components.world_config_component import WorldConfigComponent
        world_config = world.get_world_component(WorldConfigComponent)
        child_x, child_y = world_config.clamp_position(child_x, child_y)
        
        # 挂载 BirthRequestComponent，由 BirthSystem 执行实际生育
        world.add_component(entity, BirthRequestComponent(
            child_name=child_name,
            child_x=child_x,
            child_y=child_y,
            partner_id=repro.partner_id
        ))
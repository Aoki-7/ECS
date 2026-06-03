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
    处理怀孕、生育和人口增长。
    
    核心流程：
    1. 检查配偶条件（已婚、生育年龄）
    2. 随机触发怀孕事件
    3. 更新怀孕时间
    4. 怀孕期满后生育新entity
    """

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
            if (gender.gender == Gender.FEMALE and
                relation.status in (RelationshipStatus.MARRIED, RelationshipStatus.DATING) and
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
                    self.give_birth(world, entity, repro)

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

    def give_birth(self, world: World, entity, repro: ReproductionComponent):
        """
        生育新人类entity
        
        Args:
            world: World实例
            entity: 生育者entity
            repro: 繁衍组件
        """
        current_time = world.get_time().total_hours
        
        # 获取生育者的信息
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
            # 如果名字已经包含 _Child，截断到原始名字 + 代际标记
            if "_Child" in base_name:
                # 提取原始名字（第一个 _Child 之前的部分）
                base_name = base_name.split("_Child")[0]
            child_name = f"{base_name}_Child"
        else:
            child_name = f"Child_{entity.id}"
        
        # 计算新生儿的位置（在父母附近，随机偏移1格）
        child_x = (parent_space.x + random.randint(-1, 1)) if parent_space else 0
        child_y = (parent_space.y + random.randint(-1, 1)) if parent_space else 0
        child_x = max(0, min(99, child_x))
        child_y = max(0, min(99, child_y))
        
        # 使用 HumanFactory 创建完整新生儿（含初始水/食物/背包）
        from human.human_factory import HumanFactory
        child = HumanFactory.create_human(world, child_name, child_x, child_y)
        
        # 修正新生儿年龄为0
        age_comp = world.get_component(child, LifeCycleComponent)
        if age_comp:
            age_comp.age = 0
        
        # 分配部落（继承母亲部落）
        from human.systems.social.tribe_system import TribeSystem
        tribe_system = world.get_system(TribeSystem)
        if tribe_system:
            tribe_system.assign_birth_tribe(world, child, entity, current_time)
        
        # 重置生育者的繁衍状态
        repro.is_pregnant = False
        repro.pregnancy_time = 0.0
        repro.last_birth_time = current_time
        repro.partner_id = None
        
        logger.debug(f"[生育成功] 实体 {entity} 生育了新生儿 {child}（名字：{child_name}，时间：{current_time}）")
        EventLog.log(
            world, event_type="birth",
            description=f"{child_name} 出生",
            entity_id=child.id,
            target_id=entity.id,
            location=(child_x, child_y),
            data={"child_name": child_name, "parent_id": entity.id},
            severity="milestone"
        )
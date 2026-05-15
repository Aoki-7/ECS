#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reproduction_system.py
@说明:繁衍系统
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World
import random

from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.social.reproduction_component import ReproductionComponent
from human.components.basic.age_component import AgeComponent
from human.components.basic.gender_component import GenderComponent, Gender
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

    def update(self, world: World, dt):
        """
        每个时间步的更新
        
        Args:
            world: World实例
            dt: 时间增量（小时）
        """
        current_time = world.get_time().total_hours

        for entity, (relation, repro, age, gender) in world.get_components(
            RelationshipComponent, ReproductionComponent, AgeComponent, GenderComponent
        ):
            if not relation or not repro or not age or not gender:
                continue
            
            relation: RelationshipComponent
            repro: ReproductionComponent
            age: AgeComponent
            gender: GenderComponent

            # 检查是否具备怀孕条件
            if relation.status in (RelationshipStatus.MARRIED, RelationshipStatus.DATING) and age.is_reproductive_age():
                # 检查是否可以生育（不在怀孕、冷却期已过）
                if not repro.is_pregnant and current_time - repro.last_birth_time > repro.birth_cooldown:
                    # 随机生育几率（基于dt）
                    if random.random() < 0.001 * dt:  # 低概率
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
        print(f"[生育] 实体 {entity} 开始怀孕（伴侣：{relation.partner_id}）")

    def give_birth(self, world: World, entity, repro: ReproductionComponent):
        """
        生育新人类entity
        
        Args:
            world: World实例
            entity: 生育者entity
            repro: 繁衍组件
        """
        # 延迟导入，避免循环导入
        from human.entities.human_entity import HumanEntity
        
        current_time = world.get_time().total_hours
        
        # 获取生育者的信息
        parent_space = world.get_component(entity, SpaceComponent)
        parent_identity = None
        try:
            from human.components.basic.identity_component import IdentityComponent
            parent_identity = world.get_component(entity, IdentityComponent)
        except:
            pass
        
        # 创建新entity
        child = world.create_entity()
        
        # 生成新人类的名字（简化）
        if parent_identity:
            child_name = f"{parent_identity.name}_Child"
        else:
            child_name = f"Child_{child.id}"
        
        # 计算新生儿的位置（在父母附近）
        child_x = parent_space.x if parent_space else 0
        child_y = parent_space.y if parent_space else 0
        
        # 随机性别
        child_gender = random.choice([Gender.MALE, Gender.FEMALE])
        
        # 创建新生儿的所有组件
        HumanEntity.create_components(
            world, 
            child, 
            name=child_name,
            x=child_x, 
            y=child_y,
            age=0,  # 新生儿年龄为0
            gender=child_gender
        )
        
        # 重置生育者的繁衍状态
        repro.is_pregnant = False
        repro.pregnancy_time = 0.0
        repro.last_birth_time = current_time
        repro.partner_id = None
        
        print(f"[生育成功] 实体 {entity} 生育了新生儿 {child}（名字：{child_name}，时间：{current_time}）")
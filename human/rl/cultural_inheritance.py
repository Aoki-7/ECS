#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文化传承系统：知识和技能通过教学传承给下一代，形成文化积累
"""
import logging
import random
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from core.system import System
from core.world import World
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from human.components.abilities.skill_component import SkillComponent
from space.space_component import SpaceComponent
from human.rl.social_structure import SocialStructureSystem, RoleType

logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """知识类型"""
    SURVIVAL = auto()       # 生存知识
    CRAFTING = auto()       # 制作知识
    BUILDING = auto()       # 建筑知识
    FARMING = auto()        # 农业知识
    HUNTING = auto()        # 狩猎知识
    MEDICINE = auto()       # 医药知识
    SOCIAL = auto()         # 社交知识
    LEADERSHIP = auto()     # 领导知识
    TECHNOLOGY = auto()     # 技术知识
    CULTURE = auto()        # 文化知识

@dataclass
class Knowledge:
    """知识：可以传承的文化积累"""
    knowledge_id: int
    knowledge_type: KnowledgeType
    name: str
    description: str
    level: float = 1.0  # 知识等级，越高越先进
    creator_id: Optional[int] = None
    creation_time: float = 0.0
    is_active: bool = True

@dataclass
class CulturalTradition:
    """文化传统：群体共享的文化习俗"""
    tradition_id: int
    name: str
    description: str
    group_id: int
    created_time: float = 0.0
    is_active: bool = True

class CulturalInheritanceSystem(System):
    """文化传承系统：知识和技能通过教学传承给下一代"""
    tick_interval = 20  # 每20帧更新一次

    def __init__(self):
        self.knowledge: Dict[int, Knowledge] = {}
        self.next_knowledge_id = 0
        self.traditions: Dict[int, CulturalTradition] = {}
        self.next_tradition_id = 0
        self.entity_knowledge: Dict[int, Dict[KnowledgeType, float]] = {}  # 实体ID -> 知识类型 -> 掌握程度
        self.group_knowledge: Dict[int, Dict[KnowledgeType, float]] = {}  # 群体ID -> 知识类型 -> 平均水平

    def update(self, world: World, dt: float):
        """更新文化传承系统"""
        logger.info("[CulturalInheritance] 更新文化传承系统...")
        # 1. 创造新知识
        self._create_knowledge(world)

        # 2. 教学传承
        self._teach_knowledge(world)

        # 3. 形成文化传统
        self._form_traditions(world)

        # 4. 知识演进
        self._evolve_knowledge(world)

    def _create_knowledge(self, world: World):
        """创造新知识"""
        # 根据人口数量调整知识创造概率
        humans = [e.id for e, _ in world.get_components(HumanComponent)]
        population = len(humans)

        # 人口越多，知识创造越活跃
        create_probability = min(0.05, 0.001 * population)

        if random.random() < create_probability and len(self.knowledge) < 100:
            knowledge_type = random.choice(list(KnowledgeType))
            # 知识等级与现有人口知识水平相关
            avg_level = 1.0
            if self.entity_knowledge:
                all_levels = []
                for knowledge_dict in self.entity_knowledge.values():
                    all_levels.extend(knowledge_dict.values())
                if all_levels:
                    avg_level = sum(all_levels) / len(all_levels)

            knowledge = Knowledge(
                knowledge_id=self.next_knowledge_id,
                knowledge_type=knowledge_type,
                name=f"{knowledge_type.name}知识{self.next_knowledge_id}",
                description=f"关于{knowledge_type.name}的高级知识",
                level=random.uniform(avg_level, avg_level + 2.0),
                creator_id=random.choice(humans) if humans else None,
                creation_time=0.0
            )
            self.knowledge[knowledge.knowledge_id] = knowledge
            self.next_knowledge_id += 1
            logger.info(f"[CulturalInheritance] 创造新知识: {knowledge.name}, 等级: {knowledge.level:.1f}, 人口: {population}")

    def _teach_knowledge(self, world: World):
        """教学传承"""
        # 获取所有人类（使用实体对象作为键）
        human_entities = [e for e, _ in world.get_components(HumanComponent)]
        if len(human_entities) < 2:
            logger.debug(f"[CulturalInheritance] 教学传承: 人类数量不足 {len(human_entities)}")
            return

        # 每次都尝试教学，让文化传承更活跃
        teacher_entity = random.choice(human_entities)
        student_entity = random.choice([e for e in human_entities if e != teacher_entity])
        teacher_id = teacher_entity.id
        student_id = student_entity.id
        logger.debug(f"[CulturalInheritance] 教学传承: 选择教师 {teacher_id} 和学生 {student_id}")

        # 检查距离（放宽距离限制）
        teacher_pos = world.get_component(teacher_id, SpaceComponent)
        student_pos = world.get_component(student_id, SpaceComponent)
        if not teacher_pos or not student_pos:
            logger.debug(f"[CulturalInheritance] 教学传承: 位置组件缺失")
            return
        distance = ((teacher_pos.x - student_pos.x)**2 + (teacher_pos.y - student_pos.y)**2)**0.5
        if distance > 20.0:  # 进一步增加教学距离
            logger.debug(f"[CulturalInheritance] 教学传承: 距离太远 {distance:.2f}")
            return

        # 教学传承
        teacher_knowledge = self.entity_knowledge.get(teacher_id, {})
        student_knowledge = self.entity_knowledge.get(student_id, {}).copy()  # 使用copy避免引用问题
        print(f"[DEBUG] 教师知识: {teacher_knowledge}, 学生知识: {student_knowledge}")

        # 选择教师最擅长的知识
        if teacher_knowledge:
            best_knowledge = max(teacher_knowledge.items(), key=lambda x: x[1])
            knowledge_type, teacher_level = best_knowledge
            student_level = student_knowledge.get(knowledge_type, 0.0)
            print(f"[DEBUG] 知识类型: {knowledge_type}, 教师水平: {teacher_level}, 学生水平: {student_level}")

            # 教学效果：学生水平提升
            if teacher_level > student_level:
                learn_amount = (teacher_level - student_level) * 0.2  # 增加学习效果
                student_knowledge[knowledge_type] = student_level + learn_amount
                self.entity_knowledge[student_id] = student_knowledge
                print(f"[DEBUG] 教学成功: 学生知识更新为 {student_knowledge}")
                logger.info(f"[CulturalInheritance] 教学传承: 实体{teacher_id} 教 实体{student_id} {knowledge_type.name}, 提升{learn_amount:.2f}")
            else:
                print(f"[DEBUG] 教学失败: 教师水平不高于学生")
        else:
            print(f"[DEBUG] 教学失败: 教师没有知识")

    def _form_traditions(self, world: World):
        """形成文化传统"""
        # 获取社会结构系统
        social_system = None
        for system in world.systems:
            if isinstance(system, SocialStructureSystem):
                social_system = system
                break
        if not social_system:
            return

        # 为每个群体形成文化传统
        for group in social_system.groups.values():
            # 计算群体知识平均水平
            group_knowledge = {}
            for member_id in group.members:
                member_knowledge = self.entity_knowledge.get(member_id, {})
                for knowledge_type, level in member_knowledge.items():
                    if knowledge_type not in group_knowledge:
                        group_knowledge[knowledge_type] = 0.0
                    group_knowledge[knowledge_type] += level

            if not group_knowledge:
                continue

            # 计算平均值
            for knowledge_type in group_knowledge:
                group_knowledge[knowledge_type] /= len(group.members)

            # 更新群体知识
            self.group_knowledge[group.group_id] = group_knowledge

            # 如果群体有擅长的知识，形成文化传统
            best_knowledge = max(group_knowledge.items(), key=lambda x: x[1])
            knowledge_type, level = best_knowledge

            # 降低文化传统形成门槛
            if level > 0.5 and not any(t.group_id == group.group_id and t.is_active for t in self.traditions.values()):
                tradition = CulturalTradition(
                    tradition_id=self.next_tradition_id,
                    name=f"{group.name}的{knowledge_type.name}传统",
                    description=f"{group.name} 擅长 {knowledge_type.name}，形成了独特的文化传统",
                    group_id=group.group_id,
                    created_time=0.0
                )
                self.traditions[tradition.tradition_id] = tradition
                self.next_tradition_id += 1
                logger.info(f"[CulturalInheritance] 形成文化传统: {tradition.name}, 水平: {level:.2f}")

    def _evolve_knowledge(self, world: World):
        """知识演进"""
        # 知识会随时间逐渐提升
        for knowledge in self.knowledge.values():
            if knowledge.is_active:
                # 知识缓慢提升
                knowledge.level += 0.001
                # 限制知识等级上限
                knowledge.level = min(knowledge.level, 10.0)

    def get_entity_knowledge(self, entity_id: int) -> Dict[KnowledgeType, float]:
        """获取实体的知识"""
        return self.entity_knowledge.get(entity_id, {})

    def get_group_knowledge(self, group_id: int) -> Dict[KnowledgeType, float]:
        """获取群体的知识"""
        return self.group_knowledge.get(group_id, {})

    def get_knowledge_distribution(self) -> Dict[KnowledgeType, int]:
        """获取知识分布"""
        knowledge_counts = {}
        for knowledge in self.knowledge.values():
            knowledge_counts[knowledge.knowledge_type] = knowledge_counts.get(knowledge.knowledge_type, 0) + 1
        return knowledge_counts

    def get_traditions(self) -> Dict[int, CulturalTradition]:
        """获取所有文化传统"""
        return self.traditions.copy()
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
技术系统进阶扩展实现
包含集体教学、技术失传、书籍阅读三个扩展功能
"""

import random
from typing import Dict, List, Tuple
from core.world import World
from civilization.systems.human_tech_innovation_system import HumanTechInnovationSystem
from human.components.skill.human_tech_skill_component import HumanTechSkillComponent
from human.components.social.social_component import SocialComponent
from human.components.basic.human_component import HumanComponent
from civilization.components.item.book_component import BookComponent
from space.space_component import SpaceComponent
from human.components.economic.inventory.inventory_component import InventoryComponent

import logging
logger = logging.getLogger(__name__)

def add_tech_extensions(system: HumanTechInnovationSystem, world: World) -> None:
    """给技术系统附加进阶扩展功能"""
    # 扩展3：集体教学
    def _process_collective_teaching():
        if system._tick_counter % 24 != 0:
            return
        tribes = {}
        for entity, (social, tech_skill, human) in world.get_components([SocialComponent, HumanTechSkillComponent, HumanComponent]):
            tribe_id = getattr(social, 'tribe_id', -1)
            if tribe_id == -1:
                continue
            if tribe_id not in tribes or len(tech_skill.skills) > len(tribes[tribe_id][1].skills):
                tribes[tribe_id] = (entity.id, tech_skill)
        for tribe_id, (teacher_id, teacher_skill) in tribes.items():
            if len(teacher_skill.skills) < 1:
                continue
            teach_skills = list(teacher_skill.skills.keys())[:3]
            for entity, (social, student_skill, human) in world.get_components([SocialComponent, HumanTechSkillComponent, HumanComponent]):
                if getattr(social, 'tribe_id', -1) == tribe_id and entity.id != teacher_id:
                    for skill in teach_skills:
                        if skill not in student_skill.skills:
                            teacher_level = teacher_skill.get_skill_level(skill)
                            student_skill.learn_from_teacher(skill, teacher_level * 0.3, teacher_skill.skills[skill].get('domain', 'general'))
        if tribes:
            logger.info(f"[CollectiveTeach] 今日共 {len(tribes)} 个部落组织集体教学")
    
    # 扩展4：技术失传
    def _check_tech_extinction():
        current_counts = {name:0 for name in system.global_technology_library}
        for entity, tech_skill in world.get_components(HumanTechSkillComponent):
            for skill in tech_skill.skills:
                if skill in current_counts:
                    current_counts[skill] +=1
        extinct = [k for k,v in current_counts.items() if v ==0]
        for tech in extinct:
            del system.global_technology_library[tech]
            logger.warning(f"[TechExtinct] 技术《{tech}》已失传")
    
    # 扩展5：书籍阅读
    def _process_book_learning():
        books = []
        for e, (book, space, _) in world.get_components([BookComponent, SpaceComponent, 'ItemComponent']):
            if book.durability >0 and book.content_type == 'tech_manual':
                books.append((e, book, space.x, space.y))
        if not books:
            return
        for human_id, (_, tech_skill, space, inv) in world.get_components([HumanComponent, HumanTechSkillComponent, SpaceComponent, InventoryComponent]):
            # 找书
            book = None
            for item in inv.items:
                if item.get('type') == 'book':
                    for b_id, b, _, _ in books:
                        if b_id == item.get('entity_id'):
                            book = b
                            break
                    if book:
                        break
            else:
                near = [b for _,b,x,y in books if abs(x-space.x)<=3 and abs(y-space.y)<=3]
                if near:
                    book = near[0]
            if not book or not book.stored_skills:
                return
            skill = book.stored_skills[0]
            if skill['name'] not in tech_skill.skills:
                tech_skill.skills[skill['name']] = {
                    'experience': skill['experience'] * book.quality * 0.7,
                    'proficiency': 0,
                    'mastery_time': 0,
                    'domain': skill['domain'],
                    'learned_from_book': True
                }
                book.durability -=0.05
                logger.info(f"[BookLearn] E{human_id} 阅读《{book.title}》掌握《{skill['name']}》")
    
    # 挂载到系统update中
    original_update = system.update
    def extended_update(world: World, dt=1.0):
        original_update(world, dt)
        _process_collective_teaching()
        _check_tech_extinction()
        _process_book_learning()
    system.update = extended_update

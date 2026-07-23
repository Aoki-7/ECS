#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
人类技术创新系统 v4.16.0
技术掌握由人类个体主观能动性产生，不是系统自动生成
"""

import random
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto

from core.system import System
from core.world import World

from human.components.basic.human_component import HumanComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.social.social_component import SocialComponent
from human.components.health.health_component import HealthComponent
from human.components.skill.human_tech_skill_component import HumanTechSkillComponent, SkillProficiency
from space.space_component import SpaceComponent

import logging

logger = logging.getLogger(__name__)


class TechDomain(Enum):
    """技术领域（仅用于分类，不限制具体技术）"""
    AGRICULTURE = "农业"
    PRODUCTION = "生产"
    CONSTRUCTION = "建筑"
    ENERGY = "能源"
    MEDICINE = "医学"
    SOCIAL = "社会"
    MILITARY = "军事"
    TRANSPORT = "交通"
    CULTURE = "文化"
    MATERIAL = "材料"


class HumanTechInnovationSystem(System):
    """
    人类技术创新系统
    核心设计：技术由人类个体主动掌握，不是系统自动生成

    机制：
    1. 人类通过实践活动积累经验
    2. 当人类有明确需求（饥饿、寒冷、疾病等）或好奇心时，会产生研究意愿
    3. 研究意愿 + 实践经验 + 知识 + 创造力 + 资源 → 创新成功概率
    4. 创新成功后，该个体掌握一项新技能，可加入全局技术知识库
    5. 技能可以通过社会传播（观察、教学）传递给他人
    """
    tick_interval = 10

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._tick_counter = 0
        
        # 全局技术知识库：{技术名: 发明者ID, 发明时间, 领域, 普及程度}
        self.global_technology_library: Dict[str, Dict] = {}
        
        # 活动和领域的映射
        self.activity_to_domain = {
            'gather_food': TechDomain.AGRICULTURE,
            'hunt_animal': TechDomain.MILITARY,
            'plant_crops': TechDomain.AGRICULTURE,
            'mine_stone': TechDomain.CONSTRUCTION,
            'mine_ore': TechDomain.PRODUCTION,
            'build_structure': TechDomain.CONSTRUCTION,
            'trade': TechDomain.SOCIAL,
            'heal_other': TechDomain.MEDICINE,
            'fight': TechDomain.MILITARY,
            'cook_food': TechDomain.PRODUCTION,
            'make_tool': TechDomain.PRODUCTION,
            'research': TechDomain.PRODUCTION,
            'experiment': TechDomain.MATERIAL,
        }
        
        # 名词库，用于生成具体技术名
        self._noun_lib = {
            TechDomain.AGRICULTURE: ["谷物", "蔬菜", "果树", "土壤", "灌溉", "肥料", "农具", "育种", "轮作", "梯田"],
            TechDomain.PRODUCTION: ["石器", "木器", "铜器", "铁器", "陶器", "工具", "武器", "衣物", "食物", "材料"],
            TechDomain.CONSTRUCTION: ["房屋", "城墙", "道路", "桥梁", "水利", "宫殿", "住宅", "工场", "仓库", "地基"],
            TechDomain.ENERGY: ["火", "水力", "风力", "畜力", "煤炭", "石油", "蒸汽", "电力", "太阳能"],
            TechDomain.MEDICINE: ["草药", "外伤", "感冒", "发烧", "瘟疫", "外科", "内科", "针灸", "按摩", "药剂"],
            TechDomain.SOCIAL: ["氏族", "部落", "城邦", "法律", "货币", "税收", "教育", "宗教", "等级"],
            TechDomain.MILITARY: ["弓箭", "刀剑", "盔甲", "盾牌", "战车", "城墙", "战术", "阵法", "侦察", "防御"],
            TechDomain.TRANSPORT: ["道路", "车轮", "船只", "驮兽", "桥梁", "航道", "驿站"],
            TechDomain.CULTURE: ["文字", "绘画", "音乐", "舞蹈", "历法", "神话", "建筑"],
            TechDomain.MATERIAL: ["黏土", "皮革", "纤维", "矿石", "金属", "合金", "玻璃", "陶瓷"],
        }
        
        self._verb_lib = ["原始", "基础", "改良", "新式", "传统", "高效", "节能", "生态", "复合", "精密"]
        self._template_lib = ["{verb}{noun}法", "{noun}{verb}术", "{verb}{noun}工艺", "{noun}制作技术", "{noun}改良术"]

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新人类技术创新与技艺传播"""
        human_entities = list(world.get_components((
            HumanComponent, HumanTechSkillComponent, KnowledgeComponent, HealthComponent,
            SocialComponent, SpaceComponent
        )))
        
        # 1. 个体创新逻辑
        for entity, (human, tech_skill, knowledge, health, social, space) in human_entities:
            # 根据最近活动积累实践时长
            self._record_practice_from_activity(entity, tech_skill, knowledge)
            
            # 判断个体是否有研究意愿
            research_willingness = self._calculate_research_willingness(entity, human, tech_skill, health, knowledge)
            
            # 有研究意愿时，尝试主动创新或改进技术
            if research_willingness > 0 and self._rng.random() < research_willingness:
                self._try_innovation(world, entity, human, tech_skill, knowledge)
            
            # 扩展5：有大师级技能的人类，有概率把技能写成书籍
            if len(tech_skill.skills) >= 3:
                top_skill_level = max(tech_skill.get_skill_level(s) for s in tech_skill.skills)
                if top_skill_level >= 0.8 and self._rng.random() < 0.005:  # 0.5%概率写书
                    self._try_write_book(world, entity, tech_skill, knowledge)
            
            # 扩展5：附近有书时，有概率阅读学习
            if self._rng.random() < 0.02:  # 2%概率尝试阅读
                self._try_read_book(world, entity, tech_skill, knowledge, social, space)
        
        # 2. 技艺传播逻辑：人类之间互相传授技能
        self._trigger_skill_teaching(world, human_entities)
    
    def _trigger_skill_teaching(self, world: World, human_entities: List) -> None:
        """触发人类之间的技能教学行为"""
        # 先按位置分组，只考虑距离近的人类
        position_map = {}
        for entity, (human, tech_skill, knowledge, health, social, space) in human_entities:
            pos_key = (int(space.x), int(space.y))
            if pos_key not in position_map:
                position_map[pos_key] = []
            position_map[pos_key].append((entity, human, tech_skill, social))
        
        # 遍历每个位置的人类，互相尝试教学
        for pos, humans_in_pos in position_map.items():
            if len(humans_in_pos) < 2:
                continue  # 只有1个人没法教学
            
            # 每个老师找学生教学
            for teacher_data in humans_in_pos:
                teacher_id, teacher_human, teacher_skill, teacher_social = teacher_data
                if not teacher_skill.skills:
                    continue  # 没技能没法教
                
                # 老师的教学意愿：技能越熟练、知识越多、越友好，越愿意教
                teacher_level = sum(teacher_skill.get_skill_level(s) for s in teacher_skill.skills) / max(1, len(teacher_skill.skills))
                teach_willingness = 0.02 + teacher_level * 0.1  # 基础2%概率，最高12%
                if hasattr(teacher_social, 'friendliness'):
                    teach_willingness += teacher_social.friendliness * 0.05
                
                if self._rng.random() >= teach_willingness:
                    continue
                
                # 老师最熟练的技能，优先教这个
                teachable_skills = sorted(
                    teacher_skill.skills.items(),
                    key=lambda x: teacher_skill.get_skill_level(x[0]),
                    reverse=True
                )[:3]  # 选最熟练的3个技能
                if not teachable_skills:
                    continue
                
                target_skill_name, target_skill_data = teachable_skills[0]
                target_skill_level = teacher_skill.get_skill_level(target_skill_name)
                
                # 找学生：优先教亲属、同部落、新手
                for student_data in humans_in_pos:
                    student_id, student_human, student_skill, student_social = student_data
                    if student_id == teacher_id:
                        continue
                    if student_skill.has_skill(target_skill_name):
                        continue  # 已经会了不用教
                    
                    # 计算学习意愿
                    learn_willingness = 0.3  # 基础30%愿意学
                    # 亲属关系加成
                    is_family = False
                    if hasattr(teacher_social, 'relations') and student_id in teacher_social.relations:
                        relation_type = teacher_social.relations.get(student_id, {}).get('type', '')
                        if relation_type in ['parent', 'child', 'sibling', 'spouse']:
                            learn_willingness += 0.4
                            is_family = True
                    # 同部落加成
                    if teacher_social.social_group_id != -1 and teacher_social.social_group_id == student_social.social_group_id:
                        learn_willingness += 0.2
                    # 新手加成：越不懂这个领域的越愿意学
                    student_domain_practice = student_skill.get_practice_hours(target_skill_data.get('domain', 'general'))
                    if student_domain_practice < 50:
                        learn_willingness += 0.2
                    
                    if self._rng.random() < learn_willingness:
                        # 教学成功
                        base_exp = 20.0
                        
                        # 扩展1：幼年学习buff，18岁以下学习速度+50%
                        if student_human.age < 18:
                            base_exp *= 1.5
                        
                        # 扩展2：大师传承效果，老师熟练度100%时，有20%概率学生直接获得大量经验
                        master_bonus = 1.0
                        if target_skill_level >= 1.0:
                            if self._rng.random() < 0.2:
                                master_bonus = 3.0
                                logger.info(f"[MasterInherit] 大师级传承：E{teacher_id} 将《{target_skill_name}》倾囊相授给 E{student_id}，领悟突飞猛进！")
                        
                        # 亲属/代际传承额外增加经验
                        if is_family:
                            base_exp += 30.0
                            logger.info(f"[TechInherit] 亲属代际传承：E{teacher_id} 将《{target_skill_name}》传授给后代 E{student_id}")
                        
                        # 应用经验加成
                        total_exp = base_exp * master_bonus
                        student_skill.gain_experience(target_skill_name, total_exp, target_skill_data.get('domain', 'general'))
                        self.teach_skill(world, teacher_id, student_id, target_skill_name)
                        
                        break  # 每次最多教一个学生
        
        # 扩展3：技术失传检查，每个周期检查是否有技术没人掌握了
        self._check_tech_extinction(world, human_entities)
        
        # 扩展4：集体教学，有大师的部落定期组织授课
        self._trigger_group_teaching(world, human_entities)
    
    def _check_tech_extinction(self, world: World, human_entities: List) -> None:
        """检查技术是否失传：如果某技术没有任何人类掌握，就从全局技术库中移除"""
        all_held_skills = set()
        for _, (_, tech_skill, _, _, _, _) in human_entities:
            for skill_name in tech_skill.skills.keys():
                all_held_skills.add(skill_name)
        
        # 找出已经没人掌握的技术
        extinct_techs = []
        for tech_name, tech_data in self.global_technology_library.items():
            if tech_name not in all_held_skills:
                extinct_techs.append(tech_name)
        
        # 移除失传技术
        for tech_name in extinct_techs:
            del self.global_technology_library[tech_name]
            logger.warning(
                f"[TechExtinct] 技术《{tech_name}》已失传！最后掌握它的人类已经死亡，无人继承这项技艺。"
            )
    
    def _trigger_group_teaching(self, world: World, human_entities: List) -> None:
        """集体教学：部落有大师级技能持有者时，每100步组织一次授课"""
        if self._tick_counter % 100 != 0:
            return
        
        # 按部落分组
        tribe_map = {}
        for entity, (human, tech_skill, knowledge, health, social, space) in human_entities:
            tribe_id = social.social_group_id
            if tribe_id == -1:
                continue
            if tribe_id not in tribe_map:
                tribe_map[tribe_id] = []
            tribe_map[tribe_id].append((entity, human, tech_skill, social, space))
        
        # 每个部落检查是否有大师
        for tribe_id, members in tribe_map.items():
            if len(members) < 5:
                continue  # 部落太小，不需要集体教学
            
            # 找部落里的大师
            masters = []
            for member_data in members:
                entity, human, tech_skill, social, space = member_data
                for skill_name in tech_skill.skills:
                    level = tech_skill.get_skill_level(skill_name)
                    if level >= 1.0:
                        masters.append((entity, tech_skill, skill_name, level))
            
            if not masters:
                continue
            
            # 随机选一个大师来授课
            teacher_id, teacher_skill, teach_skill, teach_level = self._rng.choice(masters)
            
            # 找所有不会这个技能的部落成员当学生
            students = []
            for member_data in members:
                entity, human, tech_skill, social, space = member_data
                if entity == teacher_id or tech_skill.has_skill(teach_skill):
                    continue
                students.append(entity)
            
            if not students:
                continue
            
            # 集体授课，每个学生获得基础经验
            teach_exp = 10.0 * teach_level
            for student_id in students:
                student_skill = world.get_component(student_id, HumanTechSkillComponent)
                if student_skill:
                    student_skill.gain_experience(teach_skill, teach_exp)
                    self.teach_skill(world, teacher_id, student_id, teach_skill)
            
            logger.info(
                f"[GroupTeach] 部落{tribe_id} 组织集体授课：大师E{teacher_id} 向 {len(students)} 名部落成员传授《{teach_skill}》技术"
            )
    
    def _record_practice_from_activity(self, entity, tech_skill: HumanTechSkillComponent, knowledge: KnowledgeComponent) -> None:
        """根据记忆记录最近活动，积累实践时长"""
        memory = knowledge if hasattr(knowledge, 'recent_events') else None
        if not memory or not hasattr(memory, 'events'):
            return
        
        recent_events = memory.events[-5:] if len(memory.events) > 5 else memory.events
        for event in recent_events:
            event_type = event.get('type', '') if isinstance(event, dict) else getattr(event, 'type', '')
            domain = self.activity_to_domain.get(event_type)
            if domain:
                tech_skill.add_practice(domain.value, hours=1.0)
    
    def _calculate_research_willingness(
        self, entity, human: HumanComponent, 
        tech_skill: HumanTechSkillComponent, health: HealthComponent, 
        knowledge: KnowledgeComponent
    ) -> float:
        """
        计算人类个体的研究意愿 0-1
        由主观能动性驱动：需求、好奇心、资源、创造力共同决定
        """
        # 基础意愿
        willingness = 0.05 + tech_skill.creativity * 0.1
        
        # 需求驱动：饥饿、寒冷、疾病等会推动人类研究解决问题
        if hasattr(health, 'hunger') and health.hunger > 0.7:
            willingness += 0.15  # 饥饿推动农业/生产技术研究
        if hasattr(health, 'temperature') and health.temperature < 0.3:
            willingness += 0.1   # 寒冷推动建筑/能源技术研究
        if hasattr(health, 'disease_count') and health.disease_count > 0:
            willingness += 0.15  # 疾病推动医学研究
        
        # 资源充裕时更容易有好奇心研究
        inventory = knowledge if hasattr(knowledge, 'items') else None  # 简化，实际需要InventoryComponent
        # 这里用知识量作为替代指标
        knowledge_count = len(knowledge.knowledge) if hasattr(knowledge, 'knowledge') else 0
        if knowledge_count > 10:
            willingness += 0.1  # 知识丰富的人有好奇心
        
        # 经验驱动：某领域实践越多，越容易在该领域创新
        max_practice = max(tech_skill.total_practice_hours.values()) if tech_skill.total_practice_hours else 0
        if max_practice > 100:
            willingness += 0.1
        
        # 研究方向明确时，意愿更高
        if tech_skill.research_focus:
            willingness += 0.05
        
        # 限制在0-1之间
        return min(1.0, max(0.0, willingness))
    
    def _try_innovation(
        self, world: World, entity, human: HumanComponent,
        tech_skill: HumanTechSkillComponent, knowledge: KnowledgeComponent
    ) -> None:
        """尝试让个体进行技术创新"""
        # 确定创新方向：最熟悉的领域或研究方向
        if tech_skill.research_focus:
            # 主动研究方向
            target_domain = self._parse_domain(tech_skill.research_focus)
        else:
            # 选择实践最多的领域
            if tech_skill.total_practice_hours:
                domain_name = max(tech_skill.total_practice_hours.items(), key=lambda x: x[1])[0]
                target_domain = self._parse_domain(domain_name)
            else:
                target_domain = TechDomain.PRODUCTION
        
        # 计算创新成功概率
        practice_hours = tech_skill.get_practice_hours(target_domain.value)
        knowledge_count = len(knowledge.knowledge) if hasattr(knowledge, 'knowledge') else 0
        creativity = tech_skill.creativity
        
        # 创新概率 = 基础 + 实践经验 + 知识 + 创造力
        base_prob = 0.02
        practice_bonus = min(0.3, practice_hours / 1000)
        knowledge_bonus = min(0.2, knowledge_count / 200)
        creativity_bonus = creativity * 0.2
        total_prob = base_prob + practice_bonus + knowledge_bonus + creativity_bonus
        total_prob = min(0.8, total_prob)  # 最高80%概率
        
        if self._rng.random() > total_prob:
            return
        
        # 创新成功！生成新技术技能
        new_tech_name = self._generate_tech_name(target_domain)
        
        # 如果该技术已经存在于世界，则提升熟练度（改进已有技术）
        if new_tech_name in self.global_technology_library:
            tech_skill.gain_experience(new_tech_name, 50.0, target_domain.value)
            return
        
        # 否则，这是一个全新的技术发明
        invention_time = world.get_time() if hasattr(world, 'get_time') else 0.0
        tech_skill.create_skill(new_tech_name, target_domain.value, invention_time)
        
        # 加入全局技术库
        self.global_technology_library[new_tech_name] = {
            'inventor_id': entity.id,
            'invention_time': invention_time,
            'domain': target_domain.value,
            'popularity': 1,  # 初始普及度1人掌握
        }
        
        # 发明者获得知识加成
        if hasattr(knowledge, 'add_knowledge'):
            knowledge.add_knowledge(f"invented_{new_tech_name}", value=10.0)
        
        logger.warning(
            f"[Innovation] 人类 E{entity.id} 通过主观探索掌握了新技术：《{new_tech_name}》\n"
            f"领域：{target_domain.value}，实践时长：{practice_hours:.0f}小时，"
            f"创造力：{creativity:.2f}，发明概率：{total_prob:.1%}"
        )
    
    def _generate_tech_name(self, domain: TechDomain) -> str:
        """根据领域生成动态技术名称"""
        template = self._rng.choice(self._template_lib)
        noun = self._rng.choice(self._noun_lib.get(domain, ["未知技术"]))
        verb = self._rng.choice(self._verb_lib)
        return template.format(verb=verb, noun=noun)
    
    def _parse_domain(self, domain_name: str) -> TechDomain:
        """从字符串解析技术领域"""
        for d in TechDomain:
            if d.value == domain_name or d.name.lower() == domain_name.lower():
                return d
        return TechDomain.PRODUCTION
    
    def teach_skill(
        self, world: World, teacher_id: int, student_id: int, skill_name: str
    ) -> bool:
        """技能教学传播：老师将技能传授给学生"""
        teacher_skill = world.get_component(teacher_id, HumanTechSkillComponent)
        student_skill = world.get_component(student_id, HumanTechSkillComponent)
        
        if not teacher_skill or not student_skill or skill_name not in teacher_skill.skills:
            return False
        
        teacher_level = teacher_skill.get_skill_level(skill_name)
        domain = teacher_skill.skills[skill_name].get('domain', 'general')
        student_skill.learn_from_teacher(skill_name, teacher_level, domain)
        
        # 更新技术普及度
        if skill_name in self.global_technology_library:
            self.global_technology_library[skill_name]['popularity'] += 1
        
        logger.info(
            f"[TechTeach] E{teacher_id} 向 E{student_id} 传授了《{skill_name}》技术"
        )
        return True
    
    def get_technology_summary(self) -> Dict:
        """获取当前世界技术普及情况摘要"""
        return {
            'total_technologies': len(self.global_technology_library),
            'most_popular': sorted(
                self.global_technology_library.items(),
                key=lambda x: x[1]['popularity'],
                reverse=True
            )[:5],
            'domains': {}
        }
    
    def _try_write_book(self, world: World, entity, tech_skill: HumanTechSkillComponent, knowledge: KnowledgeComponent) -> None:
        """人类尝试把自己最熟练的技能写成书籍"""
        # 必须已经掌握"文字"相关技能才能写书
        has_writing_skill = False
        for skill_name in tech_skill.skills:
            if "文字" in skill_name or "书写" in skill_name or "记录" in skill_name:
                has_writing_skill = True
                break
        
        if not has_writing_skill:
            return  # 不会写字没法写书
        
        # 选最熟练的3个技能写入书籍
        top_skills = sorted(
            tech_skill.skills.items(),
            key=lambda x: tech_skill.get_skill_level(x[0]),
            reverse=True
        )[:3]
        
        if not top_skills:
            return
        
        # 生成书名
        first_skill_name = top_skills[0][0]
        book_title = f"《{first_skill_name}大全》"
        book_quality = min(1.0, max(0.3, tech_skill.get_skill_level(top_skills[0][0]) * self._rng.uniform(0.8, 1.2)))
        
        # 创建书籍实体
        book_entity = world.create_entity()
        from civilization.components.item.book_component import BookComponent
        from space.space_component import SpaceComponent
        book = BookComponent(
            title=book_title,
            author_id=entity.id,
            creation_time=world.get_time() if hasattr(world, 'get_time') else 0.0,
            content_type="tech_manual",
            quality=book_quality,
            language="common"
        )
        
        # 写入技能
        for skill_name, skill_data in top_skills:
            skill_level = tech_skill.get_skill_level(skill_name)
            exp_value = skill_level * 300.0  # 技能越熟练，书里的经验越多
            book.add_skill(skill_name, skill_data.get('domain', 'general'), exp_value)
        
        world.add_component(book_entity, book)
        
        # 书籍放在作者当前位置
        space = world.get_component(entity, SpaceComponent)
        if space:
            book_space = SpaceComponent(x=space.x + self._rng.randint(-1, 1), y=space.y + self._rng.randint(-1, 1))
            world.add_component(book_entity, book_space)
        
        logger.warning(
            f"[BookCreated] E{entity.id} 创作了书籍 {book_title}，记录了{len(top_skills)}项技能，品质{book_quality:.1f}"
        )
    
    def _try_read_book(self, world: World, entity, tech_skill: HumanTechSkillComponent, knowledge: KnowledgeComponent, social, space) -> None:
        """人类尝试阅读附近的书籍学习技能"""
        from civilization.components.item.book_component import BookComponent
        from space.space_component import SpaceComponent
        # 查找当前位置2格范围内的书籍
        nearby_books = []
        for book_entity, (book, book_space) in world.get_components([BookComponent, SpaceComponent]):
            dx = book_space.x - space.x
            dy = book_space.y - space.y
            distance = (dx**2 + dy**2) ** 0.5
            if distance <= 2.0 and book.is_usable():
                nearby_books.append(book)
        
        if not nearby_books:
            return
        
        # 选最近的一本书阅读
        book = nearby_books[0]
        
        # 读者智商影响学习效率，简单用知识量估算
        reader_intelligence = min(1.0, len(knowledge.knowledge) / 50.0 if hasattr(knowledge, 'knowledge') else 0.5)
        learn_result = book.read(reader_intelligence)
        
        if not learn_result:
            return
        
        # 学习书中的技能
        learned_count = 0
        for skill_data in learn_result:
            skill_name = skill_data['skill_name']
            exp = skill_data['experience']
            domain = skill_data['domain']
            
            tech_skill.gain_experience(skill_name, exp, domain)
            learned_count += 1
            
            # 如果是新技术，加入全局技术库
            if skill_name not in self.global_technology_library:
                self.global_technology_library[skill_name] = {
                    'inventor_id': -1,  # 不知道原发明者
                    'invention_time': world.get_time() if hasattr(world, 'get_time') else 0.0,
                    'domain': domain,
                    'popularity': 1,
                    'rediscovered': True
                }
        
        logger.info(
            f"[BookRead] E{entity.id} 阅读了书籍《{book.title}》，学习了{learned_count}项技能，获得了总共{sum(s['experience'] for s in learn_result):.0f}点经验"
        )
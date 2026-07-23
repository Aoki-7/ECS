#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动态技术生成系统 v2.0
完全无硬编码技术，技术由人类实践和需求自然生成
"""

import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Callable, Optional
from enum import Enum, auto

from core.system import System
from core.world import World
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.social.social_component import SocialComponent
from human.components.basic.human_component import HumanComponent

import logging

logger = logging.getLogger(__name__)


class TechDomain(Enum):
    """技术领域（动态生成，不限制）"""
    AGRICULTURE = auto()    # 农业相关
    PRODUCTION = auto()     # 生产工具
    CONSTRUCTION = auto()   # 建筑
    ENERGY = auto()         # 能源
    MEDICINE = auto()       # 医学
    SOCIAL = auto()         # 社会制度
    MILITARY = auto()       # 军事
    TRANSPORT = auto()      # 交通
    CULTURE = auto()        # 文化
    MATERIAL = auto()       # 材料


@dataclass
class DynamicTechnology:
    """动态生成的技术类，完全无硬编码属性"""
    tech_id: str
    name: str
    description: str
    domain: TechDomain
    level: int = 1
    inventor_id: int = -1  # 发明者ID
    invention_time: float = 0.0
    # 效果：动态生成的效果函数，接受世界对象作为参数
    effects: List[Callable[[World], None]] = field(default_factory=list)
    # 前置条件：哪些活动/知识/资源是发明这个技术的前提
    prerequisites: Dict[str, float] = field(default_factory=dict)
    # 效果参数：存储动态效果的参数
    effect_params: Dict[str, float] = field(default_factory=dict)


class DynamicTechnologySystem(System):
    """
    动态技术系统 - 完全无硬编码技术
    技术由人类的实践活动和需求自然生成，每次模拟的技术树完全不同
    """
    tick_interval = 50  # 每50帧检查一次技术发明

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        
        # 已发明的技术 {tech_id: DynamicTechnology}
        self.discovered_technologies: Dict[str, DynamicTechnology] = {}
        
        # 人类活动统计：{活动类型: 累计次数}，用于触发技术发明
        self.activity_stats: Dict[str, int] = {
            'gather_food': 0,
            'hunt_animal': 0,
            'plant_crops': 0,
            'mine_stone': 0,
            'mine_ore': 0,
            'build_structure': 0,
            'trade': 0,
            'heal_other': 0,
            'fight': 0,
            'cook_food': 0,
            'make_tool': 0,
        }
        
        # 常见问题统计：{问题类型: 发生次数}，用于触发解决问题的技术
        self.problem_stats: Dict[str, int] = {
            'food_shortage': 0,
            'cold': 0,
            'disease': 0,
            'enemy_attack': 0,
            'tool_break': 0,
            'building_collapse': 0,
            'water_shortage': 0,
        }
        
        # 技术名称生成模板
        self._name_templates = {
            TechDomain.AGRICULTURE: [
                "{verb}{noun}技术", "改良{noun}法", "{noun}种植术", "{noun}培育技术", "{noun}灌溉法"
            ],
            TechDomain.PRODUCTION: [
                "{noun}制作术", "{noun}加工法", "改良{noun}工艺", "{noun}制造技术", "{noun}精炼法"
            ],
            TechDomain.CONSTRUCTION: [
                "{noun}建造术", "{noun}建筑法", "改良{noun}结构", "{noun}施工技术", "{noun}设计原理"
            ],
            TechDomain.ENERGY: [
                "{noun}利用技术", "{noun}获取法", "{noun}转换技术", "{noun}储存法", "{noun}动力系统"
            ],
            TechDomain.MEDICINE: [
                "{noun}治疗法", "{noun}医术", "改良{noun}疗法", "{noun}防疫技术", "{noun}药剂配方"
            ],
            TechDomain.SOCIAL: [
                "{noun}制度", "{noun}组织法", "改良{noun}规则", "{noun}管理技术", "{noun}分配体系"
            ],
            TechDomain.MILITARY: [
                "{noun}战术", "{noun}武器制作", "改良{noun}战法", "{noun}防御技术", "{noun}攻击术"
            ],
        }
        
        # 名词库，用于动态生成技术名
        self._noun_lib = {
            TechDomain.AGRICULTURE: ["谷物", "蔬菜", "果树", "土壤", "灌溉", "肥料", "农具", "育种", "轮作", "梯田"],
            TechDomain.PRODUCTION: ["石器", "木器", "铜器", "铁器", "陶器", "工具", "武器", "衣物", "食物", "材料"],
            TechDomain.CONSTRUCTION: ["房屋", "城墙", "道路", "桥梁", "水利", "宫殿", "神庙", "住宅", "工场", "仓库"],
            TechDomain.ENERGY: ["火", "水力", "风力", "畜力", "煤炭", "石油", "蒸汽", "电力", "太阳能", "核能"],
            TechDomain.MEDICINE: ["草药", "外伤", "感冒", "发烧", "瘟疫", "外科", "内科", "针灸", "按摩", "药剂"],
            TechDomain.SOCIAL: ["氏族", "部落", "城邦", "国家", "法律", "货币", "税收", "教育", "宗教", "等级"],
            TechDomain.MILITARY: ["弓箭", "刀剑", "盔甲", "盾牌", "战车", "城墙", "战术", "阵法", "侦察", "防御"],
        }
        
        # 动词库
        self._verb_lib = ["原始", "基础", "高级", "改良", "新式", "传统", "高效", "节能", "生态", "复合"]

    def update(self, world: World, dt: float = 1.0) -> None:
        """旧版动态技术系统已弃用，技术掌握由人类个体主观能动性产生"""
        pass

    def _update_activity_and_problem_stats(self, world: World, dt: float) -> None:
        """统计人类活动和问题，更新统计数据"""
        # 统计活动
        for entity, (memory, inv) in world.get_components([MemoryComponent, InventoryComponent]):
            # 从记忆中提取最近的活动
            recent_events = memory.events[-10:] if len(memory.events) > 10 else memory.events
            for event in recent_events:
                event_type = event.get('type', '')
                if event_type in self.activity_stats:
                    self.activity_stats[event_type] += 1
        
        # 统计问题
        human_count = 0
        total_hunger = 0
        total_cold = 0
        total_disease = 0
        
        for entity, (human, health) in world.get_components([HumanComponent, KnowledgeComponent]):
            human_count += 1
            # 统计饥饿问题
            if hasattr(health, 'hunger') and health.hunger > 0.8:
                total_hunger += 1
            # 统计寒冷问题
            if hasattr(health, 'temperature') and health.temperature < 0.3:
                total_cold += 1
            # 统计疾病问题
            if hasattr(health, 'disease_count') and health.disease_count > 0:
                total_disease += 1
        
        # 更新问题统计
        if human_count > 0:
            if total_hunger / human_count > 0.3:
                self.problem_stats['food_shortage'] += 1
            if total_cold / human_count > 0.2:
                self.problem_stats['cold'] += 1
            if total_disease / human_count > 0.1:
                self.problem_stats['disease'] += 1

    def _try_invent_new_technology(self, world: World) -> None:
        """尝试根据当前活动和问题生成新技术"""
        # 计算基础发明概率，平均每个文明每1000步发明一个新技术
        base_prob = 0.05
        # 知识越多，发明概率越高
        total_knowledge = sum([len(world.get_component(e, KnowledgeComponent).knowledge) for e, _ in world.get_components(KnowledgeComponent)] or [0])
        base_prob += total_knowledge / 10000
        
        if self._rng.random() > base_prob:
            return
        
        # 确定最活跃的领域，优先发明相关技术
        activity_sorted = sorted(self.activity_stats.items(), key=lambda x: x[1], reverse=True)
        problem_sorted = sorted(self.problem_stats.items(), key=lambda x: x[1], reverse=True)
        
        top_activity = activity_sorted[0][0] if activity_sorted else 'gather_food'
        top_problem = problem_sorted[0][0] if problem_sorted else 'food_shortage'
        
        # 映射活动到技术领域
        activity_to_domain = {
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
        }
        
        problem_to_domain = {
            'food_shortage': TechDomain.AGRICULTURE,
            'cold': TechDomain.PRODUCTION,
            'disease': TechDomain.MEDICINE,
            'enemy_attack': TechDomain.MILITARY,
            'tool_break': TechDomain.PRODUCTION,
            'building_collapse': TechDomain.CONSTRUCTION,
            'water_shortage': TechDomain.AGRICULTURE,
        }
        
        # 70%概率基于最活跃的活动发明，30%概率基于最严重的问题发明
        if self._rng.random() < 0.7:
            target_domain = activity_to_domain.get(top_activity, TechDomain.PRODUCTION)
        else:
            target_domain = problem_to_domain.get(top_problem, TechDomain.PRODUCTION)
        
        # 生成动态技术
        new_tech = self._generate_technology(target_domain, world)
        if not new_tech:
            return
        
        # 选择最聪明的人类作为发明者
        inventors = []
        for entity, knowledge in world.get_components(KnowledgeComponent):
            inventors.append((entity, len(knowledge.knowledge)))
        
        if not inventors:
            return
        
        # 知识最多的人有更高概率发明
        inventors.sort(key=lambda x: x[1], reverse=True)
        inventor = self._rng.choices([x[0] for x in inventors], weights=[x[1] for x in inventors])[0]
        new_tech.inventor_id = inventor.id
        new_tech.invention_time = world.get_time()
        
        # 加入已发明技术
        tech_id = f"tech_{target_domain.name.lower()}_{len(self.discovered_technologies) + 1}"
        new_tech.tech_id = tech_id
        self.discovered_technologies[tech_id] = new_tech
        
        # 应用技术效果
        for effect in new_tech.effects:
            effect(world)
        
        logger.warning(
            f"[Technology] 人类发明了新技术：《{new_tech.name}》\n"
            f"描述：{new_tech.description}\n"
            f"领域：{target_domain.name}，等级：{new_tech.level}\n"
            f"发明者：E{inventor.id}"
        )
        
        # 发明者获得知识加成
        inv_knowledge = world.get_component(inventor, KnowledgeComponent)
        if inv_knowledge:
            inv_knowledge.add_knowledge(f"invented_{tech_id}", value=10.0)

    def _generate_technology(self, domain: TechDomain, world: World) -> Optional[DynamicTechnology]:
        """动态生成指定领域的新技术"""
        # 生成技术名称
        template = self._rng.choice(self._name_templates.get(domain, ["{noun}技术"]))
        noun = self._rng.choice(self._noun_lib.get(domain, ["未知"]))
        verb = self._rng.choice(self._verb_lib)
        tech_name = template.format(verb=verb, noun=noun)
        
        # 生成技术描述
        desc_templates = [
            "通过长期实践总结出的{noun}{domain}方法，效率提升{effect:.0f}%。",
            "发明者经过反复试验开发出的新式{noun}{domain}技术，解决了{problem}问题。",
            "传承自古老经验的{verb}{noun}工艺，让{domain}水平大幅提升。",
            "革命性的{verb}{noun}发明，彻底改变了{domain}的生产方式。"
        ]
        effect_value = self._rng.uniform(10, 50)
        problem_map = {
            TechDomain.AGRICULTURE: "粮食短缺",
            TechDomain.PRODUCTION: "工具不足",
            TechDomain.CONSTRUCTION: "建筑易坏",
            TechDomain.ENERGY: "能源不足",
            TechDomain.MEDICINE: "疾病肆虐",
            TechDomain.SOCIAL: "社会混乱",
            TechDomain.MILITARY: "易受攻击",
        }
        tech_desc = self._rng.choice(desc_templates).format(
            noun=noun, verb=verb, domain=domain.name.lower(), 
            effect=effect_value, problem=problem_map.get(domain, "实际")
        )
        
        # 生成技术等级，基于已有的同领域技术数量
        existing_domain_techs = len([t for t in self.discovered_technologies.values() if t.domain == domain])
        tech_level = existing_domain_techs + 1
        
        # 生成动态效果
        effects = []
        effect_params = {}
        
        # 不同领域生成不同效果
        if domain == TechDomain.AGRICULTURE:
            # 农业技术：提升作物产量，减少粮食短缺
            effect_params['crop_yield_bonus'] = effect_value / 100
            def agriculture_effect(w: World):
                # 应用到所有植物生长系统
                plant_system = w.get_system("PlantGrowthSystem")
                if plant_system:
                    plant_system.growth_rate_multiplier *= (1 + effect_value / 100)
            effects.append(agriculture_effect)
        
        elif domain == TechDomain.PRODUCTION:
            # 生产技术：提升工具耐久，生产效率
            effect_params['production_efficiency_bonus'] = effect_value / 100
            def production_effect(w: World):
                # 应用到资源采集系统
                gather_system = w.get_system("ResourceGatheringSystem")
                if gather_system:
                    gather_system.gathering_efficiency *= (1 + effect_value / 100)
            effects.append(production_effect)
        
        elif domain == TechDomain.CONSTRUCTION:
            # 建筑技术：提升建筑耐久，建造速度
            effect_params['building_durability_bonus'] = effect_value / 100
            def construction_effect(w: World):
                # 应用到建造系统
                build_system = w.get_system("ConstructionSystem")
                if build_system:
                    build_system.build_speed_multiplier *= (1 + effect_value / 100)
            effects.append(construction_effect)
        
        elif domain == TechDomain.MEDICINE:
            # 医学技术：提升平均寿命，减少疾病死亡率
            effect_params['heal_efficiency_bonus'] = effect_value / 100
            def medicine_effect(w: World):
                # 应用到医疗系统
                health_system = w.get_system("HealthcareSystem")
                if health_system:
                    health_system.heal_success_rate *= (1 + effect_value / 100)
            effects.append(medicine_effect)
        
        elif domain == TechDomain.MILITARY:
            # 军事技术：提升战斗力，防御能力
            effect_params['combat_damage_bonus'] = effect_value / 100
            def military_effect(w: World):
                # 应用到战斗系统
                combat_system = w.get_system("CombatSystem")
                if combat_system:
                    combat_system.attack_damage_multiplier *= (1 + effect_value / 100)
            effects.append(military_effect)
        
        elif domain == TechDomain.SOCIAL:
            # 社会技术：提升社会稳定度，组织能力
            effect_params['social_stability_bonus'] = effect_value / 100
            def social_effect(w: World):
                # 应用到社会系统
                social_system = w.get_system("SocialSystem")
                if social_system:
                    social_system.stability_multiplier *= (1 + effect_value / 100)
            effects.append(social_effect)
        
        if not effects:
            return None
        
        # 生成前置条件
        prerequisites = {}
        if existing_domain_techs > 0:
            # 需要有同领域的前置技术
            prerequisites[f"domain_{domain.name.lower()}_level"] = existing_domain_techs
        
        # 创建技术对象
        return DynamicTechnology(
            tech_id="",  # 后续填充
            name=tech_name,
            description=tech_desc,
            domain=domain,
            level=tech_level,
            effects=effects,
            prerequisites=prerequisites,
            effect_params=effect_params
        )

# 兼容旧版API：对外导出TechnologySystem别名
TechnologySystem = DynamicTechnologySystem

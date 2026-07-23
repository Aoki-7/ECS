#!/usr/bin/env python3
"""
文化演化系统 v4.16.0
处理文化的自然演化、价值观变迁、传统兴衰与文化传播
"""

import random
import logging
from typing import Tuple, Dict

from core.system import System
from core.world import World
from core.entity import Entity
from civilization.components.civilization_component import CivilizationComponent
from civilization.components.culture_component import CultureComponent, CulturalValue, CulturalNorm, CulturalTradition
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class CultureEvolutionSystem(System):
    """
    文化演化系统
    处理文化的动态变化、传播与演化
    """

    tick_interval = 100  # 每100tick执行一次（文化是慢变化系统）
    priority = 160  # 在特质系统之后运行

    # 演化配置
    VALUE_CHANGE_RATE = 0.02  # 每轮价值观最大变化幅度
    TRADITION_GENERATION_CHANCE = 0.1  # 每轮生成新传统的概率
    NORM_GENERATION_CHANCE = 0.15  # 每轮生成新规范的概率
    TABOO_GENERATION_CHANCE = 0.05  # 每轮生成新禁忌的概率
    CULTURE_SPREAD_RADIUS = 5.0  # 文化传播半径
    CULTURE_SPREAD_CHANCE = 0.2  # 文化传播概率

    def update(self, world: World, dt: float):
        # 遍历所有文明的文化组件
        all_cultures = list(world.query(CivilizationComponent, CultureComponent, SpaceComponent))
        
        for entity, civ, culture, space in all_cultures:
            # 内部演化
            self._internal_evolution(civ, culture, dt)
            
            # 与其他文明的文化交互
            for other_entity, other_civ, other_culture, other_space in all_cultures:
                if entity == other_entity:
                    continue
                # 距离足够近则尝试文化传播
                distance = ((space.x - other_space.x)**2 + (space.y - other_space.y)**2)**0.5
                if distance <= self.CULTURE_SPREAD_RADIUS:
                    self._cultural_interaction(culture, other_culture, distance)
    
    def _internal_evolution(self, civ: CivilizationComponent, culture: CultureComponent, dt: float) -> None:
        """处理文化内部自然演化"""
        # 1. 价值观自然漂移
        self._drift_values(culture)
        
        # 2. 尝试生成新的文化规范
        if random.random() < self.NORM_GENERATION_CHANCE * culture.cultural_diversity:
            self._generate_new_norm(culture)
        
        # 3. 尝试生成新的传统
        if random.random() < self.TRADITION_GENERATION_CHANCE * culture.cultural_diversity:
            self._generate_new_tradition(culture)
        
        # 4. 尝试生成新的禁忌
        if random.random() < self.TABOO_GENERATION_CHANCE * culture.values.get(CulturalValue.TRADITION, 0.5):
            self._generate_new_taboo(culture)
        
        # 5. 清理过时的规范/传统
        self._cleanup_outdated_elements(culture)
        
        # 6. 文化资本自然增长
        culture.update_cultural_capital(civ.population * 0.1)
    
    def _drift_values(self, culture: CultureComponent) -> None:
        """价值观自然漂移"""
        for value in CulturalValue:
            # 漂移幅度与文化多样性、演化速率正相关
            drift = random.uniform(-self.VALUE_CHANGE_RATE, self.VALUE_CHANGE_RATE)
            drift *= culture.cultural_diversity * culture.evolution_rate
            
            # 传统价值观漂移更慢
            if value == CulturalValue.TRADITION:
                drift *= (1 - culture.values[value])
            
            new_val = max(0.0, min(1.0, culture.values[value] + drift))
            culture.values[value] = new_val
    
    def _generate_new_norm(self, culture: CultureComponent) -> None:
        """生成新的文化规范"""
        norm_templates = [
            {
                "name": "按劳分配",
                "description": "根据劳动贡献分配资源",
                "effect": "生产效率+10%，社会冲突-5%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.INDIVIDUALISM] > 0.6
            },
            {
                "name": "平均分配",
                "description": "资源平均分配给所有成员",
                "effect": "社会凝聚力+15%，生产效率-5%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.INDIVIDUALISM] < 0.4
            },
            {
                "name": "尊老传统",
                "description": "尊重老年人，优先分配资源给长者",
                "effect": "知识传承+20%，社会稳定性+10%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.TRADITION] > 0.6
            },
            {
                "name": "尚武精神",
                "description": "崇尚武力，鼓励参军",
                "effect": "战斗能力+15%，生产效率-5%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.ASSERTIVENESS] > 0.6
            },
            {
                "name": "重农抑商",
                "description": "重视农业生产，抑制商业活动",
                "effect": "农业产量+20%，商业收入-30%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.LONG_TERM_ORIENTATION] > 0.6
            },
            {
                "name": "鼓励创新",
                "description": "鼓励新技术研发和创新",
                "effect": "科技研发速度+20%，社会稳定性-5%",
                "strength": random.uniform(0.3, 0.7),
                "acceptance": random.uniform(0.5, 0.9),
                "condition": lambda c: c.values[CulturalValue.TRADITION] < 0.4
            },
        ]
        
        # 筛选符合当前价值观的规范
        available_norms = [t for t in norm_templates if t["condition"](culture)]
        if not available_norms:
            return
        
        # 随机选一个添加
        selected = random.choice(available_norms)
        new_norm = CulturalNorm(
            name=selected["name"],
            description=selected["description"],
            effect=selected["effect"],
            strength=selected["strength"],
            acceptance=selected["acceptance"]
        )
        culture.add_norm(new_norm)
        logger.info(f"[CultureEvolution] 文明生成新规范：{new_norm.name}")
    
    def _generate_new_tradition(self, culture: CultureComponent) -> None:
        """生成新的文化传统"""
        tradition_templates = [
            {
                "name": "丰收节",
                "type": "节日",
                "frequency": 8760,  # 每年一次
                "effect": {"social_stability": 0.2, "food_consumption_rate": 0.5},
                "condition": lambda c: True
            },
            {
                "name": "祭祀仪式",
                "type": "仪式",
                "frequency": 2190,  # 每季度一次
                "effect": {"cultural_capital": 50, "social_cohesion": 0.15},
                "condition": lambda c: c.values[CulturalValue.TRADITION] > 0.5
            },
            {
                "name": "成年礼",
                "type": "习俗",
                "frequency": 720,  # 每月一次
                "effect": {"young_morale": 0.3, "skill_transfer": 0.2},
                "condition": lambda c: True
            },
            {
                "name": "战争庆典",
                "type": "节日",
                "frequency": 4380,  # 每半年一次
                "effect": {"combat_bonus": 0.2, "war_support": 0.3},
                "condition": lambda c: c.values[CulturalValue.ASSERTIVENESS] > 0.6
            },
            {
                "name": "知识竞赛",
                "type": "活动",
                "frequency": 1440,  # 每两月一次
                "effect": {"tech_point_gain": 0.2, "literacy_rate": 0.1},
                "condition": lambda c: c.values[CulturalValue.LONG_TERM_ORIENTATION] > 0.5
            },
        ]
        
        available_traditions = [t for t in tradition_templates if t["condition"](culture)]
        if not available_traditions:
            return
        
        selected = random.choice(available_traditions)
        new_tradition = CulturalTradition(
            name=selected["name"],
            type=selected["type"],
            frequency=selected["frequency"],
            effect=selected["effect"]
        )
        culture.add_tradition(new_tradition)
        logger.info(f"[CultureEvolution] 文明生成新传统：{new_tradition.name}")
    
    def _generate_new_taboo(self, culture: CultureComponent) -> None:
        """生成新的文化禁忌"""
        taboo_templates = [
            "浪费食物",
            "亵渎神灵",
            "以下犯上",
            "通奸",
            "盗窃",
            "背叛族群",
            "食用禁忌食物",
            "在神圣场所喧哗",
        ]
        
        new_taboo = random.choice(taboo_templates)
        if new_taboo not in culture.taboos:
            culture.add_taboos(new_taboo)
            logger.info(f"[CultureEvolution] 文明生成新禁忌：{new_taboo}")
    
    def _cleanup_outdated_elements(self, culture: CultureComponent) -> None:
        """清理过时的规范和传统"""
        # 清理接受度过低的规范
        culture.norms = [n for n in culture.norms if n.acceptance >= 0.2]
        
        # 清理强度过低的传统
        for tradition in culture.traditions[:]:
            # 传统随时间自然衰减强度
            if random.random() < 0.05:
                culture.remove_tradition(tradition.name)
        
        # 清理过时的禁忌（低传统社会禁忌更少）
        if culture.values[CulturalValue.TRADITION] < 0.3 and len(culture.taboos) > 3:
            remove_count = random.randint(1, 2)
            for _ in range(remove_count):
                if culture.taboos:
                    culture.taboos.pop()
    
    def _cultural_interaction(self, culture_a: CultureComponent, culture_b: CultureComponent, distance: float) -> None:
        """处理两个文明之间的文化交互与传播"""
        # 文化影响力差距
        influence_diff = culture_a.cultural_influence - culture_b.cultural_influence
        spread_chance = self.CULTURE_SPREAD_CHANCE * (1 + influence_diff * 0.5) * (1 - distance / self.CULTURE_SPREAD_RADIUS)
        
        if random.random() < spread_chance:
            # A的文化传播到B
            self._spread_culture(culture_a, culture_b)
        elif random.random() < spread_chance:
            # B的文化传播到A
            self._spread_culture(culture_b, culture_a)
    
    def _spread_culture(self, source_culture: CultureComponent, target_culture: CultureComponent) -> None:
        """文化从源文明传播到目标文明"""
        # 只有目标文化接受度足够高才会传播
        if random.random() > target_culture.foreign_culture_acceptance:
            return
        
        # 1. 价值观融合
        for value in CulturalValue:
            if random.random() < 0.3:  # 30%概率融合该维度
                diff = source_culture.values[value] - target_culture.values[value]
                target_culture.values[value] += diff * 0.1  # 融合10%的差异
                target_culture.values[value] = max(0.0, min(1.0, target_culture.values[value]))
        
        # 2. 传播规范
        if source_culture.norms and random.random() < 0.2:
            selected_norm = random.choice(source_culture.norms)
            # 检查目标是否已有该规范
            if not any(n.name == selected_norm.name for n in target_culture.norms):
                new_norm = CulturalNorm(
                    name=selected_norm.name,
                    description=selected_norm.description,
                    effect=selected_norm.effect,
                    strength=selected_norm.strength * 0.7,
                    acceptance=selected_norm.acceptance * 0.6
                )
                target_culture.add_norm(new_norm)
                logger.info(f"[CultureEvolution] 规范{new_norm.name}传播到目标文明")
        
        # 3. 传播传统
        if source_culture.traditions and random.random() < 0.1:
            selected_tradition = random.choice(source_culture.traditions)
            if not any(t.name == selected_tradition.name for t in target_culture.traditions):
                new_tradition = CulturalTradition(
                    name=selected_tradition.name,
                    type=selected_tradition.type,
                    frequency=selected_tradition.frequency,
                    effect=selected_tradition.effect.copy()
                )
                target_culture.add_tradition(new_tradition)
                logger.info(f"[CultureEvolution] 传统{new_tradition.name}传播到目标文明")
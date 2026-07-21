#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
文明特质组件 v4.16.0
定义不同文明的独特特性，提供差异化发展路径
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from core.component import Component
from typing import Dict, List, Set, Callable


class CivilizationTraitType(Enum):
    """文明特质类型"""
    # 生产类
    AGRICULTURAL_EXPERT = auto()      # 农业专家：作物产量+30%，生长速度+20%
    HUNTING_MASTER = auto()           # 狩猎大师：狩猎成功率+40%，动物掉落+25%
    MINING_PROFICIENT = auto()        # 采矿能手：矿石产出+35%，开采速度+30%
    CRAFTSMAN_SPIRIT = auto()         # 工匠精神：工具耐久+50%，制成品品质+25%
    
    # 社会类
    HIGH_FERTILITY = auto()           # 高生育率：怀孕概率+40%，生育间隔-30%
    SOCIAL_COHESION = auto()          # 社会凝聚力：内部冲突概率-60%，关系提升速度+50%
    KNOWLEDGE_SHARING = auto()        # 知识共享：科技研发速度+40%，技能传承效率+50%
    PEACE_LOVING = auto()             # 爱好和平：对外战争概率-70%，外交关系+30%
    
    # 生存类
    HARDY_CONSTITUTION = auto()       # 强健体质：疾病抵抗+50%，恶劣环境耐受+40%
    ADAPTABLE = auto()                # 适应性强：任何地形移动成本-30%，资源获取阈值-25%
    NIGHT_VISION = auto()             # 夜视能力：夜间活动效率+70%，夜间视野+50%
    RATIONING_EXPERT = auto()         # 配给专家：食物/水消耗速率-30%，资源存储上限+40%
    
    # 军事类
    WARRIOR_CULTURE = auto()          # 战士文化：战斗能力+50%，武器伤害+30%
    RAIDING_TRADITION = auto()        # 劫掠传统：战利品获取+60%，敌方资源掠夺+40%
    DEFENSIVE_EXPERT = auto()         # 防御专家：建筑耐久+100%，防御战伤害减免+50%
    NAVAL_MASTERY = auto()            # 航海精通：水上移动速度+100%，水上战斗+70%
    
    # 特殊类
    ANIMAL_FRIEND = auto()            # 动物之友：野生动物不会主动攻击，驯养成功率+80%
    LUCKY = auto()                    # 幸运：所有概率事件正面结果权重+30%
    SCHOLARLY = auto()                # 尚学：科技点获取+60%，识字率+100%
    TRADITIONAL = auto()              # 传统：文化传承速度+80%，社会稳定性+50%，科技研发速度-20%


@dataclass(slots=True)
class TraitEffect:
    """特质效果"""
    target_attribute: str             # 影响的属性名
    effect_type: str = "add"          # 效果类型：add（加值）/multiply（乘算）/override（覆盖）
    value: float = 0.0                # 效果值
    condition: Callable = None        # 生效条件（可选）


@dataclass(slots=True)
class CivilizationTraitComponent(Component):
    """
    文明特质组件
    每个文明实体挂载此组件，存储其拥有的所有特质及效果
    """
    
    # 文明拥有的特质列表
    traits: Set[CivilizationTraitType] = field(default_factory=set)
    
    # 特质效果缓存（自动计算）
    _effect_cache: Dict[str, List[TraitEffect]] = field(default_factory=dict, init=False)
    
    def add_trait(self, trait: CivilizationTraitType) -> None:
        """添加文明特质"""
        if trait not in self.traits:
            self.traits.add(trait)
            self._rebuild_effect_cache()
    
    def remove_trait(self, trait: CivilizationTraitType) -> None:
        """移除文明特质"""
        if trait in self.traits:
            self.traits.remove(trait)
            self._rebuild_effect_cache()
    
    def has_trait(self, trait: CivilizationTraitType) -> bool:
        """检查是否拥有指定特质"""
        return trait in self.traits
    
    def get_attribute_modifier(self, attribute: str, base_value: float) -> float:
        """获取属性经过所有特质修正后的值"""
        if attribute not in self._effect_cache:
            return base_value
        
        current_value = base_value
        add_values = []
        multiply_values = []
        override_value = None
        
        for effect in self._effect_cache[attribute]:
            if effect.condition is not None and not effect.condition():
                continue
                
            if effect.effect_type == "add":
                add_values.append(effect.value)
            elif effect.effect_type == "multiply":
                multiply_values.append(effect.value)
            elif effect.effect_type == "override":
                override_value = effect.value
        
        # 应用效果：先覆盖 → 再加值 → 再乘算
        if override_value is not None:
            current_value = override_value
        
        for add_val in add_values:
            current_value += add_val
        
        for multiply_val in multiply_values:
            current_value *= (1 + multiply_val)
        
        return max(0.0, current_value)
    
    def _rebuild_effect_cache(self) -> None:
        """重建特质效果缓存"""
        self._effect_cache.clear()
        
        # 定义所有特质的效果
        trait_effect_map = {
            # 生产类
            CivilizationTraitType.AGRICULTURAL_EXPERT: [
                TraitEffect("crop_yield", "multiply", 0.3),
                TraitEffect("crop_growth_speed", "multiply", 0.2),
            ],
            CivilizationTraitType.HUNTING_MASTER: [
                TraitEffect("hunting_success_rate", "multiply", 0.4),
                TraitEffect("animal_drop_amount", "multiply", 0.25),
            ],
            CivilizationTraitType.MINING_PROFICIENT: [
                TraitEffect("ore_yield", "multiply", 0.35),
                TraitEffect("mining_speed", "multiply", 0.3),
            ],
            CivilizationTraitType.CRAFTSMAN_SPIRIT: [
                TraitEffect("tool_durability", "multiply", 0.5),
                TraitEffect("craft_quality", "multiply", 0.25),
            ],
            
            # 社会类
            CivilizationTraitType.HIGH_FERTILITY: [
                TraitEffect("pregnancy_chance", "multiply", 0.4),
                TraitEffect("birth_interval", "multiply", -0.3),
            ],
            CivilizationTraitType.SOCIAL_COHESION: [
                TraitEffect("internal_conflict_chance", "multiply", -0.6),
                TraitEffect("relationship_gain_speed", "multiply", 0.5),
            ],
            CivilizationTraitType.KNOWLEDGE_SHARING: [
                TraitEffect("tech_research_speed", "multiply", 0.4),
                TraitEffect("skill_transfer_efficiency", "multiply", 0.5),
            ],
            CivilizationTraitType.PEACE_LOVING: [
                TraitEffect("war_declare_chance", "multiply", -0.7),
                TraitEffect("diplomacy_relation_bonus", "add", 0.3),
            ],
            
            # 生存类
            CivilizationTraitType.HARDY_CONSTITUTION: [
                TraitEffect("disease_resistance", "multiply", 0.5),
                TraitEffect("extreme_environment_tolerance", "multiply", 0.4),
            ],
            CivilizationTraitType.ADAPTABLE: [
                TraitEffect("terrain_movement_cost", "multiply", -0.3),
                TraitEffect("resource_collection_threshold", "multiply", -0.25),
            ],
            CivilizationTraitType.NIGHT_VISION: [
                TraitEffect("night_activity_efficiency", "multiply", 0.7),
                TraitEffect("night_vision_range", "multiply", 0.5),
            ],
            CivilizationTraitType.RATIONING_EXPERT: [
                TraitEffect("food_consumption_rate", "multiply", -0.3),
                TraitEffect("water_consumption_rate", "multiply", -0.3),
                TraitEffect("resource_storage_capacity", "multiply", 0.4),
            ],
            
            # 军事类
            CivilizationTraitType.WARRIOR_CULTURE: [
                TraitEffect("combat_ability", "multiply", 0.5),
                TraitEffect("weapon_damage", "multiply", 0.3),
            ],
            CivilizationTraitType.RAIDING_TRADITION: [
                TraitEffect("loot_amount", "multiply", 0.6),
                TraitEffect("resource_raid_amount", "multiply", 0.4),
            ],
            CivilizationTraitType.DEFENSIVE_EXPERT: [
                TraitEffect("building_durability", "multiply", 1.0),
                TraitEffect("defensive_combat_damage_reduction", "multiply", 0.5),
            ],
            CivilizationTraitType.NAVAL_MASTERY: [
                TraitEffect("water_movement_speed", "multiply", 1.0),
                TraitEffect("water_combat_bonus", "multiply", 0.7),
            ],
            
            # 特殊类
            CivilizationTraitType.ANIMAL_FRIEND: [
                TraitEffect("wild_animal_attack_chance", "override", 0.0),
                TraitEffect("animal_taming_success_rate", "multiply", 0.8),
            ],
            CivilizationTraitType.LUCKY: [
                TraitEffect("positive_event_weight", "multiply", 0.3),
            ],
            CivilizationTraitType.SCHOLARLY: [
                TraitEffect("tech_point_gain", "multiply", 0.6),
                TraitEffect("literacy_rate", "override", 1.0),
            ],
            CivilizationTraitType.TRADITIONAL: [
                TraitEffect("cultural_transmission_speed", "multiply", 0.8),
                TraitEffect("social_stability", "multiply", 0.5),
                TraitEffect("tech_research_speed", "multiply", -0.2),
            ],
        }
        
        # 构建缓存
        for trait in self.traits:
            if trait not in trait_effect_map:
                continue
            for effect in trait_effect_map[trait]:
                if effect.target_attribute not in self._effect_cache:
                    self._effect_cache[effect.target_attribute] = []
                self._effect_cache[effect.target_attribute].append(effect)

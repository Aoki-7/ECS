#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:health_component.py
@说明:健康组件 v3.0 - 细化版
@时间:2026/07/19
@版本:3.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto

from core.component import Component


class BodyPart(Enum):
    """身体部位"""
    HEAD = auto()       # 头部
    TORSO = auto()      # 躯干
    LEFT_ARM = auto()   # 左臂
    RIGHT_ARM = auto()  # 右臂
    LEFT_LEG = auto()   # 左腿
    RIGHT_LEG = auto()  # 右腿
    HEART = auto()      # 心脏
    LUNGS = auto()      # 肺
    LIVER = auto()      # 肝
    KIDNEYS = auto()    # 肾
    STOMACH = auto()    # 胃
    BRAIN = auto()      # 脑


class DiseaseType(Enum):
    """疾病类型"""
    COMMON_COLD = auto()    # 感冒
    FLU = auto()            # 流感
    INFECTION = auto()      # 感染
    FEVER = auto()          # 发烧
    CHRONIC = auto()        # 慢性病
    PARASITE = auto()       # 寄生虫
    VIRUS = auto()          # 病毒
    BACTERIA = auto()       # 细菌


class InjuryType(Enum):
    """伤害类型"""
    BRUISE = auto()         # 瘀伤
    CUT = auto()            # 割伤
    FRACTURE = auto()       # 骨折
    BURN = auto()           # 烧伤
    INTERNAL = auto()       # 内伤
    SPRAIN = auto()         # 扭伤
    CONCUSSION = auto()     # 脑震荡


class TreatmentType(Enum):
    """治疗类型"""
    REST = auto()           # 休息
    MEDICINE = auto()       # 药物
    SURGERY = auto()        # 手术
    BANDAGE = auto()        # 绷带
    HERBAL = auto()         # 草药
    NATURAL = auto()        # 自然恢复


@dataclass(slots=True)
class BodyPartHealth:
    """身体部位健康"""
    part: BodyPart
    health: float = 1.0         # 健康度 (0-1)
    injury_level: float = 0.0   # 伤害程度 (0-1)
    disease_level: float = 0.0  # 疾病程度 (0-1)
    pain_level: float = 0.0     # 疼痛程度 (0-1)
    function_level: float = 1.0  # 功能水平 (0-1)
    
    def get_overall_health(self) -> float:
        """获取整体健康度"""
        return (self.health + (1.0 - self.injury_level) + 
                (1.0 - self.disease_level) + self.function_level) / 4.0


@dataclass(slots=True)
class Disease:
    """疾病"""
    disease_id: int
    disease_type: DiseaseType
    name: str
    severity: float = 0.0       # 严重程度 (0-1)
    contagious: bool = False     # 是否传染
    curable: bool = True         # 是否可治愈
    symptoms: List[str] = field(default_factory=list)  # 症状
    affected_parts: List[BodyPart] = field(default_factory=list)  # 受影响部位
    treatment: Optional[TreatmentType] = None  # 治疗方法
    recovery_time: float = 0.0   # 恢复时间（小时）
    immunity_duration: float = 0.0  # 免疫持续时间（小时）
    
    def get_contagion_risk(self) -> float:
        """获取传染风险"""
        if not self.contagious:
            return 0.0
        return self.severity * 0.5


@dataclass(slots=True)
class Injury:
    """伤害"""
    injury_id: int
    injury_type: InjuryType
    body_part: BodyPart
    severity: float = 0.0       # 严重程度 (0-1)
    pain_level: float = 0.0     # 疼痛程度 (0-1)
    bleeding: bool = False       # 是否出血
    infected: bool = False       # 是否感染
    healing_progress: float = 0.0  # 愈合进度 (0-1)
    treatment: Optional[TreatmentType] = None  # 治疗方法
    healing_time: float = 0.0    # 愈合时间（小时）
    
    def get_healing_rate(self) -> float:
        """获取愈合速率"""
        base_rate = 0.1
        if self.treatment == TreatmentType.BANDAGE:
            base_rate *= 1.5
        elif self.treatment == TreatmentType.MEDICINE:
            base_rate *= 2.0
        elif self.treatment == TreatmentType.SURGERY:
            base_rate *= 3.0
        
        if self.infected:
            base_rate *= 0.5
        
        return base_rate


@dataclass(slots=True)
class HealthComponent(Component):
    """
    健康组件 v3.0 - 细化版
    存储健康状态，包括身体部位健康、疾病、伤害、治疗等细化功能。
    """
    
    # === 整体健康 ===
    overall_health: float = 1.0     # 整体健康度 (0-1)
    max_health: float = 100.0       # 最大健康值
    current_health: float = 100.0   # 当前健康值
    
    # === 身体部位健康 ===
    body_parts: Dict[BodyPart, BodyPartHealth] = field(default_factory=dict)
    
    # === 疾病 ===
    diseases: Dict[int, Disease] = field(default_factory=dict)
    next_disease_id: int = 0
    disease_immunity: Dict[DiseaseType, float] = field(default_factory=dict)  # 疾病免疫
    
    # === 伤害 ===
    injuries: Dict[int, Injury] = field(default_factory=dict)
    next_injury_id: int = 0
    
    # === 免疫系统 ===
    innate_immunity: float = 0.5        # 先天免疫 (0-1)
    acquired_immunity: float = 0.5      # 获得性免疫 (0-1)
    immune_response: float = 0.5        # 免疫反应 (0-1)
    
    # === 治疗 ===
    active_treatments: List[TreatmentType] = field(default_factory=list)  # 正在进行的治疗
    treatment_effectiveness: float = 1.0  # 治疗效果 (0-1)
    
    # === 健康历史 ===
    health_history: List[Dict] = field(default_factory=list)  # 健康历史记录
    max_history_length: int = 100
    
    def __post_init__(self):
        """初始化身体部位"""
        if not self.body_parts:
            for part in BodyPart:
                self.body_parts[part] = BodyPartHealth(part=part)
    
    def get_overall_health_score(self) -> float:
        """获取整体健康评分 (0-1)"""
        if not self.body_parts:
            return self.overall_health
        
        total_health = sum(part.get_overall_health() for part in self.body_parts.values())
        return total_health / len(self.body_parts)
    
    def get_health_status(self) -> str:
        """获取健康状态描述"""
        health_score = self.get_overall_health_score()
        
        if health_score < 0.3:
            return "危重"
        elif health_score < 0.5:
            return "虚弱"
        elif health_score < 0.7:
            return "一般"
        elif health_score < 0.9:
            return "良好"
        else:
            return "优秀"
    
    def add_disease(self, disease_type: DiseaseType, name: str, 
                    severity: float = 0.5, symptoms: List[str] = None,
                    affected_parts: List[BodyPart] = None) -> int:
        """添加疾病"""
        disease_id = self.next_disease_id
        self.next_disease_id += 1
        
        disease = Disease(
            disease_id=disease_id,
            disease_type=disease_type,
            name=name,
            severity=severity,
            symptoms=symptoms or [],
            affected_parts=affected_parts or []
        )
        
        self.diseases[disease_id] = disease
        
        # 影响身体部位
        for part in disease.affected_parts:
            if part in self.body_parts:
                self.body_parts[part].disease_level = min(1.0, 
                    self.body_parts[part].disease_level + severity)
        
        # 记录健康历史
        self._record_health_event("disease", f"感染疾病: {name}")
        
        return disease_id
    
    def add_injury(self, injury_type: InjuryType, body_part: BodyPart,
                   severity: float = 0.5, pain_level: float = 0.5) -> int:
        """添加伤害"""
        injury_id = self.next_injury_id
        self.next_injury_id += 1
        
        injury = Injury(
            injury_id=injury_id,
            injury_type=injury_type,
            body_part=body_part,
            severity=severity,
            pain_level=pain_level
        )
        
        self.injuries[injury_id] = injury
        
        # 影响身体部位
        if body_part in self.body_parts:
            self.body_parts[body_part].injury_level = min(1.0,
                self.body_parts[body_part].injury_level + severity)
            self.body_parts[body_part].pain_level = min(1.0,
                self.body_parts[body_part].pain_level + pain_level)
        
        # 记录健康历史
        self._record_health_event("injury", f"受伤: {injury_type.name} at {body_part.name}")
        
        return injury_id
    
    def apply_treatment(self, treatment: TreatmentType, target_id: Optional[int] = None):
        """应用治疗"""
        if treatment not in self.active_treatments:
            self.active_treatments.append(treatment)
        
        # 如果是针对特定伤害或疾病的治疗
        if target_id is not None:
            if target_id in self.injuries:
                self.injuries[target_id].treatment = treatment
            elif target_id in self.diseases:
                self.diseases[target_id].treatment = treatment
        
        # 记录健康历史
        self._record_health_event("treatment", f"接受治疗: {treatment.name}")
    
    def update_health(self, dt: float):
        """更新健康状态"""
        # 更新疾病
        diseases_to_remove = []
        for disease_id, disease in self.diseases.items():
            # 疾病自然恢复
            if disease.curable:
                disease.severity = max(0.0, disease.severity - 0.01 * dt)
                if disease.severity <= 0.0:
                    diseases_to_remove.append(disease_id)
                    # 获得免疫
                    self.disease_immunity[disease.disease_type] = disease.immunity_duration
        
        # 移除已治愈的疾病
        for disease_id in diseases_to_remove:
            del self.diseases[disease_id]
        
        # 更新伤害
        injuries_to_remove = []
        for injury_id, injury in self.injuries.items():
            # 伤害愈合
            healing_rate = injury.get_healing_rate()
            injury.healing_progress = min(1.0, injury.healing_progress + healing_rate * dt)
            
            if injury.healing_progress >= 1.0:
                injuries_to_remove.append(injury_id)
                # 恢复身体部位健康
                if injury.body_part in self.body_parts:
                    self.body_parts[injury.body_part].injury_level = max(0.0,
                        self.body_parts[injury.body_part].injury_level - injury.severity)
                    self.body_parts[injury.body_part].pain_level = max(0.0,
                        self.body_parts[injury.body_part].pain_level - injury.pain_level)
        
        # 移除已愈合的伤害
        for injury_id in injuries_to_remove:
            del self.injuries[injury_id]
        
        # 更新身体部位健康
        for part in self.body_parts.values():
            # 自然恢复
            part.health = min(1.0, part.health + 0.01 * dt)
            part.disease_level = max(0.0, part.disease_level - 0.005 * dt)
            part.injury_level = max(0.0, part.injury_level - 0.005 * dt)
            part.pain_level = max(0.0, part.pain_level - 0.01 * dt)
            
            # 更新功能水平
            part.function_level = part.health * (1.0 - part.injury_level) * (1.0 - part.disease_level)
        
        # 更新整体健康
        self.overall_health = self.get_overall_health_score()
        self.current_health = self.max_health * self.overall_health
        
        # 更新免疫系统
        self._update_immune_system(dt)
    
    def _update_immune_system(self, dt: float):
        """更新免疫系统"""
        # 先天免疫自然波动
        self.innate_immunity = max(0.0, min(1.0, 
            self.innate_immunity + (0.5 - self.innate_immunity) * 0.01 * dt))
        
        # 获得性免疫根据疾病历史增长
        if self.diseases:
            self.acquired_immunity = min(1.0, self.acquired_immunity + 0.005 * dt)
        
        # 免疫反应根据当前疾病状态
        if self.diseases:
            self.immune_response = min(1.0, self.immune_response + 0.1 * dt)
        else:
            self.immune_response = max(0.5, self.immune_response - 0.01 * dt)
    
    def _record_health_event(self, event_type: str, description: str):
        """记录健康事件"""
        event = {
            'type': event_type,
            'description': description,
            'timestamp': 0.0  # 实际应用中应该使用真实时间戳
        }
        
        self.health_history.append(event)
        
        # 限制历史记录长度
        if len(self.health_history) > self.max_history_length:
            self.health_history = self.health_history[-self.max_history_length:]
    
    def get_disease_risk(self, disease_type: DiseaseType) -> float:
        """获取感染某种疾病的风险"""
        # 基础风险
        base_risk = 0.1
        
        # 免疫影响
        if disease_type in self.disease_immunity:
            immunity = self.disease_immunity[disease_type]
            if immunity > 0:
                return base_risk * 0.1  # 有免疫力，风险大大降低
        
        # 整体健康影响
        health_factor = 1.0 - self.overall_health
        
        # 免疫系统影响
        immune_factor = 1.0 - (self.innate_immunity + self.acquired_immunity) / 2.0
        
        return base_risk * health_factor * immune_factor
    
    def get_injury_risk(self, injury_type: InjuryType, body_part: BodyPart) -> float:
        """获取受伤风险"""
        # 基础风险
        base_risk = 0.1
        
        # 身体部位健康影响
        if body_part in self.body_parts:
            part_health = self.body_parts[body_part].get_overall_health()
            health_factor = 1.0 - part_health
        else:
            health_factor = 0.5
        
        # 整体健康影响
        overall_factor = 1.0 - self.overall_health
        
        return base_risk * health_factor * overall_factor
    
    def get_treatment_options(self) -> List[TreatmentType]:
        """获取可用的治疗选项"""
        options = []
        
        # 根据当前疾病和伤害推荐治疗
        for disease in self.diseases.values():
            if disease.curable:
                if disease.disease_type in [DiseaseType.COMMON_COLD, DiseaseType.FLU]:
                    options.append(TreatmentType.REST)
                    options.append(TreatmentType.MEDICINE)
                elif disease.disease_type == DiseaseType.INFECTION:
                    options.append(TreatmentType.MEDICINE)
                    options.append(TreatmentType.HERBAL)
        
        for injury in self.injuries.values():
            if injury.injury_type in [InjuryType.CUT, InjuryType.BRUISE]:
                options.append(TreatmentType.BANDAGE)
            elif injury.injury_type == InjuryType.FRACTURE:
                options.append(TreatmentType.SURGERY)
                options.append(TreatmentType.BANDAGE)
        
        # 去重
        return list(set(options))
    
    def get_health_summary(self) -> Dict:
        """获取健康摘要"""
        return {
            'overall_health': self.overall_health,
            'health_status': self.get_health_status(),
            'diseases_count': len(self.diseases),
            'injuries_count': len(self.injuries),
            'active_treatments': [t.name for t in self.active_treatments],
            'immune_status': {
                'innate': self.innate_immunity,
                'acquired': self.acquired_immunity,
                'response': self.immune_response
            }
        }

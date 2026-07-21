#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_component.py
@说明:疾病组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum, auto

from core.component import Component


class DiseaseSeverity(Enum):
    """疾病严重程度"""
    MILD = auto()           # 轻微
    MODERATE = auto()       # 中等
    SEVERE = auto()         # 严重
    CRITICAL = auto()       # 危重


class TransmissionMode(Enum):
    """传播方式"""
    AIRBORNE = auto()       # 空气传播
    CONTACT = auto()        # 接触传播
    FOODBORNE = auto()      # 食物传播
    WATERBORNE = auto()     # 水源传播
    VECTOR = auto()         # 媒介传播（蚊虫等）
    BODILY_FLUID = auto()   # 体液传播


class DiseaseStage(Enum):
    """疾病阶段"""
    INCUBATION = auto()     # 潜伏期
    PRODROMAL = auto()      # 前驱期
    ACUTE = auto()          # 急性期
    CONVALESCENT = auto()   # 恢复期
    CHRONIC = auto()        # 慢性期


class DiseaseType(Enum):
    """疾病类型（兼容 v2 API）"""
    COMMON_COLD = "common_cold"
    FLU = "flu"
    INFECTION = "infection"
    FEVER = "fever"
    CHRONIC = "chronic"
    PARASITE = "parasite"
    VIRUS = "virus"
    BACTERIA = "bacteria"
    PLAGUE = "plague"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Disease:
    """疾病"""
    disease_id: int
    disease_type: str       # 疾病类型（如"流感"、"瘟疫"）
    severity: DiseaseSeverity
    transmission_mode: TransmissionMode
    stage: DiseaseStage
    
    # 传播属性
    infectivity: float = 0.5        # 传染性 (0-1)
    incubation_period: float = 3.0  # 潜伏期（天）
    infectious_period: float = 7.0  # 传染期（天）
    
    # 影响属性
    mortality_rate: float = 0.01    # 死亡率 (0-1)
    morbidity_rate: float = 0.3     # 发病率 (0-1)
    
    # 症状
    symptoms: List[str] = field(default_factory=list)  # 症状列表
    
    # 治疗
    treatment_effectiveness: float = 0.7  # 治疗有效性 (0-1)
    recovery_time: float = 10.0           # 恢复时间（天）
    
    # 免疫
    immunity_duration: float = 30.0       # 免疫持续时间（天）
    reinfection_probability: float = 0.1  # 再感染概率 (0-1)
    
    # 时间追踪
    infection_time: float = 0.0           # 感染时间
    stage_start_time: float = 0.0         # 阶段开始时间
    
    def is_contagious(self) -> bool:
        """是否具有传染性"""
        return self.stage in [DiseaseStage.PRODROMAL, DiseaseStage.ACUTE]
    
    def get_transmission_probability(self) -> float:
        """获取传播概率"""
        if not self.is_contagious():
            return 0.0
        
        base_probability = self.infectivity
        
        # 根据阶段调整传播概率
        if self.stage == DiseaseStage.PRODROMAL:
            return base_probability * 0.5  # 前驱期传播概率较低
        elif self.stage == DiseaseStage.ACUTE:
            return base_probability  # 急性期传播概率最高
        
        return 0.0


@dataclass(slots=True)
class Epidemic:
    """流行病"""
    epidemic_id: int
    disease_type: str
    start_time: float
    affected_regions: Set[str] = field(default_factory=set)  # 受影响区域
    
    # 统计
    total_infected: int = 0
    total_deaths: int = 0
    total_recovered: int = 0
    
    # 控制措施
    control_measures: List[str] = field(default_factory=list)  # 控制措施
    quarantine_active: bool = False
    
    def get_mortality_rate(self) -> float:
        """获取死亡率"""
        if self.total_infected == 0:
            return 0.0
        return self.total_deaths / self.total_infected
    
    def get_recovery_rate(self) -> float:
        """获取康复率"""
        if self.total_infected == 0:
            return 0.0
        return self.total_recovered / self.total_infected


@dataclass(slots=True)
class DiseaseManagerComponent(Component):
    """
    疾病管理组件 v4.0 - 细化版
    包括疾病状态、传播、治疗和免疫等细化功能。
    """
    
    # === 当前疾病 ===
    
    # === 当前疾病 ===
    current_diseases: Dict[int, Disease] = field(default_factory=dict)  # 疾病ID -> 疾病
    next_disease_id: int = 0
    
    # === 免疫状态 ===
    immunities: Dict[str, float] = field(default_factory=dict)  # 疾病类型 -> 免疫剩余时间
    natural_immunity: float = 0.5  # 先天免疫力 (0-1)
    acquired_immunity: float = 0.3  # 获得性免疫力 (0-1)
    
    # === 易感性 ===
    susceptibility: Dict[str, float] = field(default_factory=dict)  # 疾病类型 -> 易感性 (0-1)
    base_susceptibility: float = 0.5  # 基础易感性 (0-1)
    
    # === 治疗 ===
    under_treatment: bool = False  # 是否正在接受治疗
    treatment_effectiveness: float = 0.0  # 治疗有效性 (0-1)
    
    # === 隔离 ===
    quarantined: bool = False  # 是否被隔离
    quarantine_start_time: float = 0.0  # 隔离开始时间
    
    # === 历史 ===
    disease_history: List[Dict] = field(default_factory=list)  # 疾病历史
    max_history_length: int = 50
    
    # === v2 API 兼容字段 ===
    # 旧版 DiseaseComponent 使用单疾病字段（disease_name, infection_type, severity, ...）
    # 这些字段映射到 current_diseases 中的第一个疾病，实现平滑迁移。
    _v2_duration_ticks: int = 0
    _v2_max_duration_ticks: int = 100
    
    def add_disease(self, disease_type: str, severity: DiseaseSeverity, 
                   transmission_mode: TransmissionMode) -> int:
        """添加疾病"""
        disease_id = self.next_disease_id
        self.next_disease_id += 1
        
        # 根据疾病类型设置默认属性
        if disease_type == "流感":
            disease = Disease(
                disease_id=disease_id,
                disease_type=disease_type,
                severity=severity,
                transmission_mode=transmission_mode,
                stage=DiseaseStage.INCUBATION,
                infectivity=0.7,
                incubation_period=2.0,
                infectious_period=5.0,
                mortality_rate=0.001,
                symptoms=["发烧", "咳嗽", "乏力"],
                treatment_effectiveness=0.8,
                recovery_time=7.0
            )
        elif disease_type == "瘟疫":
            disease = Disease(
                disease_id=disease_id,
                disease_type=disease_type,
                severity=severity,
                transmission_mode=transmission_mode,
                stage=DiseaseStage.INCUBATION,
                infectivity=0.9,
                incubation_period=5.0,
                infectious_period=10.0,
                mortality_rate=0.3,
                symptoms=["高烧", "出血", "器官衰竭"],
                treatment_effectiveness=0.3,
                recovery_time=20.0
            )
        else:
            # 默认疾病
            disease = Disease(
                disease_id=disease_id,
                disease_type=disease_type,
                severity=severity,
                transmission_mode=transmission_mode,
                stage=DiseaseStage.INCUBATION,
                infectivity=0.5,
                incubation_period=3.0,
                infectious_period=7.0,
                mortality_rate=0.01,
                symptoms=["不适"],
                treatment_effectiveness=0.6,
                recovery_time=10.0
            )
        
        self.current_diseases[disease_id] = disease
        return disease_id
    
    def update_disease_stage(self, disease_id: int, current_time: float):
        """更新疾病阶段"""
        if disease_id not in self.current_diseases:
            return
        
        disease = self.current_diseases[disease_id]
        time_since_infection = current_time - disease.infection_time
        time_in_stage = current_time - disease.stage_start_time
        
        # 阶段转换逻辑
        if disease.stage == DiseaseStage.INCUBATION:
            if time_since_infection >= disease.incubation_period:
                disease.stage = DiseaseStage.PRODROMAL
                disease.stage_start_time = current_time
        
        elif disease.stage == DiseaseStage.PRODROMAL:
            if time_in_stage >= 1.0:  # 前驱期持续1天
                disease.stage = DiseaseStage.ACUTE
                disease.stage_start_time = current_time
        
        elif disease.stage == DiseaseStage.ACUTE:
            if time_in_stage >= disease.infectious_period:
                disease.stage = DiseaseStage.CONVALESCENT
                disease.stage_start_time = current_time
        
        elif disease.stage == DiseaseStage.CONVALESCENT:
            if time_in_stage >= disease.recovery_time:
                # 疾病痊愈
                self.recover_from_disease(disease_id, current_time)
    
    def recover_from_disease(self, disease_id: int, current_time: float):
        """从疾病中康复"""
        if disease_id not in self.current_diseases:
            return
        
        disease = self.current_diseases[disease_id]
        
        # 添加免疫力
        self.immunities[disease.disease_type] = disease.immunity_duration
        
        # 记录到历史
        self.disease_history.append({
            'disease_type': disease.disease_type,
            'severity': disease.severity.name,
            'infection_time': disease.infection_time,
            'recovery_time': current_time,
            'duration': current_time - disease.infection_time
        })
        
        # 限制历史记录长度
        if len(self.disease_history) > self.max_history_length:
            self.disease_history = self.disease_history[-self.max_history_length:]
        
        # 移除疾病
        del self.current_diseases[disease_id]
    
    def get_infection_probability(self, disease_type: str) -> float:
        """获取感染概率"""
        # 检查免疫力
        if disease_type in self.immunities and self.immunities[disease_type] > 0:
            return 0.0  # 有免疫力，不会感染
        
        # 获取易感性
        susceptibility = self.susceptibility.get(disease_type, self.base_susceptibility)
        
        # 计算感染概率
        base_probability = susceptibility
        
        # 考虑先天免疫力和获得性免疫力
        immunity_factor = (self.natural_immunity + self.acquired_immunity) / 2.0
        
        return base_probability * (1.0 - immunity_factor)
    
    def is_immune_to(self, disease_type: str) -> bool:
        """是否对疾病免疫"""
        return disease_type in self.immunities and self.immunities[disease_type] > 0
    
    def update_immunities(self, dt: float):
        """更新免疫力"""
        expired_immunities = []
        
        for disease_type, remaining_time in self.immunities.items():
            self.immunities[disease_type] = remaining_time - dt
            if self.immunities[disease_type] <= 0:
                expired_immunities.append(disease_type)
        
        # 移除过期免疫力
        for disease_type in expired_immunities:
            del self.immunities[disease_type]
    
    def get_disease_summary(self) -> Dict:
        """获取疾病摘要"""
        return {
            'current_diseases_count': len(self.current_diseases),
            'current_diseases': [d.disease_type for d in self.current_diseases.values()],
            'immunities_count': len(self.immunities),
            'under_treatment': self.under_treatment,
            'quarantined': self.quarantined,
            'disease_history_count': len(self.disease_history)
        }
    
    # === v2 API 兼容层 (Compatibility Layer for v2 DiseaseComponent) ===
    
    def _primary_disease(self) -> Optional[Disease]:
        """返回当前第一个疾病，用于兼容旧版单疾病 API"""
        if not self.current_diseases:
            return None
        # 按 disease_id 取最早添加的疾病
        first_id = min(self.current_diseases.keys())
        return self.current_diseases[first_id]
    
    def _ensure_primary_disease(self) -> Disease:
        """确保存在一个主疾病，用于兼容旧版单疾病写入"""
        disease = self._primary_disease()
        if disease is not None:
            return disease
        return self.add_disease_compat("unknown", "bacterial", 0.0, 0.0, "incubation", [])
    
    def add_disease_compat(self, disease_name: str, infection_type: str, severity: float,
                           contagiousness: float, stage: str, symptoms: List[str]) -> Disease:
        """兼容旧版的单疾病添加方式"""
        disease_id = self.next_disease_id
        self.next_disease_id += 1
        
        severity_enum = self._severity_float_to_enum(severity)
        transmission_mode = self._infection_type_str_to_mode(infection_type)
        stage_enum = self._stage_str_to_enum(stage)
        
        disease = Disease(
            disease_id=disease_id,
            disease_type=disease_name,
            severity=severity_enum,
            transmission_mode=transmission_mode,
            stage=stage_enum,
            infectivity=contagiousness,
            symptoms=list(symptoms) if symptoms else ["不适"],
            mortality_rate=0.9 if stage == "terminal" else severity * 0.1,
            recovery_time=float(self._v2_max_duration_ticks) if self._v2_max_duration_ticks > 0 else 10.0,
        )
        self.current_diseases[disease_id] = disease
        return disease
    
    @staticmethod
    def _severity_float_to_enum(severity: float) -> DiseaseSeverity:
        """旧版 0-1 severity 映射到新版等级"""
        severity = max(0.0, min(1.0, severity))
        if severity < 0.25:
            return DiseaseSeverity.MILD
        elif severity < 0.5:
            return DiseaseSeverity.MODERATE
        elif severity < 0.75:
            return DiseaseSeverity.SEVERE
        else:
            return DiseaseSeverity.CRITICAL
    
    @staticmethod
    def _severity_enum_to_float(severity: DiseaseSeverity) -> float:
        """新版 severity 等级映射回旧版 0-1"""
        mapping = {
            DiseaseSeverity.MILD: 0.15,
            DiseaseSeverity.MODERATE: 0.4,
            DiseaseSeverity.SEVERE: 0.65,
            DiseaseSeverity.CRITICAL: 0.9,
        }
        return mapping.get(severity, 0.0)
    
    @staticmethod
    def _stage_str_to_enum(stage: str) -> DiseaseStage:
        """旧版 stage 字符串映射到新版枚举"""
        stage = (stage or "").lower()
        if stage == "incubation":
            return DiseaseStage.INCUBATION
        elif stage == "active":
            return DiseaseStage.ACUTE
        elif stage == "recovery":
            return DiseaseStage.CONVALESCENT
        elif stage == "terminal":
            return DiseaseStage.ACUTE
        else:
            return DiseaseStage.INCUBATION
    
    @staticmethod
    def _stage_enum_to_str(stage: DiseaseStage) -> str:
        """新版 stage 枚举映射回旧版字符串"""
        mapping = {
            DiseaseStage.INCUBATION: "incubation",
            DiseaseStage.PRODROMAL: "incubation",
            DiseaseStage.ACUTE: "active",
            DiseaseStage.CONVALESCENT: "recovery",
            DiseaseStage.CHRONIC: "active",
        }
        return mapping.get(stage, "incubation")
    
    @staticmethod
    def _infection_type_str_to_mode(infection_type: str) -> TransmissionMode:
        """旧版 infection_type 字符串映射到新版传播方式"""
        infection_type = (infection_type or "").lower()
        if infection_type == "viral":
            return TransmissionMode.AIRBORNE
        elif infection_type == "bacterial":
            return TransmissionMode.CONTACT
        elif infection_type == "parasitic":
            return TransmissionMode.VECTOR
        elif infection_type == "fungal":
            return TransmissionMode.CONTACT
        else:
            return TransmissionMode.CONTACT
    
    @staticmethod
    def _infection_type_mode_to_str(transmission_mode: TransmissionMode) -> str:
        """新版传播方式映射回旧版 infection_type 字符串"""
        mapping = {
            TransmissionMode.AIRBORNE: "viral",
            TransmissionMode.CONTACT: "bacterial",
            TransmissionMode.FOODBORNE: "bacterial",
            TransmissionMode.WATERBORNE: "bacterial",
            TransmissionMode.VECTOR: "parasitic",
            TransmissionMode.BODILY_FLUID: "viral",
        }
        return mapping.get(transmission_mode, "bacterial")
    
    @property
    def disease_name(self) -> str:
        """兼容v2: 疾病名称"""
        disease = self._primary_disease()
        return disease.disease_type if disease else "unknown"
    
    @disease_name.setter
    def disease_name(self, value: str):
        disease = self._ensure_primary_disease()
        disease.disease_type = value
    
    @property
    def infection_type(self) -> str:
        """兼容v2: 感染类型"""
        disease = self._primary_disease()
        return self._infection_type_mode_to_str(disease.transmission_mode) if disease else "bacterial"
    
    @infection_type.setter
    def infection_type(self, value: str):
        disease = self._ensure_primary_disease()
        disease.transmission_mode = self._infection_type_str_to_mode(value)
    
    @property
    def severity(self) -> float:
        """兼容v2: 严重程度 [0.0, 1.0]"""
        disease = self._primary_disease()
        return self._severity_enum_to_float(disease.severity) if disease else 0.0
    
    @severity.setter
    def severity(self, value: float):
        disease = self._ensure_primary_disease()
        disease.severity = self._severity_float_to_enum(value)
    
    @property
    def contagiousness(self) -> float:
        """兼容v2: 传染性 [0.0, 1.0]"""
        disease = self._primary_disease()
        return disease.infectivity if disease else 0.0
    
    @contagiousness.setter
    def contagiousness(self, value: float):
        disease = self._ensure_primary_disease()
        disease.infectivity = max(0.0, min(1.0, value))
    
    @property
    def stage(self) -> str:
        """兼容v2: 疾病阶段"""
        disease = self._primary_disease()
        return self._stage_enum_to_str(disease.stage) if disease else "incubation"
    
    @stage.setter
    def stage(self, value: str):
        disease = self._ensure_primary_disease()
        disease.stage = self._stage_str_to_enum(value)
    
    @property
    def symptoms(self) -> List[str]:
        """兼容v2: 症状列表"""
        disease = self._primary_disease()
        return list(disease.symptoms) if disease else []
    
    @symptoms.setter
    def symptoms(self, value: List[str]):
        disease = self._ensure_primary_disease()
        disease.symptoms = list(value) if value else []
    
    @property
    def duration(self) -> int:
        """兼容v2: 已持续时间（tick）"""
        return self._v2_duration_ticks
    
    @duration.setter
    def duration(self, value: int):
        self._v2_duration_ticks = max(0, int(value))
    
    @property
    def max_duration(self) -> int:
        """兼容v2: 最大持续时间（tick）"""
        return self._v2_max_duration_ticks
    
    @max_duration.setter
    def max_duration(self, value: int):
        self._v2_max_duration_ticks = max(1, int(value))
    
    @property
    def is_terminal(self) -> bool:
        """兼容v2: 是否致命"""
        disease = self._primary_disease()
        return disease.mortality_rate >= 0.5 if disease else False
    
    @is_terminal.setter
    def is_terminal(self, value: bool):
        disease = self._ensure_primary_disease()
        if value:
            disease.mortality_rate = 0.9
            if disease.severity != DiseaseSeverity.CRITICAL:
                disease.severity = DiseaseSeverity.CRITICAL
        else:
            disease.mortality_rate = 0.01
    
    @property
    def immunity(self) -> Dict[str, float]:
        """兼容v2: 免疫字典（别名指向 immunities）"""
        return self.immunities
    
    @property
    def diseases(self) -> List[Disease]:
        """兼容v2: 疾病列表（返回 current_diseases 的 values）"""
        return list(self.current_diseases.values())

# (Same content as before - healthcare_system.py)
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:healthcare_system.py
@说明:医疗保健系统 - 疾病诊断与治疗
@时间:2026/04/27
@作者:Coder Agent
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto

from core.system import System
from core.world import World

# 统一从 biology 层导入疾病类型定义
from biology.components.disease_component import DiseaseType


# 症状枚举
class SymptomType(Enum):
    FEVER = "fever"
    COUGH = "cough"
    PAIN = "pain"
    FATIGUE = "fatigue"
    NAUSEA = "nausea"
    HAemorrhage = "hemorrhage"
    SWELLING = "swelling"
    RASH = "rash"
    HEADACHE = "headache"
    DIZZINESS = "dizziness"


@dataclass
class Disease:
    """疾病数据结构"""
    id: str
    name: str
    type: DiseaseType
    symptoms: List[str]
    severity: float
    
    treatments: List[Dict] = field(default_factory=list)
    contagion_level: float = 0.0


class HealthcareSystem(System):
    tick_interval = 10  # 每10帧执行一次（治疗不需要每帧）
    _MAX_HISTORY_SIZE = 100

    def __init__(self):
        super().__init__()
        self.current_disease = None
        self.treatment_plan = None
        self.medication_log = []
        self.health_history = []

    def _add_health_history(self, entry: dict) -> None:
        self.health_history.append(entry)
        if len(self.health_history) > self._MAX_HISTORY_SIZE:
            self.health_history.pop(0)

    def update(self, world: World, dt: float = 0.0):
        """系统更新：扫描疾病并尝试治疗"""
        from biology.components.disease_component import DiseaseComponent
        from biology.components.health_status_component import HealthStatusComponent

        for entity, (disease_comp, health) in world.get_components(
            DiseaseComponent, HealthStatusComponent
        ):
            disease_comp: DiseaseComponent
            health: HealthStatusComponent

            # 治疗：降低严重度
            if disease_comp.severity > 0:
                disease_comp.severity = max(0.0, disease_comp.severity - 0.5 * dt)

            # 增加免疫（使用组件的 immunity 字段，如果不存在则跳过）
            if hasattr(disease_comp, 'immunity'):
                disease_comp.immunity[disease_comp.disease_name] = min(
                    1.0,
                    disease_comp.immunity.get(disease_comp.disease_name, 0) + 0.01 * dt
                )

                # 如果严重度降为 0 且免疫足够，重置疾病
                if (disease_comp.severity <= 0
                        and disease_comp.immunity.get(disease_comp.disease_name, 0) > 0.5):
                    disease_comp.severity = 0.0
                    disease_comp.stage = "recovery"

            # 记录治疗历史
            self._add_health_history({
                "entity_id": entity.id,
                "disease": disease_comp.disease_name,
                "severity": disease_comp.severity,
                "action": "treatment",
                "timestamp": "now",
            })

    def diagnose(self, symptoms: Dict[str, float], patient_data: Dict) -> List[Disease]:
        """根据症状和患者数据诊断疾病"""
        possible_diseases = []
        
        symptom_names = list(symptoms.keys())
        
        if "fever" in symptom_names and symptoms["fever"] > 70:
            possible_diseases.append(Disease(
                id="fever_01",
                name="High Fever",
                type=DiseaseType.ACUTE,
                severity=symptoms["fever"],
                symptoms=["fever", "headache"],
                treatments=[{"name": "antipyretic", "dosage": "500mg q6h"}]
            ))
        
        if any(s in symptom_names for s in ["cough", "wheezing"]):
            possible_diseases.append(Disease(
                id="resp_inf_01",
                name="Respiratory Infection",
                type=DiseaseType.INFECTIOUS,
                severity=min(100, symptoms.get("fever", 0) + symptoms.get("cough", 0)),
                symptoms=["cough", "fever"],
                treatments=[{"name": "antibiotics", "dosage": "按医嘱"}]
            ))
        
        self._add_health_history({
            "diagnosis_time": "now",
            "symptoms": dict(symptoms),
            "diagnosed_diseases": [d.name for d in possible_diseases]
        })
        
        return possible_diseases

    def get_symptom_combination(self, combination: str) -> List[str]:
        """识别症状组合类别"""
        symptom_keywords = {
            "fever": ["fever", "高", "热"],
            "respiratory": ["cough", "咳"],
            "digestive": ["nausea", "吐"]
        }
        
        found_categories = []
        for category, keywords in symptom_keywords.items():
            if any(kw in combination.lower() for kw in keywords):
                found_categories.append(category)
        
        return found_categories

    def prescribe_treatment(self, disease: Disease, patient_condition: str) -> Dict:
        """制定治疗方案"""
        return {
            "disease": disease.name,
            "primary_medications": disease.treatments,
            "lifestyle_changes": ["rest", "hydration"],
            "follow_up_needed": True
        }

    def record_medication(self, medication: str, dosage: str, side_effects: List[str]) -> None:
        """记录用药"""
        self.medication_log.append({
            "medication": medication,
            "dosage": dosage,
            "side_effects": side_effects,
            "timestamp": "now"
        })


if __name__ == "__main__":
    import logging
    logging.getLogger(__name__).debug("医疗保健系统已加载")
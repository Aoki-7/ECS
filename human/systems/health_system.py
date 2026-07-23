#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:health_system.py
@说明:健康系统 v3.0 - 细化版
@时间:2026/07/19
@版本:3.0
'''

import logging
import random
from typing import Dict, List, Optional
from core.system import System
from core.world import World
from human.components.health.health_component import HealthComponent, DiseaseType, InjuryType, TreatmentType, BodyPart
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class HealthSystem(System):
    """健康系统 v3.0 - 细化版"""
    tick_interval = 10  # 每10帧更新一次

    def __init__(self):
        self.disease_spread_probability = 0.01  # 疾病传播概率
        self.injury_probability = 0.001  # 受伤概率

    def update(self, world: World, dt: float):
        """更新健康系统"""
        for e, (health, human, pos) in world.get_components(
            HealthComponent, HumanComponent, SpaceComponent
        ):
            entity_id = e.id
            
            # 更新健康状态
            health.update_health(dt)
            
            # 检查疾病风险
            self._check_disease_risk(health, world, entity_id)
            
            # 检查受伤风险
            self._check_injury_risk(health, world, entity_id)
            
            # 处理疾病传播
            self._handle_disease_spread(health, world, entity_id, pos)
            
            # 自动治疗
            self._auto_treatment(health)

    def _check_disease_risk(self, health: HealthComponent, world: World, entity_id: int):
        """检查疾病风险"""
        # 检查各种疾病风险
        for disease_type in DiseaseType:
            risk = health.get_disease_risk(disease_type)
            
            # 随机感染
            if random.random() < risk * 0.001:  # 调整概率
                disease_name = self._get_disease_name(disease_type)
                severity = random.uniform(0.3, 0.8)
                symptoms = self._get_disease_symptoms(disease_type)
                affected_parts = self._get_affected_parts(disease_type)
                
                health.add_disease(disease_type, disease_name, severity, symptoms, affected_parts)
                logger.info(f"[Health] 实体{entity_id} 感染疾病: {disease_name}")

    def _check_injury_risk(self, health: HealthComponent, world: World, entity_id: int):
        """检查受伤风险"""
        # 检查各种伤害风险
        for injury_type in InjuryType:
            for body_part in BodyPart:
                risk = health.get_injury_risk(injury_type, body_part)
                
                # 随机受伤
                if random.random() < risk * 0.0001:  # 调整概率
                    severity = random.uniform(0.2, 0.7)
                    pain_level = random.uniform(0.3, 0.9)
                    
                    health.add_injury(injury_type, body_part, severity, pain_level)
                    logger.info(f"[Health] 实体{entity_id} 受伤: {injury_type.name} at {body_part.name}")

    def _handle_disease_spread(self, health: HealthComponent, world: World, 
                              entity_id: int, pos: SpaceComponent):
        """处理疾病传播"""
        # 检查是否有传染性疾病
        contagious_diseases = [d for d in health.diseases.values() if d.contagious]
        
        if not contagious_diseases:
            return
        
        # 查找附近的其他实体
        nearby_entities = self._find_nearby_entities(world, pos, radius=10.0)
        
        for nearby_id in nearby_entities:
            if nearby_id == entity_id:
                continue
            
            # 获取附近实体的健康组件
            nearby_health = world.get_component(nearby_id, HealthComponent)
            if not nearby_health:
                continue
            
            # 传播疾病
            for disease in contagious_diseases:
                contagion_risk = disease.get_contagion_risk()
                
                if random.random() < contagion_risk * self.disease_spread_probability:
                    # 检查是否已经有免疫力
                    if disease.disease_type in nearby_health.disease_immunity:
                        immunity = nearby_health.disease_immunity[disease.disease_type]
                        if immunity > 0:
                            continue  # 有免疫力，不感染
                    
                    # 感染疾病
                    nearby_health.add_disease(
                        disease.disease_type,
                        disease.name,
                        disease.severity * 0.8,  # 传播的疾病稍轻
                        disease.symptoms,
                        disease.affected_parts
                    )
                    logger.info(f"[Health] 疾病传播: 实体{entity_id} -> 实体{nearby_id}, 疾病: {disease.name}")

    def _auto_treatment(self, health: HealthComponent):
        """自动治疗"""
        # 根据当前疾病和伤害自动选择治疗方法
        treatment_options = health.get_treatment_options()
        
        if treatment_options:
            # 选择最合适的治疗方法
            best_treatment = self._select_best_treatment(health, treatment_options)
            health.apply_treatment(best_treatment)

    def _select_best_treatment(self, health: HealthComponent, options: List[TreatmentType]) -> TreatmentType:
        """选择最佳治疗方法"""
        # 简单的选择逻辑
        if TreatmentType.MEDICINE in options:
            return TreatmentType.MEDICINE
        elif TreatmentType.BANDAGE in options:
            return TreatmentType.BANDAGE
        elif TreatmentType.HERBAL in options:
            return TreatmentType.HERBAL
        elif TreatmentType.REST in options:
            return TreatmentType.REST
        else:
            return options[0]

    def _find_nearby_entities(self, world: World, pos: SpaceComponent, radius: float) -> List[int]:
        """查找附近的实体"""
        nearby_entities = []
        
        for e, (human, other_pos) in world.get_components(HumanComponent, SpaceComponent):
            distance = ((pos.x - other_pos.x)**2 + (pos.y - other_pos.y)**2)**0.5
            if distance <= radius:
                nearby_entities.append(e.id)
        
        return nearby_entities

    def _get_disease_name(self, disease_type: DiseaseType) -> str:
        """获取疾病名称"""
        disease_names = {
            DiseaseType.COMMON_COLD: "普通感冒",
            DiseaseType.FLU: "流感",
            DiseaseType.INFECTION: "感染",
            DiseaseType.FEVER: "发烧",
            DiseaseType.CHRONIC: "慢性病",
            DiseaseType.PARASITE: "寄生虫感染",
            DiseaseType.VIRUS: "病毒感染",
            DiseaseType.BACTERIA: "细菌感染"
        }
        return disease_names.get(disease_type, "未知疾病")

    def _get_disease_symptoms(self, disease_type: DiseaseType) -> List[str]:
        """获取疾病症状"""
        symptoms = {
            DiseaseType.COMMON_COLD: ["咳嗽", "流鼻涕", "喉咙痛"],
            DiseaseType.FLU: ["高烧", "头痛", "肌肉疼痛", "疲劳"],
            DiseaseType.INFECTION: ["红肿", "疼痛", "发热"],
            DiseaseType.FEVER: ["体温升高", "寒战", "出汗"],
            DiseaseType.CHRONIC: ["疲劳", "疼痛", "功能下降"],
            DiseaseType.PARASITE: ["腹痛", "腹泻", "体重下降"],
            DiseaseType.VIRUS: ["发热", "疲劳", "皮疹"],
            DiseaseType.BACTERIA: ["发热", "疼痛", "炎症"]
        }
        return symptoms.get(disease_type, ["不适"])

    def _get_affected_parts(self, disease_type: DiseaseType) -> List[BodyPart]:
        """获取受影响的身体部位"""
        affected_parts = {
            DiseaseType.COMMON_COLD: [BodyPart.HEAD, BodyPart.LUNGS],
            DiseaseType.FLU: [BodyPart.HEAD, BodyPart.TORSO, BodyPart.LUNGS],
            DiseaseType.INFECTION: [BodyPart.TORSO],
            DiseaseType.FEVER: [BodyPart.HEAD, BodyPart.TORSO],
            DiseaseType.CHRONIC: [BodyPart.HEART, BodyPart.LUNGS],
            DiseaseType.PARASITE: [BodyPart.STOMACH],
            DiseaseType.VIRUS: [BodyPart.TORSO],
            DiseaseType.BACTERIA: [BodyPart.TORSO]
        }
        return affected_parts.get(disease_type, [BodyPart.TORSO])

    def get_health_statistics(self, world: World) -> Dict:
        """获取健康统计"""
        total_entities = 0
        healthy_entities = 0
        diseased_entities = 0
        injured_entities = 0
        
        for e, (health, human) in world.get_components(HealthComponent, HumanComponent):
            total_entities += 1
            
            if health.overall_health > 0.8:
                healthy_entities += 1
            
            if health.diseases:
                diseased_entities += 1
            
            if health.injuries:
                injured_entities += 1
        
        return {
            'total_entities': total_entities,
            'healthy_entities': healthy_entities,
            'diseased_entities': diseased_entities,
            'injured_entities': injured_entities,
            'health_rate': healthy_entities / total_entities if total_entities > 0 else 0.0,
            'disease_rate': diseased_entities / total_entities if total_entities > 0 else 0.0,
            'injury_rate': injured_entities / total_entities if total_entities > 0 else 0.0
        }
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_system.py
@说明:疾病系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional, Set
from core.system import System
from core.world import World
from human.components.health.disease_component_v4 import DiseaseManagerComponent, Disease, DiseaseSeverity, TransmissionMode, DiseaseStage
from human.components.health.health_component import HealthComponent
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.social.social_component_v4 import SocialManagerComponent

logger = logging.getLogger(__name__)


class DiseaseSystem(System):
    """疾病系统 v4.0 - 细化版"""
    tick_interval = 5  # 每5帧更新一次

    def __init__(self):
        self.infection_probability = 0.02  # 基础感染概率
        self.transmission_radius = 10.0    # 传播半径
        self.epidemic_threshold = 0.1      # 流行病阈值（感染人口比例）
        
        # 疾病类型库
        self.disease_types = {
            "流感": {
                "infectivity": 0.7,
                "mortality_rate": 0.001,
                "transmission_mode": TransmissionMode.AIRBORNE
            },
            "瘟疫": {
                "infectivity": 0.9,
                "mortality_rate": 0.3,
                "transmission_mode": TransmissionMode.CONTACT
            },
            "痢疾": {
                "infectivity": 0.5,
                "mortality_rate": 0.05,
                "transmission_mode": TransmissionMode.WATERBORNE
            },
            "疟疾": {
                "infectivity": 0.6,
                "mortality_rate": 0.1,
                "transmission_mode": TransmissionMode.VECTOR
            }
        }

    def update(self, world: World, dt: float):
        """更新疾病系统"""
        current_time = world.get_time().total_hours if world.get_time() else 0.0
        
        # 获取所有人类实体
        humans = []
        for e, (disease, health, human, pos) in world.get_components(
            DiseaseManagerComponent, HealthComponent, HumanComponent, SpaceComponent
        ):
            humans.append((e.id, disease, health, pos))
        
        # 更新疾病状态
        self._update_disease_states(world, humans, current_time, dt)
        
        # 处理疾病传播
        self._handle_disease_transmission(world, humans, current_time)
        
        # 处理新感染
        self._handle_new_infections(world, humans, current_time)
        
        # 检查流行病
        self._check_epidemics(world, humans, current_time)

    def _update_disease_states(self, world: World, humans: List, current_time: float, dt: float):
        """更新疾病状态"""
        for entity_id, disease, health, pos in humans:
            # 更新免疫力
            disease.update_immunities(dt)
            
            # 更新当前疾病
            for disease_id in list(disease.current_diseases.keys()):
                disease.update_disease_stage(disease_id, current_time)
                
                # 获取疾病对象
                if disease_id in disease.current_diseases:
                    current_disease = disease.current_diseases[disease_id]
                    
                    # 更新健康状态
                    self._update_health_effects(health, current_disease)
                    
                    # 检查死亡
                    if self._check_death(current_disease, health):
                        logger.info(f"[Disease] 实体{entity_id} 死于疾病: {current_disease.disease_type}")
                        # 实际应用中应该触发死亡事件
                        # world.remove_entity(entity)

    def _update_health_effects(self, health: HealthComponent, disease: Disease):
        """更新疾病对健康的影响"""
        # 根据疾病严重程度影响健康
        if disease.severity == DiseaseSeverity.MILD:
            health.overall_health = max(0.1, health.overall_health - 0.01)
        elif disease.severity == DiseaseSeverity.MODERATE:
            health.overall_health = max(0.1, health.overall_health - 0.03)
        elif disease.severity == DiseaseSeverity.SEVERE:
            health.overall_health = max(0.1, health.overall_health - 0.05)
        elif disease.severity == DiseaseSeverity.CRITICAL:
            health.overall_health = max(0.1, health.overall_health - 0.1)

    def _check_death(self, disease: Disease, health: HealthComponent) -> bool:
        """检查是否死亡"""
        # 基于疾病死亡率和健康状况
        death_probability = disease.mortality_rate * (1.0 - health.overall_health)
        return random.random() < death_probability

    def _handle_disease_transmission(self, world: World, humans: List, current_time: float):
        """处理疾病传播"""
        for entity_id, disease, health, pos in humans:
            # 检查每个当前疾病
            for disease_id, current_disease in disease.current_diseases.items():
                if not current_disease.is_contagious():
                    continue
                
                # 查找附近的其他实体
                nearby_entities = self._find_nearby_entities(world, pos, self.transmission_radius)
                
                for nearby_id in nearby_entities:
                    if nearby_id == entity_id:
                        continue
                    
                    # 获取附近实体的疾病组件
                    nearby_entity = world.query_entity(nearby_id)
                    if not nearby_entity:
                        continue
                    
                    nearby_disease = world.get_component(nearby_entity, DiseaseManagerComponent)
                    if not nearby_disease:
                        continue
                    
                    # 检查是否已经感染相同疾病
                    already_infected = any(d.disease_type == current_disease.disease_type 
                                          for d in nearby_disease.current_diseases.values())
                    if already_infected:
                        continue
                    
                    # 计算传播概率
                    transmission_prob = current_disease.get_transmission_probability()
                    infection_prob = nearby_disease.get_infection_probability(current_disease.disease_type)
                    
                    # 尝试传播
                    if random.random() < transmission_prob * infection_prob:
                        self._infect_entity(nearby_disease, current_disease.disease_type, 
                                          current_disease.severity, current_time)
                        logger.debug(f"[Disease] 实体{entity_id} 传播疾病{current_disease.disease_type}给实体{nearby_id}")

    def _handle_new_infections(self, world: World, humans: List, current_time: float):
        """处理新感染"""
        for entity_id, disease, health, pos in humans:
            # 随机感染新疾病
            if random.random() < self.infection_probability:
                # 随机选择疾病类型
                disease_type = random.choice(list(self.disease_types.keys()))
                disease_info = self.disease_types[disease_type]
                
                # 检查是否已经感染或免疫
                already_infected = any(d.disease_type == disease_type 
                                      for d in disease.current_diseases.values())
                if already_infected or disease.is_immune_to(disease_type):
                    continue
                
                # 随机选择严重程度
                severity = random.choice(list(DiseaseSeverity))
                
                # 感染疾病
                self._infect_entity(disease, disease_type, severity, current_time)
                logger.debug(f"[Disease] 实体{entity_id} 感染新疾病: {disease_type}")

    def _infect_entity(self, disease: DiseaseManagerComponent, disease_type: str, 
                      severity: DiseaseSeverity, current_time: float):
        """感染实体"""
        disease_info = self.disease_types.get(disease_type, {
            "infectivity": 0.5,
            "mortality_rate": 0.01,
            "transmission_mode": TransmissionMode.CONTACT
        })
        
        # 添加疾病
        disease_id = disease.add_disease(
            disease_type=disease_type,
            severity=severity,
            transmission_mode=disease_info["transmission_mode"]
        )
        
        # 设置感染时间
        if disease_id in disease.current_diseases:
            disease.current_diseases[disease_id].infection_time = current_time
            disease.current_diseases[disease_id].stage_start_time = current_time

    def _check_epidemics(self, world: World, humans: List, current_time: float):
        """检查流行病"""
        # 统计各种疾病类型的感染人数
        disease_counts = {}
        total_population = len(humans)
        
        for entity_id, disease, health, pos in humans:
            for current_disease in disease.current_diseases.values():
                disease_type = current_disease.disease_type
                disease_counts[disease_type] = disease_counts.get(disease_type, 0) + 1
        
        # 检查是否达到流行病阈值
        for disease_type, count in disease_counts.items():
            infection_rate = count / total_population if total_population > 0 else 0
            
            if infection_rate >= self.epidemic_threshold:
                logger.warning(f"[Disease] 疾病{disease_type}达到流行病水平，感染率: {infection_rate:.2%}")
                # 实际应用中应该触发流行病事件

    def _find_nearby_entities(self, world: World, pos: SpaceComponent, radius: float) -> List[int]:
        """查找附近的实体"""
        nearby_entities = []
        
        for e, (human, other_pos) in world.get_components(HumanComponent, SpaceComponent):
            distance = ((pos.x - other_pos.x)**2 + (pos.y - other_pos.y)**2)**0.5
            if distance <= radius:
                nearby_entities.append(e.id)
        
        return nearby_entities

    def get_disease_statistics(self, world: World) -> Dict:
        """获取疾病统计"""
        total_entities = 0
        infected_entities = 0
        disease_type_counts = {}
        total_deaths = 0  # 实际应用中应该统计死亡人数
        
        for e, (disease, human) in world.get_components(DiseaseManagerComponent, HumanComponent):
            total_entities += 1
            
            if disease.current_diseases:
                infected_entities += 1
                
                for current_disease in disease.current_diseases.values():
                    disease_type = current_disease.disease_type
                    disease_type_counts[disease_type] = disease_type_counts.get(disease_type, 0) + 1
        
        return {
            'total_entities': total_entities,
            'infected_entities': infected_entities,
            'infection_rate': infected_entities / total_entities if total_entities > 0 else 0.0,
            'disease_type_distribution': disease_type_counts,
            'total_deaths': total_deaths
        }

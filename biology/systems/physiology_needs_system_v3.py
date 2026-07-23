#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_system.py
@说明:生理需求系统 v3.0 - 细化版
@时间:2026/07/19
@版本:3.0
'''

import logging
from typing import Dict, List, Optional
from core.system import System
from core.world import World
from biology.components.physiology_needs_component_v3 import PhysiologyNeedsComponent, SleepStage, FatigueType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType

logger = logging.getLogger(__name__)


class PhysiologyNeedsSystem(System):
    """生理需求系统 v3.0 - 细化版"""
    tick_interval = 1  # 每1帧更新一次

    def __init__(self):
        self.activity_levels: Dict[int, float] = {}  # 实体ID -> 活动水平
        self.sleeping_entities: Dict[int, bool] = {}  # 实体ID -> 是否在睡觉

    def update(self, world: World, dt: float):
        """更新生理需求系统"""
        for e, (needs, human, pos, intent) in world.get_components(
            PhysiologyNeedsComponent, HumanComponent, SpaceComponent, IntentComponent
        ):
            entity_id = e.id
            
            # 获取活动水平
            activity_level = self._get_activity_level(intent)
            self.activity_levels[entity_id] = activity_level
            
            # 更新代谢
            needs.update_metabolism(dt, activity_level)
            
            # 更新睡眠
            is_sleeping = intent.intent == IntentType.SLEEP
            self.sleeping_entities[entity_id] = is_sleeping
            needs.update_sleep(dt, is_sleeping)
            
            # 更新基本需求
            self._update_basic_needs(needs, dt, activity_level)
            
            # 更新排泄系统
            self._update_excretion(needs, dt)
            
            # 更新呼吸系统
            self._update_respiration(needs, dt, activity_level)
            
            # 更新循环系统
            self._update_circulation(needs, dt, activity_level)
            
            # 更新体温调节
            self._update_temperature_regulation(needs, dt, world, pos)
            
            # 更新激素水平
            self._update_hormones(needs, dt, activity_level)
            
            # 检查需求优先级
            self._check_priority_needs(needs, intent)

    def _get_activity_level(self, intent: IntentComponent) -> float:
        """获取活动水平"""
        if intent.intent == IntentType.SLEEP:
            return 0.1
        elif intent.intent in [IntentType.REST, IntentType.IDLE]:
            return 0.3
        elif intent.intent in [IntentType.WALK, IntentType.SOCIALIZE]:
            return 0.6
        elif intent.intent in [IntentType.WORK, IntentType.GATHER, IntentType.BUILD]:
            return 0.8
        elif intent.intent in [IntentType.RUN, IntentType.FIGHT, IntentType.FLEE]:
            return 1.0
        else:
            return 0.5

    def _update_basic_needs(self, needs: PhysiologyNeedsComponent, dt: float, activity_level: float):
        """更新基本需求"""
        # 饥饿
        hunger_rate = 0.01 * activity_level
        needs.hunger = min(1.0, needs.hunger + hunger_rate * dt)
        needs.hunger_sensation = min(1.0, needs.hunger_sensation + hunger_rate * dt)
        
        # 口渴
        thirst_rate = 0.015 * activity_level
        needs.thirst = min(1.0, needs.thirst + thirst_rate * dt)
        needs.thirst_sensation = min(1.0, needs.thirst_sensation + thirst_rate * dt)
        
        # 疲劳
        fatigue_rate = 0.008 * activity_level
        needs.fatigue = min(1.0, needs.fatigue + fatigue_rate * dt)
        
        # 困倦
        sleepiness_rate = 0.005 * (1.0 + needs.sleep_debt / 8.0)
        needs.sleepiness = min(1.0, needs.sleepiness + sleepiness_rate * dt)
        
        # 营养消耗
        nutrition_consumption = 0.005 * activity_level
        needs.protein = max(0.0, needs.protein - nutrition_consumption * dt)
        needs.carbohydrate = max(0.0, needs.carbohydrate - nutrition_consumption * dt)
        needs.fat = max(0.0, needs.fat - nutrition_consumption * dt)
        needs.vitamin = max(0.0, needs.vitamin - nutrition_consumption * 0.5 * dt)
        needs.mineral = max(0.0, needs.mineral - nutrition_consumption * 0.5 * dt)

    def _update_excretion(self, needs: PhysiologyNeedsComponent, dt: float):
        """更新排泄系统"""
        # 膀胱
        bladder_rate = 0.02
        needs.bladder = min(1.0, needs.bladder + bladder_rate * dt)
        
        # 肠道
        bowel_rate = 0.01
        needs.bowel = min(1.0, needs.bowel + bowel_rate * dt)
        
        # 出汗（根据活动水平和体温）
        sweat_rate = 0.01 * (needs.body_temperature - 37.0) / 10.0
        if sweat_rate > 0:
            needs.sweat = min(1.0, needs.sweat + sweat_rate * dt)

    def _update_respiration(self, needs: PhysiologyNeedsComponent, dt: float, activity_level: float):
        """更新呼吸系统"""
        # 呼吸频率根据活动水平调整
        base_rate = 12.0
        activity_factor = activity_level * 10.0
        needs.breathing_rate = base_rate + activity_factor
        
        # 血氧水平
        if activity_level > 0.8:
            # 高强度活动时血氧可能下降
            needs.oxygen_level = max(0.7, needs.oxygen_level - 0.01 * dt)
        else:
            # 正常活动时血氧恢复
            needs.oxygen_level = min(1.0, needs.oxygen_level + 0.005 * dt)

    def _update_circulation(self, needs: PhysiologyNeedsComponent, dt: float, activity_level: float):
        """更新循环系统"""
        # 心率根据活动水平调整
        base_rate = 60.0
        activity_factor = activity_level * 80.0
        needs.heart_rate = base_rate + activity_factor
        
        # 血压根据活动水平调整
        base_systolic = 120.0
        base_diastolic = 80.0
        activity_factor_systolic = activity_level * 40.0
        activity_factor_diastolic = activity_level * 20.0
        
        needs.blood_pressure_systolic = base_systolic + activity_factor_systolic
        needs.blood_pressure_diastolic = base_diastolic + activity_factor_diastolic

    def _update_temperature_regulation(self, needs: PhysiologyNeedsComponent, dt: float, 
                                      world: World, pos: SpaceComponent):
        """更新体温调节"""
        # 获取环境温度（简化）
        ambient_temperature = 25.0  # 假设环境温度25度
        
        # 体温调节
        if needs.body_temperature < 36.5:
            # 体温过低，寒战
            needs.temperature_regulation['shivering'] = min(1.0, 
                needs.temperature_regulation['shivering'] + 0.1 * dt)
            needs.temperature_regulation['vasoconstriction'] = min(1.0,
                needs.temperature_regulation['vasoconstriction'] + 0.1 * dt)
        elif needs.body_temperature > 37.5:
            # 体温过高，出汗
            needs.temperature_regulation['sweating'] = min(1.0,
                needs.temperature_regulation['sweating'] + 0.1 * dt)
            needs.temperature_regulation['vasodilation'] = min(1.0,
                needs.temperature_regulation['vasodilation'] + 0.1 * dt)
        else:
            # 体温正常，恢复正常
            needs.temperature_regulation['shivering'] = max(0.0,
                needs.temperature_regulation['shivering'] - 0.05 * dt)
            needs.temperature_regulation['sweating'] = max(0.0,
                needs.temperature_regulation['sweating'] - 0.05 * dt)
            needs.temperature_regulation['vasoconstriction'] = max(0.0,
                needs.temperature_regulation['vasoconstriction'] - 0.05 * dt)
            needs.temperature_regulation['vasodilation'] = max(0.0,
                needs.temperature_regulation['vasodilation'] - 0.05 * dt)
        
        # 体温向环境温度回归
        temperature_diff = ambient_temperature - needs.body_temperature
        needs.body_temperature += temperature_diff * 0.01 * dt

    def _update_hormones(self, needs: PhysiologyNeedsComponent, dt: float, activity_level: float):
        """更新激素水平"""
        # 皮质醇（压力激素）
        stress_level = needs.fatigue + needs.hunger + needs.thirst
        if stress_level > 0.7:
            needs.hormone_levels['cortisol'] = min(1.0, 
                needs.hormone_levels['cortisol'] + 0.05 * dt)
        else:
            needs.hormone_levels['cortisol'] = max(0.3,
                needs.hormone_levels['cortisol'] - 0.01 * dt)
        
        # 肾上腺素（活动激素）
        if activity_level > 0.8:
            needs.hormone_levels['adrenaline'] = min(1.0,
                needs.hormone_levels['adrenaline'] + 0.1 * dt)
        else:
            needs.hormone_levels['adrenaline'] = max(0.0,
                needs.hormone_levels['adrenaline'] - 0.05 * dt)
        
        # 褪黑素（睡眠激素）
        if needs.sleepiness > 0.7:
            needs.hormone_levels['melatonin'] = min(1.0,
                needs.hormone_levels['melatonin'] + 0.05 * dt)
        else:
            needs.hormone_levels['melatonin'] = max(0.0,
                needs.hormone_levels['melatonin'] - 0.02 * dt)
        
        # 生长激素（修复激素）
        if needs.sleep_stage in [SleepStage.DEEP, SleepStage.REM]:
            needs.hormone_levels['growth_hormone'] = min(1.0,
                needs.hormone_levels['growth_hormone'] + 0.1 * dt)
        else:
            needs.hormone_levels['growth_hormone'] = max(0.3,
                needs.hormone_levels['growth_hormone'] - 0.01 * dt)

    def _check_priority_needs(self, needs: PhysiologyNeedsComponent, intent: IntentComponent):
        """检查需求优先级"""
        priority_needs = []
        
        # 饥饿
        if needs.hunger > 0.8:
            priority_needs.append("hunger")
        
        # 口渴
        if needs.thirst > 0.8:
            priority_needs.append("thirst")
        
        # 疲劳
        if needs.fatigue > 0.8:
            priority_needs.append("fatigue")
        
        # 困倦
        if needs.sleepiness > 0.8:
            priority_needs.append("sleepiness")
        
        # 膀胱
        if needs.bladder > 0.9:
            priority_needs.append("bladder")
        
        # 肠道
        if needs.bowel > 0.9:
            priority_needs.append("bowel")
        
        # 更新优先级需求
        needs.priority_needs = priority_needs
        
        # 根据优先级需求调整意图
        if priority_needs and intent.intent not in [IntentType.SLEEP, IntentType.EAT, IntentType.DRINK]:
            # 根据最紧急的需求调整意图
            if "hunger" in priority_needs:
                intent.intent = IntentType.EAT
            elif "thirst" in priority_needs:
                intent.intent = IntentType.DRINK
            elif "sleepiness" in priority_needs:
                intent.intent = IntentType.SLEEP
            elif "bladder" in priority_needs or "bowel" in priority_needs:
                intent.intent = IntentType.REST

    def get_entity_status(self, entity_id: int) -> Optional[Dict]:
        """获取实体状态"""
        # 这里应该从世界中获取实体组件，简化实现
        return {
            'activity_level': self.activity_levels.get(entity_id, 0.5),
            'is_sleeping': self.sleeping_entities.get(entity_id, False)
        }
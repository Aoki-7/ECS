#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_system.py
@说明:情绪系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional
from core.system import System
from core.world import World
from human.components.cognitive.emotion_component_v4 import EmotionComponent, BasicEmotion, ComplexEmotion
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType

logger = logging.getLogger(__name__)


class EmotionSystem(System):
    """情绪系统 v4.0 - 细化版"""
    tick_interval = 5  # 每5帧更新一次

    def __init__(self):
        self.emotion_contagion_radius = 15.0  # 情绪传染半径
        self.group_emotion_influence = 0.3    # 群体情绪影响

    def update(self, world: World, dt: float):
        """更新情绪系统"""
        # 第一遍：更新个体情绪
        for e, (emotion, human, pos, intent) in world.get_components(
            EmotionComponent, HumanComponent, SpaceComponent, IntentComponent
        ):
            entity_id = e.id
            
            # 更新情绪
            emotion.update_emotions(dt)
            
            # 根据意图调整情绪
            self._adjust_emotion_by_intent(emotion, intent)
            
            # 根据环境调整情绪
            self._adjust_emotion_by_environment(emotion, world, pos)
        
        # 第二遍：处理情绪传染
        self._handle_emotion_contagion(world)

    def _adjust_emotion_by_intent(self, emotion: EmotionComponent, intent: IntentComponent):
        """根据意图调整情绪"""
        if intent.intent == IntentType.SLEEP:
            # 睡眠时增加平静度
            emotion.calmness = min(1.0, emotion.calmness + 0.1)
            emotion.stress = max(0.0, emotion.stress - 0.1)
        
        elif intent.intent == IntentType.EAT:
            # 进食时增加满足感
            emotion.satisfaction = min(1.0, emotion.satisfaction + 0.2)
            emotion.happiness = min(1.0, emotion.happiness + 0.1)
        
        elif intent.intent == IntentType.SOCIALIZE:
            # 社交时增加快乐
            emotion.happiness = min(1.0, emotion.happiness + 0.15)
            emotion.loneliness = max(0.0, emotion.loneliness - 0.2)
        
        elif intent.intent == IntentType.WORK:
            # 工作时增加挫败感（如果工作不顺利）
            if random.random() < 0.3:  # 30%概率工作不顺利
                emotion.frustration = min(1.0, emotion.frustration + 0.1)
        
        elif intent.intent == IntentType.FIGHT:
            # 战斗时增加愤怒和恐惧
            emotion.anger = min(1.0, emotion.anger + 0.3)
            emotion.fear = min(1.0, emotion.fear + 0.2)
        
        elif intent.intent == IntentType.FLEE:
            # 逃跑时增加恐惧
            emotion.fear = min(1.0, emotion.fear + 0.4)

    def _adjust_emotion_by_environment(self, emotion: EmotionComponent, world: World, pos: SpaceComponent):
        """根据环境调整情绪"""
        # 获取环境信息（简化）
        # 实际应用中应该从环境系统获取温度、光照、天气等信息
        
        # 温度影响
        temperature = 25.0  # 假设环境温度
        if temperature < 10:
            # 寒冷环境增加不适
            emotion.disgust = min(1.0, emotion.disgust + 0.05)
        elif temperature > 30:
            # 炎热环境增加不适
            emotion.disgust = min(1.0, emotion.disgust + 0.05)
        
        # 光照影响
        light_level = 0.5  # 假设光照水平
        if light_level < 0.3:
            # 黑暗环境增加恐惧
            emotion.fear = min(1.0, emotion.fear + 0.05)
        elif light_level > 0.8:
            # 明亮环境增加快乐
            emotion.happiness = min(1.0, emotion.happiness + 0.05)
        
        # 天气影响
        weather = "sunny"  # 假设天气
        if weather == "rainy":
            # 雨天增加忧郁
            emotion.sadness = min(1.0, emotion.sadness + 0.05)
        elif weather == "stormy":
            # 暴风雨增加恐惧
            emotion.fear = min(1.0, emotion.fear + 0.1)

    def _handle_emotion_contagion(self, world: World):
        """处理情绪传染"""
        # 获取所有实体
        entities = []
        for e, (emotion, human, pos) in world.get_components(
            EmotionComponent, HumanComponent, SpaceComponent
        ):
            entities.append((e.id, emotion, pos))
        
        # 计算群体情绪
        group_emotion = self._calculate_group_emotion(entities)
        
        # 应用群体情绪影响
        for entity_id, emotion, pos in entities:
            # 查找附近的实体
            nearby_emotions = self._find_nearby_emotions(entities, pos, self.emotion_contagion_radius)
            
            if nearby_emotions:
                # 计算附近实体的平均情绪
                avg_emotion = self._calculate_average_emotion(nearby_emotions)
                
                # 应用情绪传染
                emotion.apply_group_emotion(avg_emotion, self.group_emotion_influence)

    def _calculate_group_emotion(self, entities: List) -> Dict[str, float]:
        """计算群体情绪"""
        if not entities:
            return {}
        
        emotion_sums = {}
        emotion_counts = {}
        
        for _, emotion, _ in entities:
            # 基本情绪
            for emotion_name in ['happiness', 'sadness', 'anger', 'fear', 'surprise', 'disgust']:
                value = getattr(emotion, emotion_name, 0.0)
                emotion_sums[emotion_name] = emotion_sums.get(emotion_name, 0.0) + value
                emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
        
        # 计算平均值
        group_emotion = {}
        for emotion_name, total in emotion_sums.items():
            count = emotion_counts[emotion_name]
            group_emotion[emotion_name] = total / count if count > 0 else 0.0
        
        return group_emotion

    def _find_nearby_emotions(self, entities: List, pos: SpaceComponent, radius: float) -> List:
        """查找附近的情绪"""
        nearby_emotions = []
        
        for entity_id, emotion, other_pos in entities:
            distance = ((pos.x - other_pos.x)**2 + (pos.y - other_pos.y)**2)**0.5
            if distance <= radius:
                nearby_emotions.append(emotion)
        
        return nearby_emotions

    def _calculate_average_emotion(self, emotions: List) -> Dict[str, float]:
        """计算平均情绪"""
        if not emotions:
            return {}
        
        emotion_sums = {}
        emotion_counts = {}
        
        for emotion in emotions:
            # 基本情绪
            for emotion_name in ['happiness', 'sadness', 'anger', 'fear', 'surprise', 'disgust']:
                value = getattr(emotion, emotion_name, 0.0)
                emotion_sums[emotion_name] = emotion_sums.get(emotion_name, 0.0) + value
                emotion_counts[emotion_name] = emotion_counts.get(emotion_name, 0) + 1
        
        # 计算平均值
        avg_emotion = {}
        for emotion_name, total in emotion_sums.items():
            count = emotion_counts[emotion_name]
            avg_emotion[emotion_name] = total / count if count > 0 else 0.0
        
        return avg_emotion

    def get_emotion_statistics(self, world: World) -> Dict:
        """获取情绪统计"""
        total_entities = 0
        happy_entities = 0
        sad_entities = 0
        angry_entities = 0
        fearful_entities = 0
        
        for e, (emotion, human) in world.get_components(EmotionComponent, HumanComponent):
            total_entities += 1
            
            if emotion.happiness > 0.6:
                happy_entities += 1
            if emotion.sadness > 0.6:
                sad_entities += 1
            if emotion.anger > 0.6:
                angry_entities += 1
            if emotion.fear > 0.6:
                fearful_entities += 1
        
        return {
            'total_entities': total_entities,
            'happy_entities': happy_entities,
            'sad_entities': sad_entities,
            'angry_entities': angry_entities,
            'fearful_entities': fearful_entities,
            'happiness_rate': happy_entities / total_entities if total_entities > 0 else 0.0,
            'sadness_rate': sad_entities / total_entities if total_entities > 0 else 0.0,
            'anger_rate': angry_entities / total_entities if total_entities > 0 else 0.0,
            'fear_rate': fearful_entities / total_entities if total_entities > 0 else 0.0
        }

    def get_group_emotion(self, world: World, center: SpaceComponent, radius: float) -> Dict[str, float]:
        """获取群体情绪"""
        emotions = []
        
        for e, (emotion, human, pos) in world.get_components(
            EmotionComponent, HumanComponent, SpaceComponent
        ):
            distance = ((center.x - pos.x)**2 + (center.y - pos.y)**2)**0.5
            if distance <= radius:
                emotions.append(emotion)
        
        return self._calculate_average_emotion(emotions)
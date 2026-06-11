#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_system.py
@说明:情绪系统 v2.0
@时间:2026/05/25
@作者:AI Assistant
@版本:2.0

增强版情绪系统：
- 根据生理状态更新情绪（饥饿→悲伤/愤怒，口渴→压力/恐惧）
- 根据环境更新情绪（极端天气→恐惧/压力）
- 根据行为结果更新情绪（成功→喜悦/希望，失败→挫败/悲伤）
- 根据社交状态更新情绪（孤独→悲伤，社交→快乐）
- 情绪自然衰减和恢复
- 联动记忆系统记录情绪事件
'''

from core.system import System
from core.world import World

from human.components.cognitive.emotion_component import EmotionComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from core.components.action_component import ActionComponent, ActionStatus
from human.components.cognitive.memory_component import MemoryComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus


class EmotionSystem(System):
    tick_interval = 2  # 每2帧执行一次（情绪变化较慢）
    """
    处理情绪变化的系统。
    根据生理状态、环境、行为和社交互动实时调整情绪。
    """

    def update(self, world: World, dt: float):
        current_time = world.get_time().total_hours

        for entity, (emotion, needs, action) in world.get_components(
            EmotionComponent, PhysiologyNeedsComponent, ActionComponent
        ):
            if not emotion or not needs:
                continue

            # 1. 生理状态影响情绪
            self._apply_physiology_effects(emotion, needs, dt)
            
            # 2. 环境耦合影响情绪
            self._apply_environment_effects(emotion, world, entity, dt)
            
            # 3. 行为结果影响情绪
            self._apply_action_effects(emotion, action, dt)
            
            # 4. 社交状态影响情绪
            self._apply_social_effects(emotion, world, entity, dt)
            
            # 5. 情绪自然衰减
            self._apply_natural_decay(emotion, dt)
            
            # 6. 复合情绪更新
            self._update_composite_emotions(emotion)
            
            # 7. 记录重大情绪变化到记忆
            memory = world.get_component(entity, MemoryComponent)
            if memory:
                self._record_emotion_events(emotion, memory, current_time, needs, action)

    def _apply_physiology_effects(self, emotion: EmotionComponent, needs, dt: float):
        """生理需求对情绪的影响"""
        # 极度饥饿 → 愤怒 + 悲伤 + 压力
        if needs.hunger > 80:
            emotion.adjust_emotion("anger", 0.03 * dt)
            emotion.adjust_emotion("sadness", 0.02 * dt)
            emotion.adjust_emotion("stress", 0.04 * dt)
            emotion.adjust_emotion("hope", -0.02 * dt)
        elif needs.hunger > 50:
            emotion.adjust_emotion("sadness", 0.01 * dt)
            emotion.adjust_emotion("stress", 0.01 * dt)
        elif needs.hunger < 20:
            # 吃饱后 → 快乐 + 平静
            emotion.adjust_emotion("happiness", 0.01 * dt)
            emotion.adjust_emotion("calmness", 0.01 * dt)
        
        # 极度口渴 → 恐惧 + 压力 + 挫败
        if needs.thirst > 80:
            emotion.adjust_emotion("fear", 0.04 * dt)
            emotion.adjust_emotion("stress", 0.05 * dt)
            emotion.adjust_emotion("frustration", 0.03 * dt)
            emotion.adjust_emotion("hope", -0.03 * dt)
        elif needs.thirst > 50:
            emotion.adjust_emotion("stress", 0.02 * dt)
        elif needs.thirst < 20:
            emotion.adjust_emotion("happiness", 0.01 * dt)
            emotion.adjust_emotion("calmness", 0.01 * dt)
        
        # 疲劳 → 悲伤 + 压力
        if needs.energy < 20:
            emotion.adjust_emotion("sadness", 0.02 * dt)
            emotion.adjust_emotion("stress", 0.02 * dt)
            emotion.adjust_emotion("excitement", -0.02 * dt)
        elif needs.energy > 70:
            emotion.adjust_emotion("excitement", 0.01 * dt)
            emotion.adjust_emotion("happiness", 0.01 * dt)
        
        # 舒适度影响
        if needs.comfort < 30:
            emotion.adjust_emotion("disgust", 0.01 * dt)
            emotion.adjust_emotion("sadness", 0.01 * dt)

    def _apply_environment_effects(self, emotion: EmotionComponent, world: World, entity, dt: float):
        """环境对情绪的影响"""
        env = world.get_environment()
        if not env:
            return
        
        # 极端温度 → 压力 + 不适
        if env.air_temperature > 35:
            emotion.adjust_emotion("stress", 0.02 * dt)
            emotion.adjust_emotion("disgust", 0.01 * dt)
        elif env.air_temperature < 0:
            emotion.adjust_emotion("fear", 0.01 * dt)
            emotion.adjust_emotion("stress", 0.02 * dt)
        elif 18 <= env.air_temperature <= 26:
            # 舒适温度 → 平静 + 快乐
            emotion.adjust_emotion("calmness", 0.01 * dt)
            emotion.adjust_emotion("happiness", 0.005 * dt)
        
        # 极端湿度
        if env.air_humidity > 0.9:
            emotion.adjust_emotion("disgust", 0.01 * dt)
        
        # 高风速/暴风雨
        if env.wind_speed > 15:
            emotion.adjust_emotion("fear", 0.02 * dt)
            emotion.adjust_emotion("stress", 0.01 * dt)
        
        # 降水
        if hasattr(env, 'rainfall') and env.rainfall > 10:
            emotion.adjust_emotion("sadness", 0.01 * dt)
        
        # 光照（PAR）影响
        if hasattr(env, 'par') and env.par > 800:
            # 阳光明媚 → 快乐
            emotion.adjust_emotion("happiness", 0.01 * dt)
            emotion.adjust_emotion("joy", 0.01 * dt)

    def _apply_action_effects(self, emotion: EmotionComponent, action, dt: float):
        """行为结果对情绪的影响"""
        if not action:
            return
        
        # 成功找到水源/食物 → 喜悦 + 希望
        if action.status == ActionStatus.SUCCESS:
            emotion.adjust_emotion("joy", 0.05)
            emotion.adjust_emotion("hope", 0.03)
            emotion.adjust_emotion("frustration", -0.05)
        
        # 失败 → 挫败 + 悲伤
        elif action.status == ActionStatus.FAILED:
            emotion.adjust_emotion("frustration", 0.05)
            emotion.adjust_emotion("sadness", 0.03)
            emotion.adjust_emotion("anger", 0.02)
            emotion.adjust_emotion("hope", -0.02)

    def _apply_social_effects(self, emotion: EmotionComponent, world: World, entity, dt: float):
        """社交状态对情绪的影响"""
        relation = world.get_component(entity, RelationshipComponent)
        if not relation:
            return
        
        # 已婚/恋爱 → 快乐 + 信任
        if relation.status == RelationshipStatus.MARRIED:
            emotion.adjust_emotion("happiness", 0.005 * dt)
            emotion.adjust_emotion("trust", 0.005 * dt)
            emotion.adjust_emotion("loneliness", -0.01 * dt)
        elif relation.status == RelationshipStatus.SINGLE:
            # 单身时间过长 → 孤独
            emotion.adjust_emotion("loneliness", 0.005 * dt)

    def _apply_natural_decay(self, emotion: EmotionComponent, dt: float):
        """情绪自然衰减"""
        # 愤怒和恐惧自然消退
        emotion.adjust_emotion("anger", -0.005 * dt)
        emotion.adjust_emotion("fear", -0.005 * dt)
        emotion.adjust_emotion("surprise", -0.01 * dt)
        emotion.adjust_emotion("disgust", -0.005 * dt)
        
        # 快乐和喜悦缓慢回落
        emotion.adjust_emotion("joy", -0.003 * dt)
        
        # 悲伤缓慢消退（但比快乐慢）
        emotion.adjust_emotion("sadness", -0.002 * dt)
        
        # 挫败感消退
        emotion.adjust_emotion("frustration", -0.004 * dt)
        
        # 兴奋度回落
        emotion.adjust_emotion("excitement", -0.003 * dt)
        
        # 压力根据平静度缓慢恢复
        if emotion.calmness > 0.5:
            emotion.adjust_emotion("stress", -0.005 * dt)
        
        # 希望缓慢恢复（有下限）
        if emotion.hope < 0.3:
            emotion.adjust_emotion("hope", 0.002 * dt)
        
        # 幸福感向中性回归
        if emotion.happiness > 0.5:
            emotion.adjust_emotion("happiness", -0.002 * dt)
        elif emotion.happiness < 0.3:
            emotion.adjust_emotion("happiness", 0.002 * dt)
        
        # 平静度向中性回归
        if emotion.calmness > 0.6:
            emotion.adjust_emotion("calmness", -0.002 * dt)
        elif emotion.calmness < 0.3:
            emotion.adjust_emotion("calmness", 0.002 * dt)

    def _update_composite_emotions(self, emotion: EmotionComponent):
        """更新复合情绪之间的相互影响"""
        # 高压力抑制快乐
        if emotion.stress > 0.6:
            emotion.adjust_emotion("happiness", -0.01)
            emotion.adjust_emotion("joy", -0.01)
        
        # 高快乐抑制压力和悲伤
        if emotion.happiness > 0.7 or emotion.joy > 0.7:
            emotion.adjust_emotion("stress", -0.01)
            emotion.adjust_emotion("sadness", -0.01)
        
        # 高信任降低恐惧
        if emotion.trust > 0.6:
            emotion.adjust_emotion("fear", -0.01)
        
        # 孤独感积累 → 悲伤
        if emotion.loneliness > 0.5:
            emotion.adjust_emotion("sadness", 0.005)
        
        # 高愤怒抑制信任
        if emotion.anger > 0.6:
            emotion.adjust_emotion("trust", -0.01)
        
        # 挫败感积累 → 愤怒
        if emotion.frustration > 0.6:
            emotion.adjust_emotion("anger", 0.005)

    def _record_emotion_events(self, emotion: EmotionComponent, memory: MemoryComponent,
                                current_time: float, needs, action):
        """记录重大情绪变化到记忆"""
        # 只在情绪极端时记录
        dominant = emotion.get_dominant_emotion()
        
        if dominant == "fear" and emotion.fear > 0.7:
            memory.add_event(
                current_time, "emotion_extreme",
                "感到极度恐惧", impact=-0.8,
                location=getattr(action, 'target_pos', None) if action else None
            )
        elif dominant == "joy" and emotion.joy > 0.7:
            memory.add_event(
                current_time, "emotion_extreme",
                "感到非常喜悦", impact=0.8,
                location=getattr(action, 'target_pos', None) if action else None
            )
        elif dominant == "anger" and emotion.anger > 0.7:
            memory.add_event(
                current_time, "emotion_extreme",
                "感到非常愤怒", impact=-0.6,
                location=getattr(action, 'target_pos', None) if action else None
            )

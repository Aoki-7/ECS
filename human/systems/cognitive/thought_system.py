#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:thought_system.py
@说明:思维系统
@时间:2026/05/25
@作者:AI Assistant
@版本:1.0

根据情绪、生理需求、环境和记忆生成内心独白/思维。
'''

import random

from core.system import System
from core.world import World

from human.components.cognitive.brain_component import BrainComponent
from human.components.cognitive.emotion_component import EmotionComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from core.components.action_component import ActionComponent, ActionType


class ThoughtSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    思维系统
    
    根据当前状态生成内心独白，更新 BrainComponent。
    思维不直接影响行为，但通过情绪和心理状态间接影响决策。
    """

    def update(self, world: World, dt: float):
        for entity, (brain, emotion, needs, action) in world.get_components(
            BrainComponent, EmotionComponent, PhysiologyNeedsComponent, ActionComponent
        ):
            if not brain or not emotion or not needs:
                continue

            thought = self._generate_thought(entity, emotion, needs, action)
            brain.set_thought(thought)
            brain.update_mental_state(emotion.get_mood_score(), emotion.stress)
            
            # 根据行为模式更新
            brain.behavior_mode = self._determine_behavior_mode(action, needs, emotion)

    def _generate_thought(self, entity, emotion: EmotionComponent, 
                          needs: PhysiologyNeedsComponent, action: ActionComponent) -> str:
        """生成内心独白"""
        thoughts = []
        
        # 生理需求驱动的思维
        if needs.thirst > 80:
            thoughts.append("好渴...必须尽快找到水。")
        elif needs.thirst > 50:
            thoughts.append("有点口渴了。")
        
        if needs.hunger > 80:
            thoughts.append("饿得发慌，需要食物。")
        elif needs.hunger > 50:
            thoughts.append("肚子饿了。")
        
        if needs.energy < 20:
            thoughts.append("太累了，好想睡一觉。")
        elif needs.energy < 40:
            thoughts.append("有点疲倦。")
        
        # 情绪驱动的思维
        if emotion.fear > 0.5:
            thoughts.append("我有点害怕...")
        if emotion.anger > 0.5:
            thoughts.append("真是令人恼火！")
        if emotion.joy > 0.5:
            thoughts.append("心情真不错！")
        if emotion.sadness > 0.5:
            thoughts.append("感觉有点难过...")
        if emotion.loneliness > 0.5:
            thoughts.append("好孤独啊，想找人聊聊。")
        if emotion.excitement > 0.4:
            thoughts.append("感觉充满了干劲！")
        if emotion.stress > 0.6:
            thoughts.append("压力好大...")
        if emotion.hope > 0.7:
            thoughts.append("一切都会好起来的。")
        
        # 行为驱动的思维
        if action.current_action == ActionType.SEARCH:
            thoughts.append("让我找找看附近有什么。")
        elif action.current_action == ActionType.MOVE_TO:
            thoughts.append("正在赶路...")
        elif action.current_action == ActionType.EAT:
            thoughts.append("终于可以吃东西了。")
        elif action.current_action == ActionType.DRINK:
            thoughts.append("喝水的感觉真好。")
        elif action.current_action == ActionType.SLEEP:
            thoughts.append("zzZ...")
        elif action.current_action == ActionType.SOCIALIZE:
            thoughts.append("和朋友们在一起真开心。")
        
        # 心情综合思维（低优先级）
        mood = emotion.get_mood_label()
        if mood == "非常开心" and not thoughts:
            thoughts.append("今天真是美好的一天。")
        elif mood == "痛苦" and not thoughts:
            thoughts.append("为什么事情会变成这样...")
        
        # 如果没有特别的想法，随机通用思维
        if not thoughts:
            general_thoughts = [
                "今天天气还不错。",
                "接下来该做什么呢...",
                "希望一切顺利。",
                "活着就是最大的幸福。",
                "世界真大，我想多看看。",
                "也许该做点什么有意义的事。",
            ]
            return random.choice(general_thoughts)
        
        # 返回最强烈的思维（列表中的第一个通常是最紧急的）
        return thoughts[0]

    def _determine_behavior_mode(self, action: ActionComponent, 
                                  needs: PhysiologyNeedsComponent, 
                                  emotion: EmotionComponent) -> str:
        """确定当前行为模式"""
        # 生存优先
        if needs.thirst > 60 or needs.hunger > 60 or needs.energy < 30:
            return "survival"
        # 逃跑
        if emotion.fear > 0.6:
            return "escape"
        # 休息
        if action.current_action == ActionType.SLEEP or needs.energy < 40:
            return "rest"
        # 社交
        if action.current_action == ActionType.SOCIALIZE or emotion.loneliness > 0.5:
            return "social"
        # 工作/收集
        if action.current_action in (ActionType.PICKUP, ActionType.GATHER):
            return "work"
        # 探索
        if action.current_action in (ActionType.SEARCH, ActionType.MOVE_TO):
            return "explore"
        return "idle"

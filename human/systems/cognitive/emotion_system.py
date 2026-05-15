#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_system.py
@说明:情绪系统
@时间:2026/04/15 10:37:00
@作者:Sherry
@版本:1.0
'''




from core.system import System
from core.world import World
from human.components.cognitive.emotion_component import EmotionComponent

class EmotionSystem(System):
    """
    处理情绪变化的系统。
    根据环境刺激调整情绪。
    """

    def update(self, world: World, dt: float):

        for _, (emotion,) in world.get_components(EmotionComponent):
            emotion: EmotionComponent
            
            # 示例逻辑：时间流逝会逐渐减少愤怒和恐惧
            emotion.adjust_emotion("anger", -0.01 * dt)
            emotion.adjust_emotion("fear", -0.01 * dt)

            # 示例逻辑：如果快乐值过低，逐渐增加恐惧
            if emotion.happiness < 0.3:
                emotion.adjust_emotion("fear", 0.02 * dt)
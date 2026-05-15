#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:intent_system.py
@说明:意图系统，用于处理意图识别和意图执行
@时间:2026/04/01 13:59:14
@作者:Sherry
@版本:2.0
'''


from core.system import System
from core.world import World


from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType



class IntentSystem(System):
    """
        意图系统
        从Need -> Intent
        
        优先级：EAT > DRINK > SLEEP > SOCIALIZE > EXPLORE > IDLE
        - 当无紧急需求时，人类会探索周围环境以发现资源
    """
    # 需求触发阈值
    HUNGER_THRESHOLD = 50
    THIRST_THRESHOLD = 50
    ENERGY_THRESHOLD = 40
    SOCIAL_THRESHOLD = 30

    # 紧急权重乘数（用于平局时打破优先级）
    CRITICAL_WEIGHTS = {
        IntentType.SLEEP: 1.3,    # 疲劳危及生命，优先级最高
        IntentType.DRINK: 1.15,   # 脱水比饥饿更快致命
        IntentType.EAT: 1.0,      # 基准
        IntentType.SOCIALIZE: 0.8,
    }

    def _urgency(self, needs: PhysiologyNeedsComponent) -> list[tuple[IntentType, float, str]]:
        """
        计算各需求的紧急程度，返回 (意图类型, 紧急度分值, 描述) 列表。
        分值越高表示越紧急（0.0 ~ 1.0），使用 CRITICAL_WEIGHTS 打破平局。
        """
        candidates = []

        # 饥饿：hunger 越高越紧急
        if needs.hunger > self.HUNGER_THRESHOLD:
            raw = needs.hunger / 100.0
            weight = self.CRITICAL_WEIGHTS[IntentType.EAT]
            candidates.append((IntentType.EAT, raw * weight, f"饥饿={needs.hunger:.0f}"))

        # 口渴：thirst 越高越紧急
        if needs.thirst > self.THIRST_THRESHOLD:
            raw = needs.thirst / 100.0
            weight = self.CRITICAL_WEIGHTS[IntentType.DRINK]
            candidates.append((IntentType.DRINK, raw * weight, f"口渴={needs.thirst:.0f}"))

        # 体力：energy 越低越紧急
        if needs.energy < self.ENERGY_THRESHOLD:
            raw = 1.0 - needs.energy / 100.0
            weight = self.CRITICAL_WEIGHTS[IntentType.SLEEP]
            candidates.append((IntentType.SLEEP, raw * weight, f"疲劳={100-needs.energy:.0f}"))

        # 社交需求
        if needs.social < self.SOCIAL_THRESHOLD:
            raw = (100.0 - needs.social) / 100.0
            weight = self.CRITICAL_WEIGHTS[IntentType.SOCIALIZE]
            candidates.append((IntentType.SOCIALIZE, raw * weight, f"孤独={100-needs.social:.0f}"))

        return candidates

    def update(self, world: World, dt: float):
        for e, [needs, intent] in world.get_components(
            PhysiologyNeedsComponent,
            IntentComponent
            ):

            needs: PhysiologyNeedsComponent
            intent: IntentComponent

            candidates = self._urgency(needs)

            if candidates:
                # 选取紧急度最高的需求
                candidates.sort(key=lambda x: x[1], reverse=True)
                best_intent, best_score, _ = candidates[0]
                intent.intent = best_intent
                intent.priority = best_score
            else:
                # 无紧急需求 → 探索
                intent.intent = IntentType.EXPLORE
                intent.priority = 0.3
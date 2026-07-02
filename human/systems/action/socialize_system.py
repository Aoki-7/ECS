from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:socialize_system.py
@说明:社交系统 v2.0
@时间:2026/05/25
@作者:AI Assistant
@版本:2.0

增强版社交系统：
- 社交互动影响双方情绪
- 记录社交事件到记忆
- 更新关系强度
- 社交质量根据性格和情绪变化
'''

from core.system import System
from core.world import World

from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.systems.physiological.physiology_needs_system import PhysiologyNeedsHelper
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.systems.social.tribe_system import TribeSystem
from human.components.basic.identity_component import IdentityComponent


class SocializeSystem(System):
    tick_interval = 1  # 每帧执行一次，避免社交动作持续过长时间导致生理需求失控
    """
    社交系统
    处理社交行为，增加社会需求满足，影响情绪和记忆。
    """

    # 社交进度速率（5小时完成）
    SOCIALIZE_PROGRESS_RATE = 0.2
    # 基础社交需求恢复量
    SOCIALIZE_NEED_RECOVERY = 30.0
    # 记忆影响系数
    MEMORY_IMPACT_MULTIPLIER = 0.3
    # 情绪调整系数
    HAPPINESS_ADJUSTMENT = 0.1
    JOY_ADJUSTMENT = 0.15
    LONELINESS_ADJUSTMENT = -0.2
    STRESS_ADJUSTMENT = -0.05
    TRUST_ADJUSTMENT = 0.05
    # 同部落质量加成
    TRIBE_QUALITY_BONUS = 0.15
    # 同部落忠诚度加成
    TRIBE_LOYALTY_BONUS = 2.0
    # 关系强度增长
    RELATIONSHIP_STRENGTH_GAIN = 10.0
    # 社交质量计算系数
    QUALITY_BASE = 0.5
    QUALITY_HAPPINESS_FACTOR = 0.2
    QUALITY_JOY_FACTOR = 0.15
    QUALITY_CALMNESS_FACTOR = 0.1
    QUALITY_ANGER_FACTOR = -0.3
    QUALITY_FEAR_FACTOR = -0.2
    QUALITY_SADNESS_FACTOR = -0.15
    QUALITY_LONELINESS_FACTOR = -0.1
    QUALITY_KINDNESS_FACTOR = 0.15
    QUALITY_CURIOSITY_FACTOR = 0.05
    QUALITY_GREED_FACTOR = -0.1
    QUALITY_MIN = 0.1
    QUALITY_MAX = 1.0
    # 记忆信任度系数
    MEMORY_TRUST_BASE = 0.5
    MEMORY_TRUST_QUALITY_FACTOR = 0.2

    def update(self, world: World, dt: float):
        time = world.get_time()
        # 防御：如果 get_time() 返回 None，使用默认值 0.0
        if time is None:
            current_time = 0.0
        else:
            current_time = time.total_hours

        for entity, (needs, action, task) in world.get_components(
            PhysiologyNeedsComponent, ActionComponent, TaskComponent
        ):
            needs: PhysiologyNeedsComponent
            action: ActionComponent
            task: TaskComponent

            if action.current_action != ActionType.SOCIALIZE:
                continue

            # 模拟社交过程
            action.progress += dt * self.SOCIALIZE_PROGRESS_RATE

            if action.progress >= 1.0:
                # 社交完成
                self._complete_socialization(world, entity, needs, action, task, current_time)

    def _complete_socialization(self, world: World, entity, needs, action, task, current_time: float):
        """完成社交互动"""
        # 基础社交需求恢复
        PhysiologyNeedsHelper.add_social(needs, self.SOCIALIZE_NEED_RECOVERY)

        # 获取相关组件
        emotion = world.get_component(entity, EmotionComponent)
        memory = world.get_component(entity, MemoryComponent)
        personality = world.get_component(entity, PersonalityComponent)
        relation = world.get_component(entity, RelationshipComponent)
        identity = world.get_component(entity, IdentityComponent)
        membership = world.get_component(entity, TribeMembershipComponent)
        
        # 计算社交质量（基于性格和情绪）
        quality = self._calculate_social_quality(emotion, personality)
        
        # 同部落社交加成
        if action.target_entity is not None:
            target = world.query_entity(action.target_entity)
            if target:
                target_membership = world.get_component(target, TribeMembershipComponent)
                if (membership and target_membership and 
                    membership.tribe_id is not None and 
                    membership.tribe_id == target_membership.tribe_id):
                    quality = min(self.QUALITY_MAX, quality + self.TRIBE_QUALITY_BONUS)
                    # 增加忠诚度
                    TribeSystem.add_loyalty(membership, self.TRIBE_LOYALTY_BONUS)
                    if target_membership:
                        TribeSystem.add_loyalty(target_membership, self.TRIBE_LOYALTY_BONUS)

        # 影响情绪
        if emotion:
            emotion.adjust_emotion("happiness", self.HAPPINESS_ADJUSTMENT * quality)
            emotion.adjust_emotion("joy", self.JOY_ADJUSTMENT * quality)
            emotion.adjust_emotion("loneliness", self.LONELINESS_ADJUSTMENT * quality)
            emotion.adjust_emotion("stress", self.STRESS_ADJUSTMENT * quality)
            emotion.adjust_emotion("trust", self.TRUST_ADJUSTMENT * quality)
            emotion.last_mood_change = "社交互动"

        # 记录到记忆
        if memory:
            desc = f"与伙伴进行了愉快的社交" if quality > 0.5 else "进行了社交互动"
            MemoryManagementSystem.add_event(memory, 
                current_time, "socialized", desc,
                impact=self.MEMORY_IMPACT_MULTIPLIER * quality,
                location=getattr(action, 'target_pos', None)
            )
            MemoryManagementSystem.record_success(memory, "socialize")

        # 如果有目标实体，更新双方关系
        if action.target_entity is not None:
            target = world.query_entity(action.target_entity)
            if target:
                self._update_mutual_relationship(world, entity, target, quality, current_time)

        # 标记完成
        action.progress = 1.0
        action.status = ActionStatus.SUCCESS
        task.status = TaskStatus.DONE

    def _calculate_social_quality(self, emotion: EmotionComponent, 
                                   personality: PersonalityComponent) -> float:
        """
        计算社交互动质量 (0-1)
        
        影响因素：
        - 情绪状态（快乐/平静促进，愤怒/恐惧抑制）
        - 性格（善良/好奇心促进，贪婪抑制）
        """
        quality = self.QUALITY_BASE

        if emotion:
            quality += emotion.happiness * self.QUALITY_HAPPINESS_FACTOR
            quality += emotion.joy * self.QUALITY_JOY_FACTOR
            quality += emotion.calmness * self.QUALITY_CALMNESS_FACTOR
            quality -= emotion.anger * self.QUALITY_ANGER_FACTOR
            quality -= emotion.fear * self.QUALITY_FEAR_FACTOR
            quality -= emotion.sadness * self.QUALITY_SADNESS_FACTOR
            quality -= emotion.loneliness * self.QUALITY_LONELINESS_FACTOR

        if personality:
            quality += personality.kindness * self.QUALITY_KINDNESS_FACTOR
            quality += personality.curiosity * self.QUALITY_CURIOSITY_FACTOR
            quality -= personality.greed * self.QUALITY_GREED_FACTOR

        return max(self.QUALITY_MIN, min(self.QUALITY_MAX, quality))

    def _update_mutual_relationship(self, world: World, entity1, entity2, 
                                     quality: float, current_time: float):
        """更新双方关系"""
        # 更新实体1的关系
        relation1 = world.get_component(entity1, RelationshipComponent)
        if relation1:
            relation1.relationship_strength = min(100.0,
                relation1.relationship_strength + self.RELATIONSHIP_STRENGTH_GAIN * quality)
        
        # 更新实体2的关系
        relation2 = world.get_component(entity2, RelationshipComponent)
        if relation2:
            relation2.relationship_strength = min(100.0,
                relation2.relationship_strength + self.RELATIONSHIP_STRENGTH_GAIN * quality)
        
        # 记录人物记忆
        memory1 = world.get_component(entity1, MemoryComponent)
        memory2 = world.get_component(entity2, MemoryComponent)
        identity1 = world.get_component(entity1, IdentityComponent)
        identity2 = world.get_component(entity2, IdentityComponent)
        
        name1 = identity1.name if identity1 else f"Human_{entity1.id}"
        name2 = identity2.name if identity2 else f"Human_{entity2.id}"
        
        if memory1:
            MemoryManagementSystem.record_person(memory1, 
                entity2.id, name2, current_time,
                relationship="friend", trust=self.MEMORY_TRUST_BASE + self.MEMORY_TRUST_QUALITY_FACTOR * quality
            )
        
        if memory2:
            MemoryManagementSystem.record_person(memory2, 
                entity1.id, name1, current_time,
                relationship="friend", trust=0.5 + 0.2 * quality
            )

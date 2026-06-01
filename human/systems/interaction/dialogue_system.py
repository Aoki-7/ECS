#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
对话系统 - 处理实体间的交互对话
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random

from core.system import System
from core.world import World

from human.components.social.dialogue_component import DialogueComponent
from core.components.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.memory_component import MemoryComponent


# 预定义的话题和功能回应
RESPONSE_CATEGORIES = {
    "personal": [
        "个人经历", "成长背景", "家庭情况", "教育经历", "工作经历"
    ],
    "interests": [
        "兴趣爱好", "喜欢的活动", "擅长的事物", "理想职业"
    ],
    "social": [
        "朋友关系", "社交偏好", "聚会习惯", "社区参与"
    ]
}


@dataclass
class DialogueContext:
    """对话上下文"""
    participants: List[int] = field(default_factory=list)
    topic: str = ""
    sentiment: float = 0.0  # -1 负面, 0 中性, +1 正面
    trust_level: float = 0.0
    shared_history: List[str] = field(default_factory=list)
    
    def add_participant(self, entity_id: int):
        if entity_id not in self.participants:
            self.participants.append(entity_id)
    
    def remove_participant(self, entity_id: int):
        self.participants.remove(entity_id) if entity_id in self.participants else None
    
    def is_active(self) -> bool:
        return len(self.participants) > 0


@dataclass 
class DialogueTurn:
    """对话轮次记录"""
    turn序号: int
    speakers: List[int]
    topics: List[str]
    sentiment: float
    key_points: List[str]
    summary: str
    
    @classmethod
    def generate(cls, context: DialogueContext, speaker: int) -> "DialogueTurn":
        """生成对话回合"""
        all_turns = getattr(cls, '_all_turns', [])
        return cls(
            turn序号=len(all_turns) + 1,
            speakers=list(context.participants),
            topics=[context.topic] if context.topic else [],
            sentiment=context.sentiment,
            key_points=[],
            summary=f"[对话记录] {context.topic} 讨论"
        )


class DialogueSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    对话系统 - 管理实体间对话交互（ECS 版）
    
    功能：
    - 话题识别和转换
    - 情感回应生成
    - 信任度计算
    - 对话历史管理
    """
    
    def __init__(self):
        super().__init__()
        self.active_dialogue: Optional[DialogueContext] = None
        self.turn_history: List[DialogueTurn] = []
        self.knowledge_base: Dict[str, str] = {}  # 实体知识库
    
    def start_conversation(self, topic: str, participants: Optional[List[int]] = None) -> DialogueContext:
        """开始新对话"""
        context = DialogueContext(
            topic=topic,
            sentiment=0.0,
            trust_level=0.0 if participants else 5.0
        )
        if participants:
            for p in participants:
                context.add_participant(p)
        self.active_dialogue = context
        return context
    
    def add_speaker(self, entity_id: int):
        """添加对话参与者"""
        if self.active_dialogue:
            self.active_dialogue.add_participant(entity_id)
    
    def respond_to_message(self, message: str, from_entity: int) -> str:
        """
        生成分角色回复
        
        Args:
            message: 用户消息/输入
            
        Returns:
            合适的回应文本
        """
        if not self.active_dialogue:
            return "请先开始对话"
        
        # 简单关键词匹配来生成回应
        keywords = [
            ["hello", "hi", "hey", "你好", "在吗"],
            ["how are you", "感觉如何", "怎么样"],
            ["what do you think", "你怎么看", "认为"],
            ["thank", "谢谢", "感谢"],
            ["sorry", "抱歉", "对不起"]
        ]
        
        message_lower = message.lower()
        
        for category, keywords_list in keywords:
            if any(kw in message_lower for kw in keywords_list):
                self._handle_specific_response(message, from_entity, category)
                break
        
        # 如果没匹配到关键词，生成一般回应
        return self._generate_general_response(message)
    
    def _handle_specific_response(self, message: str, speaker: int, category: str) -> str:
        """处理特定类型的回复"""
        responses = {
            "personal": [
                "这让我想到我自己的经历...",
                "说实话，我的家庭背景很简单...",
                "我刚从大学毕业不久。"
            ],
            "interests": [
                "我非常喜欢编程和游戏！",
                "业余时间我喜欢尝试新的烹饪食谱.",
                "我对音乐很热爱。"
            ],
            "social": [
                "我不太擅长社交场合，但朋友都很好。",
                "我喜欢参加社区活动，认识新朋友。",
                "周末我通常会和家人在一起。"
            ]
        }
        
        response_list = responses.get(category, [""])
        if response_list:
            self.active_dialogue.sentiment += random.uniform(-0.2, 0.3)
            return random.choice(response_list)
        return ""
    
    def _generate_general_response(self, message: str) -> str:
        """生成一般性回应"""
        # 简单基于关键词的回应
        if any(w in message.lower() for w in ["hello", "hi", "hey"]):
            return "你好！最近过得怎么样？"
        elif any(w in message.lower() for w in ["thank", "thanks", "感谢"]):
            return "不客气，很高兴能帮你。"
        elif any(w in message.lower() for w in ["sorry", "apologize", "抱歉"]):
            return "没关系，理解你的感受。"
        else:
            # 默认回应
            generic_responses = [
                "我在听。你能告诉我更多吗？",
                "这个观点很有意思。",
                "我正在思考你说的...",
                "这真是个值得讨论的话题。"
            ]
            return random.choice(generic_responses)
    
    def update_context(self, message: str, sentiment: float = None):
        """更新对话上下文"""
        if self.active_dialogue and sentiment:
            self.active_dialogue.sentiment = max(-1, min(1, 
                self.active_dialogue.sentiment + sentiment * 0.1))
    
    def save_turn(self, context: DialogueContext, speakers: List[int], topics: List[str]):
        """保存对话轮次记录"""
        if not self.turn_history:
           DialogueTurn._all_turns = []
        
        turn = DialogueTurn(
            turn序号=len(self.turn_history) + 1,
            speakers=speakers,
            topics=topics,
            sentiment=context.sentiment if context else 0.0,
            key_points=[],
            summary="".join(context.shared_history) if context else ""
        )
        self.turn_history.append(turn)

    def update(self, world: World, dt: float = 0.0):
        """系统更新：处理当前处于 TALK/INTERACT 状态的实体"""
        for entity, (action, dialogue) in world.get_components(
            ActionComponent, DialogueComponent
        ):
            action: ActionComponent
            dialogue: DialogueComponent

            if action.current_action not in (ActionType.TALK, ActionType.INTERACT):
                continue

            if not dialogue.is_talking:
                dialogue.is_talking = True
                dialogue.turn_count = 0

            # 对话进度推进
            action.progress += dt * 0.2
            dialogue.turn_count += 1

            if action.progress >= 1.0:
                # 对话完成
                action.progress = 1.0
                action.status = ActionStatus.SUCCESS
                dialogue.is_talking = False

                # 记录到记忆
                memory = world.get_component(entity, MemoryComponent)
                if memory and dialogue.target_entity_id is not None:
                    current_time = world.get_time().total_hours
                    memory.add_event(
                        current_time, "dialogue",
                        f"与 {dialogue.target_entity_id} 进行了对话",
                        impact=dialogue.sentiment * 0.3,
                    )

                # 清理对话状态
                dialogue.target_entity_id = None
                dialogue.topic = ""
                dialogue.sentiment = 0.0

if __name__ == "__main__":
    import logging
    logging.getLogger(__name__).debug("对话系统已加载")
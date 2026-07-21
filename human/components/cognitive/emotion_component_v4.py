#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from core.component import Component
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum, auto


class EmotionIntensity(Enum):
    """情绪强度"""
    MILD = auto()       # 轻微
    MODERATE = auto()   # 中等
    STRONG = auto()     # 强烈
    EXTREME = auto()    # 极端


class EmotionDuration(Enum):
    """情绪持续时间"""
    BRIEF = auto()      # 短暂（几分钟）
    SHORT = auto()      # 短期（几小时）
    MEDIUM = auto()     # 中期（几天）
    LONG = auto()       # 长期（几周）
    CHRONIC = auto()    # 慢性（几个月）


class BasicEmotion(Enum):
    """基本情绪"""
    HAPPINESS = auto()  # 快乐
    SADNESS = auto()    # 悲伤
    ANGER = auto()      # 愤怒
    FEAR = auto()       # 恐惧
    SURPRISE = auto()   # 惊讶
    DISGUST = auto()    # 厌恶


class ComplexEmotion(Enum):
    """复合情绪"""
    ANXIETY = auto()        # 焦虑
    DEPRESSION = auto()     # 抑郁
    EXCITEMENT = auto()     # 兴奋
    FRUSTRATION = auto()    # 沮丧
    SATISFACTION = auto()   # 满足
    JEALOUSY = auto()       # 嫉妒
    GUILT = auto()          # 内疚
    SHAME = auto()          # 羞耻
    PRIDE = auto()          # 自豪
    HOPE = auto()           # 希望
    DESPAIR = auto()        # 绝望
    LONELINESS = auto()     # 孤独
    LOVE = auto()           # 爱
    HATE = auto()           # 恨


@dataclass(slots=True)
class EmotionState:
    """情绪状态"""
    emotion_type: Enum
    intensity: float = 0.0          # 强度 (0-1)
    duration: float = 0.0           # 持续时间（小时）
    trigger: Optional[str] = None   # 触发因素
    target: Optional[int] = None    # 目标实体ID
    
    def get_intensity_level(self) -> EmotionIntensity:
        """获取强度等级"""
        if self.intensity < 0.3:
            return EmotionIntensity.MILD
        elif self.intensity < 0.6:
            return EmotionIntensity.MODERATE
        elif self.intensity < 0.8:
            return EmotionIntensity.STRONG
        else:
            return EmotionIntensity.EXTREME
    
    def get_duration_level(self) -> EmotionDuration:
        """获取持续时间等级"""
        if self.duration < 0.1:
            return EmotionDuration.BRIEF
        elif self.duration < 1.0:
            return EmotionDuration.SHORT
        elif self.duration < 24.0:
            return EmotionDuration.MEDIUM
        elif self.duration < 168.0:  # 一周
            return EmotionDuration.LONG
        else:
            return EmotionDuration.CHRONIC


@dataclass(slots=True)
class EmotionComponent(Component):
    """
    情绪组件 v4.0 - 细化版
    包括基本情绪、复合情绪、情绪强度、持续时间、情绪影响等细化功能。
    """
    
    # === 基本情绪 (0-1) ===
    happiness: float = 0.5   # 快乐程度
    anger: float = 0.0       # 愤怒程度
    fear: float = 0.0        # 恐惧程度
    joy: float = 0.0         # 喜悦程度
    sadness: float = 0.0     # 悲伤程度
    disgust: float = 0.0     # 厌恶程度
    surprise: float = 0.0    # 惊讶程度

    # === 复合情绪 (0-1) ===
    anxiety: float = 0.0         # 焦虑
    depression: float = 0.0      # 抑郁
    excitement: float = 0.0      # 兴奋
    frustration: float = 0.0     # 沮丧
    satisfaction: float = 0.5    # 满足
    jealousy: float = 0.0        # 嫉妒
    guilt: float = 0.0           # 内疚
    shame: float = 0.0           # 羞耻
    pride: float = 0.0           # 自豪
    hope: float = 0.5            # 希望
    despair: float = 0.0         # 绝望
    loneliness: float = 0.0      # 孤独
    love: float = 0.0            # 爱
    hate: float = 0.0            # 恨

    # === 情绪状态 ===
    current_emotions: Dict[str, EmotionState] = field(default_factory=dict)  # 当前情绪状态
    emotion_history: List[EmotionState] = field(default_factory=list)        # 情绪历史
    max_history_length: int = 100

    # === 情绪影响 ===
    stress: float = 0.0      # 压力（口渴+饥饿+疲劳综合）
    calmness: float = 0.5    # 平静度
    trust: float = 0.5       # 对周围环境的信任
    mood: float = 0.5        # 心情（整体情绪状态）

    # === 情绪调节 ===
    emotion_regulation: float = 0.5  # 情绪调节能力 (0-1)
    emotional_stability: float = 0.5  # 情绪稳定性 (0-1)
    emotional_intelligence: float = 0.5  # 情绪智力 (0-1)

    # === 情绪传染 ===
    emotional_contagion: float = 0.5  # 情绪传染敏感度 (0-1)
    group_emotion_influence: float = 0.0  # 群体情绪影响 (0-1)

    # === 情绪变化记录 ===
    last_mood_change: str = ""  # 上次情绪变化原因
    mood_change_history: List[Dict] = field(default_factory=list)  # 情绪变化历史

    def get_overall_mood(self) -> float:
        """获取整体心情 (0-1)"""
        # 基本情绪权重
        basic_emotions = [
            self.happiness, self.joy, self.sadness, 
            self.anger, self.fear, self.surprise, self.disgust
        ]
        basic_avg = sum(basic_emotions) / len(basic_emotions)
        
        # 复合情绪权重
        complex_emotions = [
            self.satisfaction, self.hope, self.excitement,
            self.anxiety, self.depression, self.frustration
        ]
        complex_avg = sum(complex_emotions) / len(complex_emotions)
        
        # 综合计算
        return (basic_avg * 0.6 + complex_avg * 0.4)

    def get_emotional_state(self) -> str:
        """获取情绪状态描述"""
        mood = self.get_overall_mood()
        
        if mood < 0.3:
            return "非常低落"
        elif mood < 0.5:
            return "低落"
        elif mood < 0.7:
            return "一般"
        elif mood < 0.9:
            return "良好"
        else:
            return "非常好"

    def add_emotion(self, emotion_type: Enum, intensity: float, 
                    trigger: Optional[str] = None, target: Optional[int] = None):
        """添加情绪"""
        emotion_name = emotion_type.name if hasattr(emotion_type, 'name') else str(emotion_type)
        
        emotion_state = EmotionState(
            emotion_type=emotion_type,
            intensity=intensity,
            duration=0.0,
            trigger=trigger,
            target=target
        )
        
        self.current_emotions[emotion_name] = emotion_state
        
        # 更新对应的情绪值
        self._update_emotion_value(emotion_type, intensity)
        
        # 记录情绪变化
        self._record_emotion_change(emotion_type, intensity, trigger)

    def _update_emotion_value(self, emotion_type: Enum, intensity: float):
        """更新情绪值"""
        emotion_name = emotion_type.name if hasattr(emotion_type, 'name') else str(emotion_type)
        
        # 基本情绪
        if emotion_name == 'HAPPINESS':
            self.happiness = intensity
        elif emotion_name == 'ANGER':
            self.anger = intensity
        elif emotion_name == 'FEAR':
            self.fear = intensity
        elif emotion_name == 'JOY':
            self.joy = intensity
        elif emotion_name == 'SADNESS':
            self.sadness = intensity
        elif emotion_name == 'DISGUST':
            self.disgust = intensity
        elif emotion_name == 'SURPRISE':
            self.surprise = intensity
        
        # 复合情绪
        elif emotion_name == 'ANXIETY':
            self.anxiety = intensity
        elif emotion_name == 'DEPRESSION':
            self.depression = intensity
        elif emotion_name == 'EXCITEMENT':
            self.excitement = intensity
        elif emotion_name == 'FRUSTRATION':
            self.frustration = intensity
        elif emotion_name == 'SATISFACTION':
            self.satisfaction = intensity
        elif emotion_name == 'JEALOUSY':
            self.jealousy = intensity
        elif emotion_name == 'GUILT':
            self.guilt = intensity
        elif emotion_name == 'SHAME':
            self.shame = intensity
        elif emotion_name == 'PRIDE':
            self.pride = intensity
        elif emotion_name == 'HOPE':
            self.hope = intensity
        elif emotion_name == 'DESPAIR':
            self.despair = intensity
        elif emotion_name == 'LONELINESS':
            self.loneliness = intensity
        elif emotion_name == 'LOVE':
            self.love = intensity
        elif emotion_name == 'HATE':
            self.hate = intensity

    def _record_emotion_change(self, emotion_type: Enum, intensity: float, trigger: Optional[str]):
        """记录情绪变化"""
        emotion_name = emotion_type.name if hasattr(emotion_type, 'name') else str(emotion_type)
        
        change_record = {
            'emotion': emotion_name,
            'intensity': intensity,
            'trigger': trigger,
            'timestamp': 0.0  # 实际应用中应该使用真实时间戳
        }
        
        self.mood_change_history.append(change_record)
        
        # 限制历史记录长度
        if len(self.mood_change_history) > self.max_history_length:
            self.mood_change_history = self.mood_change_history[-self.max_history_length:]
        
        # 更新上次情绪变化原因
        self.last_mood_change = f"{emotion_name}: {trigger}" if trigger else emotion_name

    def update_emotions(self, dt: float):
        """更新情绪状态"""
        # 更新当前情绪持续时间
        emotions_to_remove = []
        for emotion_name, emotion_state in self.current_emotions.items():
            emotion_state.duration += dt
            
            # 情绪自然衰减
            decay_rate = 0.1 * (1.0 - self.emotion_regulation)
            emotion_state.intensity = max(0.0, emotion_state.intensity - decay_rate * dt)
            
            # 如果情绪强度降到很低，移除该情绪
            if emotion_state.intensity < 0.1:
                emotions_to_remove.append(emotion_name)
        
        # 移除已衰减的情绪
        for emotion_name in emotions_to_remove:
            del self.current_emotions[emotion_name]
        
        # 更新基本情绪（向中性值回归）
        neutral_value = 0.5
        regression_rate = 0.05 * dt
        
        self.happiness = self._regress_to_neutral(self.happiness, neutral_value, regression_rate)
        self.anger = self._regress_to_neutral(self.anger, 0.0, regression_rate)
        self.fear = self._regress_to_neutral(self.fear, 0.0, regression_rate)
        self.sadness = self._regress_to_neutral(self.sadness, 0.0, regression_rate)
        self.surprise = self._regress_to_neutral(self.surprise, 0.0, regression_rate)
        
        # 更新复合情绪
        self.anxiety = self._regress_to_neutral(self.anxiety, 0.0, regression_rate)
        self.depression = self._regress_to_neutral(self.depression, 0.0, regression_rate)
        self.excitement = self._regress_to_neutral(self.excitement, 0.0, regression_rate)
        self.frustration = self._regress_to_neutral(self.frustration, 0.0, regression_rate)
        
        # 更新心情
        self.mood = self.get_overall_mood()
        
        # 更新压力（根据负面情绪）
        negative_emotions = [self.anger, self.fear, self.sadness, self.anxiety, self.frustration]
        self.stress = sum(negative_emotions) / len(negative_emotions)
        
        # 更新平静度
        self.calmness = 1.0 - self.stress

    def _regress_to_neutral(self, current: float, neutral: float, rate: float) -> float:
        """向中性值回归"""
        if current > neutral:
            return max(neutral, current - rate)
        else:
            return min(neutral, current + rate)

    def get_emotion_impact_on_behavior(self) -> Dict[str, float]:
        """获取情绪对行为的影响"""
        return {
            'decision_quality': self.calmness * (1.0 - self.stress),
            'social_interaction': self.happiness * (1.0 - self.loneliness),
            'work_efficiency': self.satisfaction * (1.0 - self.frustration),
            'risk_taking': self.excitement * (1.0 - self.fear),
            'creativity': self.joy * (1.0 - self.depression),
            'cooperation': self.trust * (1.0 - self.anger)
        }

    def get_emotion_impact_on_health(self) -> Dict[str, float]:
        """获取情绪对健康的影响"""
        return {
            'immune_system': self.calmness * (1.0 - self.stress),
            'recovery_rate': self.hope * (1.0 - self.despair),
            'pain_tolerance': self.emotional_stability * (1.0 - self.anxiety),
            'sleep_quality': self.calmness * (1.0 - self.excitement),
            'appetite': self.happiness * (1.0 - self.depression)
        }

    def apply_group_emotion(self, group_emotion: Dict[str, float], influence: float = 0.5):
        """应用群体情绪影响"""
        # 情绪传染
        contagion_factor = self.emotional_contagion * influence
        
        for emotion_name, group_intensity in group_emotion.items():
            current_intensity = getattr(self, emotion_name.lower(), 0.0)
            
            # 向群体情绪靠拢
            new_intensity = current_intensity + (group_intensity - current_intensity) * contagion_factor
            
            # 更新情绪值
            setattr(self, emotion_name.lower(), new_intensity)
        
        # 更新群体情绪影响
        self.group_emotion_influence = influence

    def get_emotional_summary(self) -> Dict:
        """获取情绪摘要"""
        return {
            'overall_mood': self.mood,
            'emotional_state': self.get_emotional_state(),
            'stress_level': self.stress,
            'calmness': self.calmness,
            'current_emotions': {name: state.intensity for name, state in self.current_emotions.items()},
            'emotion_count': len(self.current_emotions),
            'dominant_emotion': max(self.current_emotions.items(), key=lambda x: x[1].intensity)[0] if self.current_emotions else None
        }

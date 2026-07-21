#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:physiology_needs_component.py
@说明:生理需求组件 v3.0 - 细化版
@时间:2026/07/19
@版本:3.0
'''

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum, auto

from core.component import Component


class SleepStage(Enum):
    """睡眠阶段"""
    AWAKE = auto()      # 清醒
    LIGHT = auto()      # 浅睡
    DEEP = auto()       # 深睡
    REM = auto()        # 快速眼动


class FatigueType(Enum):
    """疲劳类型"""
    MUSCLE = auto()     # 肌肉疲劳
    MENTAL = auto()     # 精神疲劳
    EYE = auto()        # 眼疲劳


@dataclass(slots=True)
class PhysiologyNeedsComponent(Component):
    """
    生理需求组件 v3.0 - 细化版
    存储生理需求状态，包括营养、代谢、睡眠等细化功能。
    """
    
    # === 基本需求 (0-1) ===
    hunger: float = 0.0
    thirst: float = 0.0
    sleepiness: float = 0.0
    fatigue: float = 0.0
    
    # === 营养系统 (0-1) ===
    protein: float = 0.5        # 蛋白质
    carbohydrate: float = 0.5   # 碳水化合物
    fat: float = 0.5            # 脂肪
    vitamin: float = 0.5        # 维生素
    mineral: float = 0.5        # 矿物质
    
    # === 代谢系统 ===
    basal_metabolic_rate: float = 1500.0  # 基础代谢率（卡路里/天）
    energy_expenditure: float = 0.0       # 当前能量消耗
    body_temperature: float = 37.0        # 体温（摄氏度）
    
    # === 排泄系统 (0-1) ===
    bladder: float = 0.0        # 膀胱
    bowel: float = 0.0          # 肠道
    sweat: float = 0.0          # 出汗
    
    # === 呼吸系统 ===
    oxygen_level: float = 1.0   # 血氧水平
    breathing_rate: float = 12.0  # 呼吸频率（次/分钟）
    
    # === 循环系统 ===
    heart_rate: float = 60.0    # 心率（次/分钟）
    blood_pressure_systolic: float = 120.0   # 收缩压
    blood_pressure_diastolic: float = 80.0   # 舒张压
    
    # === 疲劳细化 ===
    muscle_fatigue: float = 0.0     # 肌肉疲劳
    mental_fatigue: float = 0.0     # 精神疲劳
    eye_fatigue: float = 0.0        # 眼疲劳
    
    # === 睡眠细化 ===
    sleep_stage: SleepStage = SleepStage.AWAKE  # 当前睡眠阶段
    sleep_quality: float = 0.5      # 睡眠质量 (0-1)
    sleep_duration: float = 0.0     # 当前睡眠时长（小时）
    sleep_debt: float = 0.0         # 睡眠债务（小时）
    
    # === 饮食细化 ===
    hunger_sensation: float = 0.0   # 饥饿感
    satiety: float = 0.5            # 饱腹感
    thirst_sensation: float = 0.0   # 口渴感
    appetite: float = 0.5           # 食欲
    
    # === 兼容旧系统 ===
    energy: float = 100.0
    social: float = 50.0
    max_hunger: float = 100.0
    max_thirst: float = 100.0
    max_energy: float = 100.0
    max_fatigue: float = 100.0
    max_comfort: float = 100.0
    max_social: float = 100.0
    comfort: float = 0.5
    temperature_comfort: float = 0.5
    hygiene: float = 0.5
    cleanliness: float = 0.5
    health: float = 1.0
    pain: float = 0.0
    priority_needs: List[str] = field(default_factory=list)
    
    # === 新增字段 ===
    # 营养需求
    nutritional_needs: Dict[str, float] = field(default_factory=lambda: {
        'protein': 0.5,
        'carbohydrate': 0.5,
        'fat': 0.5,
        'vitamin': 0.5,
        'mineral': 0.5
    })
    
    # 代谢状态
    metabolic_state: Dict[str, float] = field(default_factory=lambda: {
        'glucose': 0.5,      # 血糖
        'insulin': 0.5,      # 胰岛素
        'glycogen': 0.5,     # 糖原
        'ketones': 0.0       # 酮体
    })
    
    # 体温调节
    temperature_regulation: Dict[str, float] = field(default_factory=lambda: {
        'shivering': 0.0,    # 寒战
        'sweating': 0.0,     # 出汗
        'vasodilation': 0.5, # 血管扩张
        'vasoconstriction': 0.5  # 血管收缩
    })
    
    # 免疫系统状态
    immune_status: Dict[str, float] = field(default_factory=lambda: {
        'innate_immunity': 0.5,      # 先天免疫
        'acquired_immunity': 0.5,    # 获得性免疫
        'inflammation': 0.0,         # 炎症
        'antibody_level': 0.5        # 抗体水平
    })
    
    # 激素水平
    hormone_levels: Dict[str, float] = field(default_factory=lambda: {
        'cortisol': 0.5,     # 皮质醇（压力激素）
        'adrenaline': 0.0,   # 肾上腺素
        'melatonin': 0.0,    # 褪黑素
        'growth_hormone': 0.5,  # 生长激素
        'insulin': 0.5       # 胰岛素
    })
    
    def get_overall_health(self) -> float:
        """获取整体健康评分 (0-1)"""
        # 综合考虑各项指标
        nutrition_score = (
            self.protein + self.carbohydrate + self.fat + 
            self.vitamin + self.mineral
        ) / 5.0
        
        physiological_score = (
            self.oxygen_level + (1.0 - abs(self.body_temperature - 37.0) / 10.0) +
            (1.0 - abs(self.heart_rate - 60.0) / 100.0) +
            (1.0 - abs(self.blood_pressure_systolic - 120.0) / 100.0)
        ) / 4.0
        
        fatigue_score = 1.0 - (
            self.muscle_fatigue + self.mental_fatigue + self.eye_fatigue
        ) / 3.0
        
        return (nutrition_score + physiological_score + fatigue_score + self.health) / 4.0
    
    def get_nutritional_status(self) -> str:
        """获取营养状态描述"""
        avg_nutrition = (
            self.protein + self.carbohydrate + self.fat + 
            self.vitamin + self.mineral
        ) / 5.0
        
        if avg_nutrition < 0.3:
            return "严重营养不良"
        elif avg_nutrition < 0.5:
            return "营养不良"
        elif avg_nutrition < 0.7:
            return "营养一般"
        elif avg_nutrition < 0.9:
            return "营养良好"
        else:
            return "营养优秀"
    
    def get_sleep_status(self) -> str:
        """获取睡眠状态描述"""
        if self.sleep_stage == SleepStage.AWAKE:
            if self.sleepiness < 0.3:
                return "精神饱满"
            elif self.sleepiness < 0.6:
                return "轻微困倦"
            else:
                return "非常困倦"
        elif self.sleep_stage == SleepStage.LIGHT:
            return "浅睡中"
        elif self.sleep_stage == SleepStage.DEEP:
            return "深睡中"
        else:  # REM
            return "快速眼动睡眠中"
    
    def get_fatigue_status(self) -> str:
        """获取疲劳状态描述"""
        max_fatigue = max(self.muscle_fatigue, self.mental_fatigue, self.eye_fatigue)
        
        if max_fatigue < 0.3:
            return "精力充沛"
        elif max_fatigue < 0.6:
            return "轻微疲劳"
        elif max_fatigue < 0.8:
            return "中度疲劳"
        else:
            return "极度疲劳"
    
    def update_metabolism(self, dt: float, activity_level: float = 1.0):
        """更新代谢状态"""
        # 基础代谢消耗
        basal_consumption = self.basal_metabolic_rate * dt / 24.0
        
        # 活动消耗
        activity_consumption = basal_consumption * activity_level
        
        # 更新能量消耗
        self.energy_expenditure += activity_consumption
        
        # 更新血糖
        glucose_consumption = activity_consumption / 1000.0  # 简化计算
        self.metabolic_state['glucose'] = max(0.0, self.metabolic_state['glucose'] - glucose_consumption)
        
        # 如果血糖低，消耗糖原
        if self.metabolic_state['glucose'] < 0.3:
            glycogen_consumption = glucose_consumption * 0.5
            self.metabolic_state['glycogen'] = max(0.0, self.metabolic_state['glycogen'] - glycogen_consumption)
        
        # 如果糖原也低，开始产生酮体
        if self.metabolic_state['glycogen'] < 0.2:
            self.metabolic_state['ketones'] = min(1.0, self.metabolic_state['ketones'] + 0.01 * dt)
    
    def update_sleep(self, dt: float, is_sleeping: bool):
        """更新睡眠状态"""
        if is_sleeping:
            # 增加睡眠时长
            self.sleep_duration += dt
            
            # 根据睡眠时长调整睡眠阶段
            if self.sleep_duration < 0.5:
                self.sleep_stage = SleepStage.LIGHT
            elif self.sleep_duration < 2.0:
                self.sleep_stage = SleepStage.DEEP
            else:
                self.sleep_stage = SleepStage.REM
            
            # 改善睡眠质量
            self.sleep_quality = min(1.0, self.sleep_quality + 0.1 * dt)
            
            # 减少睡眠债务
            self.sleep_debt = max(0.0, self.sleep_debt - dt)
            
            # 恢复疲劳
            recovery_rate = 0.2 * self.sleep_quality
            self.muscle_fatigue = max(0.0, self.muscle_fatigue - recovery_rate * dt)
            self.mental_fatigue = max(0.0, self.mental_fatigue - recovery_rate * dt)
            self.eye_fatigue = max(0.0, self.eye_fatigue - recovery_rate * dt)
        else:
            # 重置睡眠状态
            self.sleep_stage = SleepStage.AWAKE
            self.sleep_duration = 0.0
            
            # 增加睡眠债务
            self.sleep_debt += dt
            
            # 增加疲劳
            fatigue_rate = 0.05 * (1.0 + self.sleep_debt / 8.0)
            self.muscle_fatigue = min(1.0, self.muscle_fatigue + fatigue_rate * dt)
            self.mental_fatigue = min(1.0, self.mental_fatigue + fatigue_rate * dt)
            self.eye_fatigue = min(1.0, self.eye_fatigue + fatigue_rate * dt)
    
    def consume_food(self, protein: float, carbohydrate: float, fat: float, 
                     vitamin: float, mineral: float):
        """消耗食物，补充营养"""
        self.protein = min(1.0, self.protein + protein)
        self.carbohydrate = min(1.0, self.carbohydrate + carbohydrate)
        self.fat = min(1.0, self.fat + fat)
        self.vitamin = min(1.0, self.vitamin + vitamin)
        self.mineral = min(1.0, self.mineral + mineral)
        
        # 增加饱腹感
        total_nutrition = protein + carbohydrate + fat + vitamin + mineral
        self.satiety = min(1.0, self.satiety + total_nutrition)
        
        # 减少饥饿感
        self.hunger_sensation = max(0.0, self.hunger_sensation - total_nutrition)
        
        # 更新血糖
        self.metabolic_state['glucose'] = min(1.0, self.metabolic_state['glucose'] + carbohydrate)
    
    def drink_water(self, amount: float):
        """喝水，缓解口渴"""
        self.thirst = max(0.0, self.thirst - amount)
        self.thirst_sensation = max(0.0, self.thirst_sensation - amount)
        
        # 更新膀胱
        self.bladder = min(1.0, self.bladder + amount * 0.5)
    
    def excrete(self):
        """排泄"""
        self.bladder = 0.0
        self.bowel = 0.0
        self.sweat = 0.0

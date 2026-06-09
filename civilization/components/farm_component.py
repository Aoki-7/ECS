#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农场组件

v3.0.1 新增 — 农业系统自然演化版

核心设计原则：
- 无硬编码作物生长规则，生长从土壤/水/光条件自然计算
- 农业知识从实践中积累（何时播种、灌溉、收割）
- 不同文明可能发展出完全不同的农业技术
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random

from core.component import Component


@dataclass(slots=True)
class FarmPlotComponent(Component):
    """
    农田地块组件

    记录单个农田地块的状态。
    """
    # 土壤质量（从实际土壤属性计算）
    soil_quality: float = 0.5  # 0-1

    # 当前作物（None = 休耕）
    crop_type: Optional[str] = None

    # 作物生长阶段
    growth_stage: float = 0.0  # 0-1，0=刚播种，1=成熟

    # 作物健康度
    health: float = 1.0  # 0-1

    # 水分水平
    water_level: float = 0.5  # 0-1

    # 是否已灌溉（本周期）
    irrigated_this_cycle: bool = False

    # 播种时间（tick）
    plant_tick: int = 0

    # 预计成熟 tick
    expected_mature_tick: int = 0

    # 历史产量记录
    yield_history: List[float] = field(default_factory=list)

    def can_harvest(self) -> bool:
        """是否可以收割"""
        return self.crop_type is not None and self.growth_stage >= 0.9

    def calculate_yield(self) -> float:
        """
        计算产量

        从土壤质量、健康度、水分水平自然计算。
        """
        if self.crop_type is None:
            return 0.0
        base_yield = self.soil_quality * self.health
        water_bonus = 1.0 - abs(self.water_level - 0.6)  # 最佳水分 0.6
        return max(0.0, base_yield * water_bonus * random.uniform(0.8, 1.2))

    def update_growth(self, dt: float, conditions: Dict) -> None:
        """
        更新生长

        Args:
            dt: 时间步长
            conditions: 环境条件 {temperature, light, moisture}
        """
        if self.crop_type is None:
            return

        # 生长速度从环境条件计算
        temp = conditions.get("temperature", 20.0)
        light = conditions.get("light", 0.5)
        moisture = conditions.get("moisture", 0.5)

        # 温度适宜度（不同作物有不同最适温度，这里简化）
        temp_factor = max(0.0, 1.0 - abs(temp - 22.0) / 15.0)

        # 光照因子
        light_factor = light

        # 水分因子
        water_factor = 1.0 - abs(self.water_level - 0.6) * 2.0

        # 综合生长
        growth_rate = temp_factor * light_factor * water_factor * 0.01 * dt
        self.growth_stage = min(1.0, self.growth_stage + growth_rate)

        # 健康度更新
        if self.water_level < 0.2 or self.water_level > 0.9:
            self.health = max(0.0, self.health - 0.01 * dt)
        else:
            self.health = min(1.0, self.health + 0.005 * dt)

        # 水分自然蒸发/吸收
        self.water_level = max(0.0, self.water_level - 0.02 * dt)
        self.irrigated_this_cycle = False


@dataclass(slots=True)
class FarmingKnowledgeComponent(Component):
    """
    农业知识组件

    从实践中积累的农业经验。
    无硬编码的"最佳实践"，所有知识从实验中学习。
    """

    # 作物种植经验
    # crop_type -> {尝试次数, 成功次数, 平均产量, 最佳播种季节, 最佳土壤类型}
    crop_experience: Dict[str, Dict] = field(default_factory=dict)

    # 灌溉知识
    # 记录不同水分水平下的产量结果
    irrigation_experiments: List[Dict] = field(default_factory=list)

    # 轮作知识
    # 记录作物序列的产量效果
    rotation_experiments: List[Dict] = field(default_factory=list)

    # 已知作物类型（从实践中发现）
    known_crops: List[str] = field(default_factory=list)

    def record_planting(
        self, crop_type: str, soil_type: str, season: str,
        yield_amount: float, success: bool,
    ) -> None:
        """记录一次种植经验"""
        if crop_type not in self.crop_experience:
            self.crop_experience[crop_type] = {
                "attempts": 0, "successes": 0,
                "total_yield": 0.0, "yield_count": 0,
                "soil_preferences": {}, "season_preferences": {},
            }

        exp = self.crop_experience[crop_type]
        exp["attempts"] += 1
        if success:
            exp["successes"] += 1
            exp["total_yield"] += yield_amount
            exp["yield_count"] += 1

        # 记录土壤偏好
        if soil_type not in exp["soil_preferences"]:
            exp["soil_preferences"][soil_type] = []
        exp["soil_preferences"][soil_type].append(yield_amount)

        # 记录季节偏好
        if season not in exp["season_preferences"]:
            exp["season_preferences"][season] = []
        exp["season_preferences"][season].append(yield_amount)

    def get_best_crop_for_conditions(
        self, soil_type: str, season: str
    ) -> Optional[str]:
        """根据条件推荐最佳作物"""
        best_crop = None
        best_score = -1.0

        for crop, exp in self.crop_experience.items():
            if exp["yield_count"] == 0:
                continue

            avg_yield = exp["total_yield"] / exp["yield_count"]
            success_rate = exp["successes"] / max(1, exp["attempts"])

            # 土壤匹配度
            soil_scores = exp["soil_preferences"].get(soil_type, [])
            soil_bonus = sum(soil_scores) / len(soil_scores) if soil_scores else 0.0

            # 季节匹配度
            season_scores = exp["season_preferences"].get(season, [])
            season_bonus = sum(season_scores) / len(season_scores) if season_scores else 0.0

            score = avg_yield * success_rate + soil_bonus * 0.3 + season_bonus * 0.3

            if score > best_score:
                best_score = score
                best_crop = crop

        return best_crop

    def suggest_irrigation_level(self) -> float:
        """建议灌溉水平（从实验中学习）"""
        if not self.irrigation_experiments:
            return 0.6  # 默认探索值

        # 找出历史最高产对应的水分水平
        best_level = 0.6
        best_yield = 0.0

        for exp in self.irrigation_experiments:
            if exp["yield"] > best_yield:
                best_yield = exp["yield"]
                best_level = exp["water_level"]

        return best_level

    def discover_new_crop(self, crop_type: str) -> None:
        """发现新作物"""
        if crop_type not in self.known_crops:
            self.known_crops.append(crop_type)


@dataclass(slots=True)
class IrrigationComponent(Component):
    """
    灌溉系统组件

    记录灌溉设施的状态。
    """
    water_source: Optional[int] = None  # 水源实体 ID
    flow_rate: float = 0.1  # 灌溉速率
    efficiency: float = 0.7  # 效率
    last_irrigation_tick: int = 0

    def irrigate(self, plot: FarmPlotComponent, amount: float) -> float:
        """
        灌溉农田

        Returns:
            实际灌溉水量
        """
        actual = amount * self.efficiency
        plot.water_level = min(1.0, plot.water_level + actual)
        plot.irrigated_this_cycle = True
        return actual

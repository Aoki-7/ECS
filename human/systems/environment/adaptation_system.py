#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:adaptation_system.py
@说明:环境适应系统 - 处理季节和气候的影响
@时间:2026/04/27
@作者:Coder Agent
@版本:1.0
'''

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from core.system import System
from core.world import World


# 季节和气候配置
SEASONS = {
    "spring": {"start": "March 20", "temp_range": (15, 25), "precipitation": "moderate"},
    "summer": {"start": "June 21", "temp_range": (25, 35), "precipitation": "variable"},
    "autumn": {"start": "Sept 22", "temp_range": (15, 28), "precipitation": "moderate"},
    "winter": {"start": "Dec 21", "temp_range": (-10, 10), "precipitation": "snow/ice possible"}
}

WEATHER_TYPES = ["sunny", "cloudy", "rainy", "snowy", "storm"]


@dataclass
class Weather:
    """天气状态"""
    type: str = "clear"
    temperature: float = 20.0
    humidity: float = 50.0
    precipitation_rate: float = 0.0
    wind_speed: float = 5.0  # m/s


class EnvironmentAdaptationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    环境适应系统 - 处理季节和气候对人类的影响
    
    功能：
    - 季节性需求变化（冬季保暖、夏季降温）
    - 恶劣天气防护
    - 气候对行为的影响
    - 日照时长影响（光照疗法等）
    """
    
    def __init__(self):
        super().__init__()
        self.current_season: str = "spring"
        self.weather: Weather = Weather()
        self.adaptation_log: List[Dict] = []

    def set_weather(self, weather_type: str, temp: float = None) -> None:
        """设置天气"""
        self.weather.type = weather_type
        if temp is not None:
            self.weather.temperature = temp
        self._update_season_from_weather()

    def _update_season_from_weather(self):
        """根据当前温度估算季节"""
        temp = self.weather.temperature
        if temp < 0:
            self.current_season = "winter"
        elif temp < 15:
            self.current_season = "spring" or "autumn"
        elif temp > 28:
            self.current_season = "summer"

    def get_season_effects(self, entity_id: int) -> Dict:
        """获取季节对指定实体的影响"""
        effects = {
            "current_season": self.current_season,
            "temperature_effect": "",
            "precipitation_effect": "",
            "behavioral_suggestions": []
        }
        
        # 获取实体的位置信息
        location = self._get_location(entity_id)
        
        if self.current_season == "winter":
            effects["temperature_effect"] = "cold_stress"
            effects["behavioral_suggestions"].append("build_shelter")
            effects["behavioral_suggestions"].append("store_food")
            effects["wear_layers"] = 3  # layer count
        
        elif self.current_season == "summer":
            effects["temperature_effect"] = "heat_stress"
            effects["behavioral_suggestions"].append("find_shade")
            effects["behavioral_suggestions"].append("hydrate")
            effects["wear_layers"] = 1
        
        elif self.current_season in ["spring", "autumn"]:
            effects["temperature_effect"] = "mild"
            effects["wear_layers"] = 2
        
        if self.weather.type == "rainy":
            effects["precipitation_effect"] = "wet_conditions"
            effects["carry_items"].append("umbrella")
        
        return effects

    def _get_location(self, entity_id: int) -> Optional[Dict]:
        """获取实体当前位置"""
        # NOTE: 位置查询待接入空间系统（SpaceSystem）
        return None

    def calculate_overwintering_readiness(self, entity_id: int) -> float:
        """
        计算冬季生存准备度
        
        Returns:
            0-100 的准备度评分
        """
        score = 50.0  # 基础分
        
        location = self._get_location(entity_id)
        
        # 检查住所
        if location and "house" in location.get("type", ""):
            score += 20
        
        # 检查储物
        inventory = self._get_inventory(entity_id, None)
        if inventory:
            food_items = [item for item in inventory.items() 
                         if any(f_keyword in item.name.lower() for f_keyword in ["food", "storage", "dry"])]
            if len(food_items) >= 3:
                score += 15
        
        # 检查储备物资（如毛皮、衣物）
        warm_items = [item for item in inventory.items() 
                     if any(warm in item.name.lower() for warm in ["fur", "wool", "robe", "layer"])]
        if len(warm_items) >= 2:
            score += 10
        
        # 检查健康状况
        health = self._get_health(entity_id, None)
        if health and health.vitality < 60:
            score -= 15
        
        return min(100, max(0, round(score, 1)))

    def get_weather_warnings(self) -> List[str]:
        """获取天气预警信息"""
        warnings = []
        
        temp = self.weather.temperature
        weather_type = self.weather.type
        
        if "storm" in weather_type:
            warnings.append(f"⚠️ 风暴警报！风速 {self.weather.wind_speed} m/s")
        
        if weather_type == "snowy" and temp < -5:
            warnings.append("❄️ 严寒警报，注意保暖")
        
        if self.weather.precipitation_rate > 80:
            warnings.append("🌧️ 强降雨，小心路滑")
        
        return warnings

    def update(self, world: World, dt) -> None:
        """系统更新"""
        # NOTE: 主动更新逻辑暂不需要，该系统目前仅响应查询
        pass


# 环境事件触发器
@dataclass
class EnvironmentalTrigger:
    """环境事件类型定义"""
    types = {
        "season_change": "季节变更",
        "weather_event": "极端天气事件",
        "extreme_heat": "热浪",
        "extreme_cold": "寒潮",
        "flooding": "洪水",
        "drought": "干旱"
    }

    def __init__(self):
        self.current_events: List[Dict] = []
        self.effect_duration: Dict[str, int] = {}  # 事件持续回合数


def get_overwintering_strategy_advice() -> str:
    """获取过冬策略建议"""
    strategies = [
        "🏠 建造或加固住所，确保防风保暖",
        "❄️ 储存足够的食物和饮水",
        "🔥 准备生火工具和燃料",
        "🧥 收集或制作保暖衣物",
        "💊 储备常用药品"
    ]
    
    return "\n".join(strategies)


if __name__ == "__main__":
    import logging
    logging.getLogger(__name__).debug("环境适应系统已加载")
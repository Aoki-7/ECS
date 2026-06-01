#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:adaptation_system.py
@说明:环境适应系统 - 对接真实天气数据
@时间:2026/04/27
@版本:2.0

变更：
- 移除自建 Weather dataclass，改从世界 EnvironmentComponent 读取真实天气
- 修复季节短路 BUG（"spring" or "autumn" 永远等于 "spring"）
- adaptation_log 增加上限裁剪
"""

from typing import Dict, List

from core.system import System
from core.world import World


class EnvironmentAdaptationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    环境适应系统 - 处理季节和气候对人类的影响

    从世界 EnvironmentComponent 读取真实天气数据，不再维护独立天气模型。
    """

    # 日志上限
    MAX_LOG_ENTRIES = 500

    def __init__(self):
        super().__init__()
        self.current_season: str = "spring"
        self.adaptation_log: List[Dict] = []

    def _determine_season(self, temperature: float, month: int) -> str:
        """
        根据温度和月份判定季节。

        修复原短路 BUG："spring" or "autumn" 永远等于 "spring"。
        """
        if temperature < 0:
            return "winter"
        if temperature > 28:
            return "summer"
        # 温度在 0~28°C 之间，根据月份区分春秋
        if 3 <= month <= 5:
            return "spring"
        if 9 <= month <= 11:
            return "autumn"
        # 默认：冬夏交界月份归为较温和的季节
        return "spring" if month < 3 else "autumn"

    def _get_environment(self, world: World) -> Dict:
        """从世界获取真实环境数据"""
        env = world.get_environment()
        time_comp = world.get_time()

        month = 3  # 默认春季
        if time_comp and hasattr(time_comp, 'month'):
            month = time_comp.month

        if env is None:
            return {
                "temperature": 20.0,
                "humidity": 50.0,
                "rainfall": 0.0,
                "wind_speed": 0.0,
                "month": month,
            }

        return {
            "temperature": getattr(env, 'air_temperature', 20.0),
            "humidity": getattr(env, 'air_humidity', 50.0),
            "rainfall": getattr(env, 'rainfall', 0.0),
            "wind_speed": getattr(env, 'wind_speed', 0.0),
            "month": month,
        }

    def get_season_effects(self, entity_id: int, env_data: Dict) -> Dict:
        """获取季节对指定实体的影响"""
        effects = {
            "current_season": self.current_season,
            "temperature_effect": "",
            "behavioral_suggestions": [],
        }

        if self.current_season == "winter":
            effects["temperature_effect"] = "cold_stress"
            effects["behavioral_suggestions"].extend(["build_shelter", "store_food"])

        elif self.current_season == "summer":
            effects["temperature_effect"] = "heat_stress"
            effects["behavioral_suggestions"].extend(["find_shade", "hydrate"])

        elif self.current_season in ("spring", "autumn"):
            effects["temperature_effect"] = "mild"

        if env_data.get("rainfall", 0) > 10.0:
            effects["precipitation_effect"] = "wet_conditions"

        return effects

    def _prune_log(self):
        """裁剪日志防止无限增长"""
        if len(self.adaptation_log) > self.MAX_LOG_ENTRIES:
            self.adaptation_log = self.adaptation_log[-self.MAX_LOG_ENTRIES:]

    def update(self, world: World, dt) -> None:
        """系统更新：从世界读取真实环境并更新季节判定"""
        env_data = self._get_environment(world)
        self.current_season = self._determine_season(
            env_data["temperature"], env_data["month"]
        )

        # 如有需要可在此记录适应日志
        self._prune_log()

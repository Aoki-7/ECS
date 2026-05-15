

from core.component import Component


from dataclasses import dataclass
from environment.season.season_state import Season



@dataclass
class SeasonComponent(Component):
    """
    季节组件（世界级）

    提供气候长期趋势
    """

    # =========================
    # 当前季节
    # =========================

    season: Season = Season.SPRING

    # 当前季节剩余小时
    season_remaining_hours: float = 90 * 24

    # 一年长度（小时）
    year_length_hours: float = 360 * 24

    # 当前年份时间
    year_progress: float = 0.0

    # =========================
    # 气候偏移
    # =========================

    temperature_offset: float = 0.0
    rainfall_factor: float = 1.0
    sunlight_factor: float = 1.0

    # =========================
    # 工具函数
    # =========================

    def is_spring(self):
        return self.season == Season.SPRING
    
    def is_summer(self):
        return self.season == Season.SUMMER

    def is_autumn(self):
        return self.season == Season.AUTUMN
    
    def is_winter(self):
        return self.season == Season.WINTER

    def to_dict(self):
        return {
            "当前季节": self.season.name,
            "季节剩余时间（小时）": self.season_remaining_hours,
        }




from dataclasses import dataclass

from core.component import Component


"""
控制长期气候波动：

例如：

厄尔尼诺
小冰期
湿润周期
干旱周期

它只影响 气候基线。

ElNino
LaNina
Neutral
"""

@dataclass
class ClimateComponent(Component):
    """
    长期气候基线（10-100年）

    决定地区整体气候类型
    """
    mean_temp: float = 15.0
    humidity_bias: float = 0.0
    rainfall_bias: float = 0.0

    climate_phase: str  = "Neutral"
    phase_remaining_days: float = 0.0
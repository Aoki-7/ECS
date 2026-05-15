



from dataclasses import dataclass

from core.component import Component


@dataclass
class ClimateComponent(Component):
    """
    气候组件是对天气的约束

    长期气候基线（10-100年）

    决定地区整体气候类型
    """
    climate_type: str = "temperate"

    mean_annual_temp: float = 15.0
    annual_temp_range: float = 20.0

    mean_annual_precip: float = 800.0
    precipitation_seasonality: float = 0.5

    mean_humidity: float = 0.6

    prevailing_wind_dir: float = 180.0
    prevailing_wind_strength: float = 5.0
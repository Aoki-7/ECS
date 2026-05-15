#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
天气状态分类阈值

定义从连续物理量到离散天气状态标签的全部映射阈值。
纯数据层，无逻辑。
"""

from enum import Enum


# ============================================================
# 离散天气状态枚举（纯标签，不存储演化状态）
# ============================================================

class CloudCoverLevel(Enum):
    """云量等级（从总云量导出）"""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"


class PrecipitationType(Enum):
    """降水类型（从温度导出）"""
    NONE = "none"
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"


class PrecipitationIntensity(Enum):
    """降水强度等级（从降水速率导出）"""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    EXTREME = "extreme"


class WindLevel(Enum):
    """风力等级（从风速导出）"""
    CALM = "calm"
    BREEZE = "breeze"
    STRONG = "strong"
    GALE = "gale"
    STORM = "storm"


class VisibilityState(Enum):
    """能见度状态（从相对湿度和降水导出）"""
    CLEAR = "clear"
    HAZE = "haze"
    FOG = "fog"
    DENSE_FOG = "dense_fog"


# ============================================================
# 云量 → CloudCoverLevel 阈值
# ============================================================

CLOUD_COVER_THRESHOLDS = [
    (0.05, CloudCoverLevel.CLEAR),          # < 5%   → 晴
    (0.25, CloudCoverLevel.PARTLY_CLOUDY),  # 5-25%  → 少云
    (0.50, CloudCoverLevel.CLOUDY),         # 25-50% → 多云
    (1.01, CloudCoverLevel.OVERCAST),       # > 50%  → 阴
]

# ============================================================
# 降水类型 ← 温度阈值 (°C)
# ============================================================

# 降水类型判断（当降水速率 > 0 时有效）
SNOW_TEMP_THRESHOLD: float = -2.0      # T < -2 → 雪
SLEET_TEMP_UPPER: float = 2.0          # -2 ≤ T < 2 → 雨夹雪
# T ≥ 2 → 雨

# ============================================================
# 降水速率 (mm/h) → PrecipitationIntensity 阈值
# ============================================================

PRECIP_INTENSITY_THRESHOLDS = [
    (0.01, PrecipitationIntensity.LIGHT),      # 0~0.01… 微量（但归类为LIGHT）
    (0.1, PrecipitationIntensity.LIGHT),        # 0.01~0.1 间歇？直接用下面的
    (2.5, PrecipitationIntensity.MODERATE),     # 0.1~2.5 → 小雨（LIGHT）
    (7.6, PrecipitationIntensity.HEAVY),        # 2.5~7.6 → 中雨（MODERATE）
    (50.0, PrecipitationIntensity.EXTREME),     # 7.6~50 → 大雨（HEAVY）
    (1e9, PrecipitationIntensity.EXTREME),      # > 50 → 极端
]

# 修正：更清晰的阈值定义映射
PRECIP_RATE_TO_INTENSITY = [
    (0.1, PrecipitationIntensity.LIGHT),        # 0 < rate ≤ 0.1 mm/h → LIGHT
    (2.5, PrecipitationIntensity.MODERATE),     # 0.1 < rate ≤ 2.5 → MODERATE
    (7.6, PrecipitationIntensity.HEAVY),        # 2.5 < rate ≤ 7.6 → HEAVY
    (50.0, PrecipitationIntensity.EXTREME),     # 7.6 < rate ≤ 50 → EXTREME
    (float('inf'), PrecipitationIntensity.EXTREME),  # > 50 → EXTREME
]

# ============================================================
# 风速 (m/s) → WindLevel 阈值
# ============================================================

WIND_SPEED_TO_LEVEL = [
    (0.3, WindLevel.CALM),               # 0~0.2 → 无风；0.3 → 轻风（这里简化为BREEZE起点）
    (1.5, WindLevel.BREEZE),             # 0.3~1.5 → 轻风
    (5.4, WindLevel.STRONG),             # 1.5~5.4 → 和风-强风
    (10.7, WindLevel.GALE),              # 5.4~10.7 → 强风-疾风
    (17.1, WindLevel.STORM),             # 10.7~17.1 → 大风-暴风
    (float('inf'), WindLevel.STORM),     # > 17.1 → 暴风
]

# ============================================================
# 能见度 ← 相对湿度 + 降水 阈值
# ============================================================

# 雾形成的相对湿度阈值
FOG_RH_THRESHOLD: float = 0.93
DENSE_FOG_RH_THRESHOLD: float = 0.97
HAZE_RH_LOWER: float = 0.75
HAZE_RH_UPPER: float = 0.93

# 有降水时，能见度自动降级规则
PRECIP_VISIBILITY_MAP = {
    PrecipitationIntensity.LIGHT: VisibilityState.HAZE,
    PrecipitationIntensity.MODERATE: VisibilityState.FOG,
    PrecipitationIntensity.HEAVY: VisibilityState.FOG,
    PrecipitationIntensity.EXTREME: VisibilityState.DENSE_FOG,
}

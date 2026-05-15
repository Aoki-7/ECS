#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from .weather_types import *


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .weather_types import *


# =========================================================
# ⏳ Duration（半马尔可夫核心）
# =========================================================

SKY_DURATION = {
    SkyState.CLEAR: (6, 24),
    SkyState.PARTLY_CLOUDY: (4, 16),
    SkyState.CLOUDY: (4, 12),
    SkyState.OVERCAST: (3, 10),
}

PRECIPITATION_DURATION = {
    PrecipitationType.NONE: (4, 24),
    PrecipitationType.RAIN: (1, 6),
    PrecipitationType.SNOW: (2, 8),
    PrecipitationType.SLEET: (1, 4),
    PrecipitationType.HAIL: (0.5, 2),
}

FOG_DURATION = {
    VisibilityState.CLEAR: (6, 24),
    VisibilityState.FOG: (1, 6),
    VisibilityState.DENSE_FOG: (0.5, 3),
    VisibilityState.HAZE: (4, 24),
}

WIND_DURATION = {
    WindLevel.CALM: (4, 12),
    WindLevel.BREEZE: (3, 10),
    WindLevel.STRONG: (1, 6),
    WindLevel.GALE: (0.5, 3),
    WindLevel.STORM: (0.5, 2),
}

EXTREME_DURATION = {
    ExtremeWeather.NONE: (6, 48),
    ExtremeWeather.THUNDERSTORM: (0.5, 3),
    ExtremeWeather.BLIZZARD: (2, 8),
    ExtremeWeather.SANDSTORM: (2, 10),
    ExtremeWeather.TORNADO: (0.1, 0.5),
    ExtremeWeather.HURRICANE: (6, 24),
}


# =========================================================
# 🌥 云量
# =========================================================

SKY_TRANSITIONS = {
    SkyState.CLEAR: {
        SkyState.CLEAR: 0.6,
        SkyState.PARTLY_CLOUDY: 0.3,
        SkyState.CLOUDY: 0.1,
    },
    SkyState.PARTLY_CLOUDY: {
        SkyState.CLEAR: 0.2,
        SkyState.PARTLY_CLOUDY: 0.5,
        SkyState.CLOUDY: 0.3,
    },
    SkyState.CLOUDY: {
        SkyState.PARTLY_CLOUDY: 0.3,
        SkyState.CLOUDY: 0.5,
        SkyState.OVERCAST: 0.2,
    },
    SkyState.OVERCAST: {
        SkyState.CLOUDY: 0.4,
        SkyState.OVERCAST: 0.6,
    }
}


# =========================================================
# 🌧 降水类型
# =========================================================

PRECIPITATION_TYPE_TRANSITIONS = {
    PrecipitationType.NONE: {
        PrecipitationType.NONE: 0.7,
        PrecipitationType.RAIN: 0.25,
        PrecipitationType.SNOW: 0.05,
    },
    PrecipitationType.RAIN: {
        PrecipitationType.NONE: 0.3,
        PrecipitationType.RAIN: 0.6,
        PrecipitationType.SLEET: 0.1,
    },
    PrecipitationType.SNOW: {
        PrecipitationType.NONE: 0.3,
        PrecipitationType.SNOW: 0.6,
        PrecipitationType.SLEET: 0.1,
    },
    PrecipitationType.SLEET: {
        PrecipitationType.RAIN: 0.4,
        PrecipitationType.SNOW: 0.3,
        PrecipitationType.SLEET: 0.3,
    },
    PrecipitationType.HAIL: {
        PrecipitationType.RAIN: 0.7,
        PrecipitationType.NONE: 0.3,
    }
}


# =========================================================
# 🌧 强度（只在有降水时有效）
# =========================================================

PRECIPITATION_INTENSITY_TRANSITIONS = {
    PrecipitationIntensity.NONE: {
        PrecipitationIntensity.NONE: 1.0
    },
    PrecipitationIntensity.LIGHT: {
        PrecipitationIntensity.LIGHT: 0.6,
        PrecipitationIntensity.MODERATE: 0.3,
        PrecipitationIntensity.NONE: 0.1,
    },
    PrecipitationIntensity.MODERATE: {
        PrecipitationIntensity.LIGHT: 0.3,
        PrecipitationIntensity.MODERATE: 0.5,
        PrecipitationIntensity.HEAVY: 0.2,
    },
    PrecipitationIntensity.HEAVY: {
        PrecipitationIntensity.MODERATE: 0.4,
        PrecipitationIntensity.HEAVY: 0.5,
        PrecipitationIntensity.EXTREME: 0.1,
    },
    PrecipitationIntensity.EXTREME: {
        PrecipitationIntensity.HEAVY: 0.7,
        PrecipitationIntensity.EXTREME: 0.3,
    },
}


# =========================================================
# 🌫 能见度
# =========================================================

VISIBILITY_TRANSITIONS = {
    VisibilityState.CLEAR: {
        VisibilityState.CLEAR: 0.7,
        VisibilityState.FOG: 0.2,
        VisibilityState.HAZE: 0.1,
    },
    VisibilityState.FOG: {
        VisibilityState.CLEAR: 0.3,
        VisibilityState.FOG: 0.5,
        VisibilityState.DENSE_FOG: 0.2,
    },
    VisibilityState.DENSE_FOG: {
        VisibilityState.FOG: 0.6,
        VisibilityState.DENSE_FOG: 0.4,
    },
    VisibilityState.HAZE: {
        VisibilityState.CLEAR: 0.4,
        VisibilityState.HAZE: 0.6,
    },
}


# =========================================================
# 💨 风
# =========================================================

WIND_TRANSITIONS = {
    WindLevel.CALM: {
        WindLevel.CALM: 0.6,
        WindLevel.BREEZE: 0.4,
    },
    WindLevel.BREEZE: {
        WindLevel.CALM: 0.3,
        WindLevel.BREEZE: 0.5,
        WindLevel.STRONG: 0.2,
    },
    WindLevel.STRONG: {
        WindLevel.BREEZE: 0.4,
        WindLevel.STRONG: 0.4,
        WindLevel.GALE: 0.2,
    },
    WindLevel.GALE: {
        WindLevel.STRONG: 0.5,
        WindLevel.GALE: 0.3,
        WindLevel.STORM: 0.2,
    },
    WindLevel.STORM: {
        WindLevel.GALE: 0.6,
        WindLevel.STORM: 0.4,
    },
}


# =========================================================
# ⛈ 极端天气（低概率事件）
# =========================================================

EXTREME_TRANSITIONS = {
    ExtremeWeather.NONE: {
        ExtremeWeather.NONE: 0.97,
        ExtremeWeather.THUNDERSTORM: 0.02,
        ExtremeWeather.BLIZZARD: 0.005,
        ExtremeWeather.SANDSTORM: 0.003,
        ExtremeWeather.TORNADO: 0.001,
        ExtremeWeather.HURRICANE: 0.001,
    },
    ExtremeWeather.THUNDERSTORM: {
        ExtremeWeather.NONE: 0.7,
        ExtremeWeather.THUNDERSTORM: 0.3,
    },
    ExtremeWeather.BLIZZARD: {
        ExtremeWeather.NONE: 0.6,
        ExtremeWeather.BLIZZARD: 0.4,
    },
    ExtremeWeather.SANDSTORM: {
        ExtremeWeather.NONE: 0.7,
        ExtremeWeather.SANDSTORM: 0.3,
    },
    ExtremeWeather.TORNADO: {
        ExtremeWeather.NONE: 0.9,
        ExtremeWeather.TORNADO: 0.1,
    },
    ExtremeWeather.HURRICANE: {
        ExtremeWeather.NONE: 0.8,
        ExtremeWeather.HURRICANE: 0.2,
    },
}


# =========================
# 降水概率（受云量影响）
# =========================
def precipitation_probability(sky: SkyState) -> float:
    if sky == SkyState.CLEAR:
        return 0.05
    if sky == SkyState.PARTLY_CLOUDY:
        return 0.15
    if sky == SkyState.CLOUDY:
        return 0.4
    if sky == SkyState.OVERCAST:
        return 0.7
    return 0.0


# =========================
# 工具函数
# =========================
def weighted_choice(table: dict):
    r = random.random()
    cumulative = 0.0
    for state, prob in table.items():
        cumulative += prob
        if r <= cumulative:
            return state
    return list(table.keys())[-1]


# =========================
# 主更新函数
# =========================
def next_weather_state(state: WeatherState) -> WeatherState:

    # --- 云量 ---
    new_sky = weighted_choice(SKY_TRANSITIONS[state.sky])

    # --- 降水 ---
    rain_prob = precipitation_probability(new_sky)

    if random.random() < rain_prob:
        precip_type = PrecipitationType.RAIN

        intensity = random.choices(
            [
                PrecipitationIntensity.LIGHT,
                PrecipitationIntensity.MODERATE,
                PrecipitationIntensity.HEAVY
            ],
            weights=[0.6, 0.3, 0.1]
        )[0]
    else:
        precip_type = PrecipitationType.NONE
        intensity = PrecipitationIntensity.NONE

    # --- 能见度 ---
    if precip_type != PrecipitationType.NONE and random.random() < 0.3:
        visibility = VisibilityState.FOG
    else:
        visibility = VisibilityState.CLEAR

    # --- 风 ---
    wind = random.choices(
        [
            WindLevel.CALM,
            WindLevel.BREEZE,
            WindLevel.STRONG,
        ],
        weights=[0.5, 0.4, 0.1]
    )[0]

    # --- 极端天气 ---
    if precip_type == PrecipitationType.RAIN and wind == WindLevel.STRONG and random.random() < 0.1:
        extreme = ExtremeWeather.THUNDERSTORM
    else:
        extreme = ExtremeWeather.NONE

    return WeatherState(
        sky=new_sky,
        precipitation_type=precip_type,
        precipitation_intensity=intensity,
        visibility=visibility,
        wind=wind,
        extreme=extreme
    )
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .weather_types import *


def derive_weather_label(state: WeatherState) -> str:
    """
    从多维状态派生“人类可读天气”
    """

    # 极端天气优先
    if state.extreme != ExtremeWeather.NONE:
        return state.extreme.value

    # 降水
    if state.precipitation_type != PrecipitationType.NONE:
        return f"{state.precipitation_intensity.value}_{state.precipitation_type.value}"

    # 能见度
    if state.visibility != VisibilityState.CLEAR:
        return state.visibility.value

    # 云量
    return state.sky.value
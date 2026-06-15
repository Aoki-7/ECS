#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境常量测试

v3.2 优化新增
"""

import pytest

from environment.config.environment_constants import (
    DEFAULT_PAR, DEFAULT_PHOTOPERIOD, DAYTIME_PAR_THRESHOLD,
    DEFAULT_AIR_TEMP, DEFAULT_SOIL_TEMP, DEFAULT_TEMP_DIFF,
    DEFAULT_SOIL_MOISTURE, DEFAULT_FIELD_CAPACITY, DEFAULT_WILTING_POINT,
    DEFAULT_AIR_HUMIDITY, DEFAULT_VPD,
    DEFAULT_CO2, DEFAULT_O2,
    DEFAULT_SOIL_PH, DEFAULT_SOIL_EC,
    DEFAULT_NITROGEN, DEFAULT_PHOSPHORUS, DEFAULT_POTASSIUM,
    DEFAULT_WIND_SPEED, DEFAULT_RAINFALL,
    THERMAL_DIFFUSION_COEFF, HUMIDITY_DIFFUSION_COEFF,
    WATER_FLOW_COEFF, ADVECTION_COEFF, RECOVERY_RATE_BASE,
    MAX_DIFFUSION_COEFF,
    DAYS_PER_SEASON, SEASONS,
    RAIN_EVAPORATION_RATE, CLOUD_FORMATION_THRESHOLD,
    STORM_WIND_THRESHOLD,
)


class TestEnvironmentConstants:
    """测试环境常量"""

    def test_light_constants(self):
        assert DEFAULT_PAR > 0
        assert DEFAULT_PHOTOPERIOD > 0
        assert DAYTIME_PAR_THRESHOLD > 0

    def test_temperature_constants(self):
        assert DEFAULT_AIR_TEMP > -50
        assert DEFAULT_SOIL_TEMP > -50
        assert DEFAULT_TEMP_DIFF >= 0

    def test_moisture_constants(self):
        assert 0 < DEFAULT_SOIL_MOISTURE < 1
        assert 0 < DEFAULT_FIELD_CAPACITY < 1
        assert 0 < DEFAULT_WILTING_POINT < 1
        assert DEFAULT_WILTING_POINT < DEFAULT_FIELD_CAPACITY

    def test_gas_constants(self):
        assert DEFAULT_CO2 > 0
        assert DEFAULT_O2 > 0

    def test_soil_constants(self):
        assert 0 < DEFAULT_SOIL_PH < 14
        assert DEFAULT_NITROGEN > 0
        assert DEFAULT_PHOSPHORUS > 0
        assert DEFAULT_POTASSIUM > 0

    def test_diffusion_coefficients(self):
        assert THERMAL_DIFFUSION_COEFF > 0
        assert HUMIDITY_DIFFUSION_COEFF > 0
        assert WATER_FLOW_COEFF >= 0
        assert ADVECTION_COEFF >= 0
        assert MAX_DIFFUSION_COEFF > 0

    def test_season_constants(self):
        assert DAYS_PER_SEASON > 0
        assert len(SEASONS) == 4
        assert "spring" in SEASONS
        assert "winter" in SEASONS

    def test_weather_thresholds(self):
        assert RAIN_EVAPORATION_RATE >= 0
        assert 0 < CLOUD_FORMATION_THRESHOLD < 1
        assert STORM_WIND_THRESHOLD > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

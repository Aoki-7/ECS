#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
季节变化系统测试

v3.3 新增
"""

import pytest

from environment.season.season_change_system import SeasonChangeSystem
from environment.environment_component import EnvironmentComponent
from core.world import World


class TestSeasonChangeSystem:
    """测试季节变化系统"""

    @pytest.fixture
    def system(self):
        return SeasonChangeSystem()

    def test_calculate_season(self, system):
        """测试季节计算"""
        assert system._calculate_season(80) == "spring"
        assert system._calculate_season(172) == "summer"
        assert system._calculate_season(266) == "autumn"
        assert system._calculate_season(355) == "winter"
        assert system._calculate_season(1) == "winter"

    def test_transition_factor(self, system):
        """测试过渡因子"""
        # 季节开始时逐渐增强
        assert system._calculate_transition_factor("spring", 80) == 0.0
        assert system._calculate_transition_factor("spring", 85) == pytest.approx(0.33, 0.1)

        # 季节中期稳定
        assert system._calculate_transition_factor("spring", 120) == 1.0

        # 季节结束时逐渐减弱
        assert system._calculate_transition_factor("spring", 160) == pytest.approx(0.67, 0.1)

    def test_season_effects(self, system):
        """测试季节效果应用"""
        env = EnvironmentComponent()
        initial_temp = env.air_temperature

        system._apply_season_effects(env, "summer", 200)

        # 夏季温度应该上升
        assert env.air_temperature > initial_temp

    def test_winter_cools(self, system):
        """测试冬季降温"""
        env = EnvironmentComponent()
        initial_temp = env.air_temperature

        system._apply_season_effects(env, "winter", 10)

        # 冬季温度应该下降
        assert env.air_temperature < initial_temp

    def test_get_season_info(self, system):
        """测试季节信息获取"""
        info = system.get_season_info(100)
        assert info["season"] == "spring"
        assert "effects" in info
        assert info["is_northern"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

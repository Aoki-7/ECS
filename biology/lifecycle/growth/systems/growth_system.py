#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/systems/growth_system.py
@说明:生长系统（光合作用 + 呼吸 + 生长能量计算）

根据环境条件与基因表型，计算每个植物实体的：
    - 光合收入（受光、CO₂、温度、水分、VPD 影响）
    - 呼吸消耗（Q10 温度系数）
    - 能量变更与生长池分配

读取的表型性状：
    max_photosynthesis_rate, light_use_efficiency, optimal_temp,
    growth_partition, metabolism_rate,
    shade_tolerance, cold_tolerance, heat_tolerance, water_use_efficiency
"""

from core.world import World
from core.system import System

from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.energy_component import EnergyComponent


class GrowthSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    光合作用与能量收支系统

    职责：
        - 从环境读取光照、CO₂、温度、水分胁迫、VPD
        - 从 phenotype 读取基因表达的光合与耐受参数
        - 计算净光合产物并更新能量池
    """

    def update(self, world: World, delta_hours: float = 1.0) -> None:
        """
        执行生长更新

        Args:
            world: World 实例
            delta_hours: 时间步长（小时）
        """
        env = world.get_environment()
        if env is None:
            return

        for entity, (pheno, energy) in world.get_components(
            PhenotypeComponent, EnergyComponent
        ):
            # 计算光合参数
            params = self._calc_photosynthesis_params(pheno, env)
            # 计算环境因子
            env_factors = self._calc_environment_factors(pheno, env, params)
            # 计算能量收支
            self._update_energy(energy, params, env_factors, delta_hours)

    def _calc_photosynthesis_params(self, pheno, env) -> dict:
        """计算光合基础参数"""
        max_photo = PhenotypeSystem.get(pheno, "max_photosynthesis_rate", 20.0)
        alpha = PhenotypeSystem.get(pheno, "light_use_efficiency", 0.05)
        shade_tol = PhenotypeSystem.get(pheno, "shade_tolerance", 0.3)
        par = PhenotypeSystem.get(pheno, "effective_par", env.par)

        # Michaelis-Menten
        if max_photo <= 0:
            light_response = 0.0
        else:
            light_response = (alpha * par) / (1 + alpha * par / max_photo)

        # 耐阴增益
        if par < 200:
            shade_boost = shade_tol * (1.0 - par / 200.0) * 0.3
            light_response *= (1.0 + shade_boost)

        return {
            "max_photo": max_photo,
            "light_response": light_response,
            "par": par,
        }

    def _calc_environment_factors(self, pheno, env, params) -> dict:
        """计算环境修正因子"""
        optimal_temp = PhenotypeSystem.get(pheno, "optimal_temp", 25.0)
        cold_tol = PhenotypeSystem.get(pheno, "cold_tolerance", 0.4)
        heat_tol = PhenotypeSystem.get(pheno, "heat_tolerance", 0.5)
        wue = PhenotypeSystem.get(pheno, "water_use_efficiency", 0.05)
        temp = env.air_temperature

        # CO₂
        co2_factor = env.co2 / 400.0

        # 温度
        temp_diff = temp - optimal_temp
        if temp_diff < 0:
            cold_width = 15.0 * (1.0 + cold_tol * 0.6)
            temp_factor = max(0.0, 1.0 - (temp_diff / cold_width) ** 2)
        else:
            heat_width = 15.0 * (1.0 + heat_tol * 0.6)
            temp_factor = max(0.0, 1.0 - (temp_diff / heat_width) ** 2)

        # 水分
        water_stress = PhenotypeSystem.get(pheno, "plant_water_stress", env.water_stress_index)
        wue_bonus = wue * 2.0
        effective_stress = max(0.0, water_stress - wue_bonus)
        water_factor = 1.0 - effective_stress

        # VPD
        vpd_factor = max(0.0, 1.0 - abs(env.vpd - 1.0) / 2.0)

        return {
            "co2_factor": co2_factor,
            "temp_factor": temp_factor,
            "water_factor": water_factor,
            "vpd_factor": vpd_factor,
            "temperature": temp,
        }

    def _update_energy(self, energy, params, env_factors, delta_hours: float) -> None:
        """更新能量收支"""
        growth_part = energy.get("growth_partition", 0.6)
        base_metab = energy.get("metabolism_rate", 0.01)

        # 光合总收入
        photosynthesis_rate = (
            params["light_response"]
            * env_factors["co2_factor"]
            * env_factors["temp_factor"]
            * env_factors["water_factor"]
            * env_factors["vpd_factor"]
        )
        photosynthesis_gain = photosynthesis_rate * delta_hours

        # 呼吸消耗
        q10 = 2.0
        temp = env_factors["temperature"]
        temp_resp_factor = q10 ** ((temp - 20) / 10)
        respiration_cost = energy.value * base_metab * temp_resp_factor * delta_hours

        # 生长分配
        surplus = photosynthesis_gain - respiration_cost
        growth_energy = surplus * growth_part if surplus > 0 else 0.0

        # 能量变更
        delta_energy = photosynthesis_gain - respiration_cost
        energy.value += delta_energy
        energy.growth_pool += growth_energy
        energy.value -= growth_energy
        energy.value = max(0.0, min(energy.value, energy.max_energy))

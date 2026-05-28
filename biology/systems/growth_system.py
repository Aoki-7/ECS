# biology/systems/growth_system.py
#
# 光合作用 + 呼吸 + 生长能量计算
#
# 读取的基因（来自 PhenotypeComponent）：
#   已有: max_photosynthesis_rate, light_use_efficiency, optimal_temp,
#         growth_partition, metabolism_rate
#   新增: shade_tolerance, cold_tolerance, heat_tolerance, water_use_efficiency

from core.world import World
from core.system import System
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent


class GrowthSystem(System):

    def update(self, world: World, delta_hours: float = 1.0):

        env = world.get_environment()
        if env is None:
            return

        for entity, (pheno, energy) in world.get_components(PhenotypeComponent, EnergyComponent):

            # ==========================================================
            # 1) 基础参数（来自基因，有默认值兜底）
            # ==========================================================

            max_photo = pheno.get("max_photosynthesis_rate", 20.0)
            alpha = pheno.get("light_use_efficiency", 0.05)
            optimal_temp = pheno.get("optimal_temp", 25.0)
            growth_part = pheno.get("growth_partition", 0.6)
            base_metab = pheno.get("metabolism_rate", 0.01)

            # 新增耐受基因
            shade_tol = pheno.get("shade_tolerance", 0.3)
            cold_tol = pheno.get("cold_tolerance", 0.4)
            heat_tol = pheno.get("heat_tolerance", 0.5)
            wue = pheno.get("water_use_efficiency", 0.05)

            # ==========================================================
            # 2) 光响应（带耐阴修正）
            # ==========================================================

            par = env.par

            # 基础 Michaelis-Menten
            if max_photo <= 0:
                light_response = 0.0
            else:
                light_response = (alpha * par) / (1 + alpha * par / max_photo)

            # 耐阴增益：低光下提高光效
            if par < 200:
                shade_boost = shade_tol * (1.0 - par / 200.0) * 0.3
                light_response = light_response * (1.0 + shade_boost)

            # ==========================================================
            # 3) CO₂ 修正
            # ==========================================================

            co2_factor = env.co2 / 400.0

            # ==========================================================
            # 4) 温度响应（非对称钟形曲线）
            # ==========================================================

            temp = env.air_temperature
            temp_diff = temp - optimal_temp

            if temp_diff < 0:
                # 低温侧：耐寒性拉宽曲线
                cold_width = 15.0 * (1.0 + cold_tol * 0.6)
                temp_factor = max(0.0, 1.0 - (temp_diff / cold_width) ** 2)
            else:
                # 高温侧：耐热性拉宽曲线
                heat_width = 15.0 * (1.0 + heat_tol * 0.6)
                temp_factor = max(0.0, 1.0 - (temp_diff / heat_width) ** 2)

            # ==========================================================
            # 5) 水分胁迫（WUE 修正）
            # ==========================================================

            water_stress = env.water_stress_index
            # 高 WUE 的植物受水分胁迫影响更小
            wue_bonus = wue * 2.0  # WUE=0.15 → 减免 30%
            effective_stress = max(0.0, water_stress - wue_bonus)
            water_factor = 1.0 - effective_stress

            # ==========================================================
            # 6) VPD 胁迫
            # ==========================================================

            vpd_factor = max(0.0, 1.0 - abs(env.vpd - 1.0) / 2.0)

            # ==========================================================
            # 7) 光合总收入
            # ==========================================================

            photosynthesis_rate = (
                light_response
                * co2_factor
                * temp_factor
                * water_factor
                * vpd_factor
            )

            photosynthesis_gain = photosynthesis_rate * delta_hours

            # ==========================================================
            # 8) 呼吸消耗（温度指数 Q10）
            # ==========================================================

            q10 = 2.0
            temp_resp_factor = q10 ** ((temp - 20) / 10)

            respiration_cost = (
                energy.value
                * base_metab
                * temp_resp_factor
                * delta_hours
            )

            # ==========================================================
            # 9) 生长分配
            # ==========================================================

            surplus = photosynthesis_gain - respiration_cost

            growth_energy = 0.0
            if surplus > 0:
                growth_energy = surplus * growth_part

            # ==========================================================
            # 10) 能量变更
            # ==========================================================

            delta_energy = photosynthesis_gain - respiration_cost

            energy.value += delta_energy
            energy.growth_pool += growth_energy
            energy.value -= growth_energy

            # 安全边界
            energy.value = max(0.0, min(energy.value, energy.max_energy))




# biology/systems/growth_system.py

from core.world import World
from core.system import System
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.energy_component import EnergyComponent


class GrowthSystem:

    def update(self, world: World, delta_hours: float = 1.0):

        env = world.get_environment()

        for entity, (pheno, energy) in world.get_components(PhenotypeComponent, EnergyComponent):

            # ====
            # 1️⃣ 基础参数（来自基因）
            # ====
            pheno: PhenotypeComponent
            energy: EnergyComponent

            max_photosynthesis = pheno.get("max_photosynthesis_rate", 20.0)  # μmol CO2/m²/s
            alpha = pheno.get("light_use_efficiency", 0.05)
            optimal_temp = pheno.get("optimal_temp", 25.0)
            growth_partition = pheno.get("growth_partition", 0.6)
            base_metabolism = pheno.get("metabolism_rate", 0.01)

            # ====
            # 2️⃣ 光响应曲线（非线性）
            # ====

            # Michaelis-Menten 近似光饱和
            par = env.par
            light_response = (alpha * par) / (1 + alpha * par / max_photosynthesis)

            # ====
            # 3️⃣ CO₂ 修正
            # ====

            co2_factor = env.co2 / 400.0  # 400ppm为基准

            # ====
            # 4️⃣ 温度响应（钟形曲线）
            # ====

            temp = env.air_temperature
            temp_factor = max(
                0.0,
                1 - ((temp - optimal_temp) / 15) ** 2
            )

            # ====
            # 5️⃣ 水分胁迫
            # ====

            water_stress = env.water_stress_index
            water_factor = 1.0 - water_stress

            # ====
            # 6️⃣ VPD 胁迫
            # ====

            # 理想 VPD ≈ 1.0 kPa
            vpd_factor = max(
                0.0,
                1 - abs(env.vpd - 1.0) / 2.0
            )

            # ====
            # 7️⃣ 光合收入（单位时间）
            # ====

            photosynthesis_rate = (
                light_response
                * co2_factor
                * temp_factor
                * water_factor
                * vpd_factor
            )

            photosynthesis_gain = photosynthesis_rate * delta_hours

            # ====
            # 8️⃣ 呼吸（温度指数）
            # ====

            q10 = 2.0
            temp_resp_factor = q10 ** ((temp - 20) / 10)

            respiration_cost = (
                energy.value
                * base_metabolism
                * temp_resp_factor
                * delta_hours
            )

            # ====
            # 9️⃣ 生长分配
            # ====

            surplus = photosynthesis_gain - respiration_cost

            growth_energy = 0.0
            if surplus > 0:
                growth_energy = surplus * growth_partition

            # ====
            # 🔟 能量变化
            # ====

            delta_energy = (
                photosynthesis_gain
                - respiration_cost
            )

            energy.value += delta_energy

            energy.growth_pool += growth_energy
            energy.value -= growth_energy

            # ====
            # 安全边界
            # ====

            energy.value = max(
                0.0,
                min(energy.value, energy.max_energy)
            )
# plant/presets.py
"""
植物物种基因预设模板

本模块集中维护所有植物物种的纯基因配置。

设计原则：
    1. 模板只保留基因相关参数（生理生化），没有任何硬编码外观
    2. 外观（高度、茎粗、叶数等）由 MorphologySystem 根据基因 + 生长环境 + 时间动态推导
    3. 生命周期阶段时长由 PlantFactory 根据 growth 类基因实时计算，不再硬编码

基因维度（6 大类，23 个基因）：
    ─ photosynthesis : 光合系统（5 个）
    ─ resource       : 资源利用（3 个）
    ─ stress         : 抗逆胁迫（4 个）
    ─ growth         : 生长代谢（4 个）
    ─ reproduction   : 繁殖策略（4 个）
    ─ evolution      : 进化潜力（3 个）
"""

from typing import Dict

#: 物种基因预设表（23 个纯基因，无任何外观硬编码）
#: key   : 物种标识名 (str)
#: value : {基因表达目标 -> 基础强度值 (Dict[str, float])}
SPECIES_PRESETS: Dict[str, Dict[str, float]] = {

    # ────────────────────────────────────────────
    # 🌿 基础草本 — 各项能力均衡，默认对照组
    # ────────────────────────────────────────────
    "basic": {
        # photosynthesis
        "max_photosynthesis_rate": 20.0,
        "light_use_efficiency": 0.05,
        "shade_tolerance": 0.3,
        "light_compensation_point": 20.0,
        "light_saturation_point": 500.0,
        # resource
        "water_use_efficiency": 0.05,
        "nutrient_use_efficiency": 0.5,
        "carbon_storage_efficiency": 0.3,
        # stress
        "cold_tolerance": 0.4,
        "heat_tolerance": 0.5,
        "drought_tolerance": 0.3,
        "flood_tolerance": 0.2,
        # growth
        "metabolism_rate": 0.01,
        "growth_partition": 0.6,
        "maintenance_cost": 0.02,
        "storage_partition": 0.2,
        # reproduction
        "seed_production": 1.0,
        "seed_size": 1.0,
        "dispersal_radius": 3.0,
        "germination_rate": 0.7,
        # evolution
        "mutation_rate": 0.1,
        "adaptability": 0.5,
        "genetic_stability": 0.7,
    },

    # ────────────────────────────────────────────
    # ⚡ 速生杂草 — 高代谢、高繁殖、寿命短
    # ────────────────────────────────────────────
    "fast": {
        "max_photosynthesis_rate": 35.0,
        "light_use_efficiency": 0.09,
        "shade_tolerance": 0.2,
        "light_compensation_point": 30.0,
        "light_saturation_point": 800.0,
        "water_use_efficiency": 0.06,
        "nutrient_use_efficiency": 0.6,
        "carbon_storage_efficiency": 0.2,
        "cold_tolerance": 0.2,
        "heat_tolerance": 0.6,
        "drought_tolerance": 0.2,
        "flood_tolerance": 0.1,
        "metabolism_rate": 0.025,
        "growth_partition": 0.75,
        "maintenance_cost": 0.04,
        "storage_partition": 0.1,
        "seed_production": 2.0,
        "seed_size": 0.5,
        "dispersal_radius": 5.0,
        "germination_rate": 0.9,
        "mutation_rate": 0.15,
        "adaptability": 0.7,
        "genetic_stability": 0.5,
    },

    # ────────────────────────────────────────────
    # 🌲 乔木 — 低代谢、长寿、高储存、低繁殖
    # ────────────────────────────────────────────
    "tree": {
        "max_photosynthesis_rate": 15.0,
        "light_use_efficiency": 0.04,
        "shade_tolerance": 0.5,
        "light_compensation_point": 15.0,
        "light_saturation_point": 600.0,
        "water_use_efficiency": 0.06,
        "nutrient_use_efficiency": 0.7,
        "carbon_storage_efficiency": 0.6,
        "cold_tolerance": 0.6,
        "heat_tolerance": 0.4,
        "drought_tolerance": 0.5,
        "flood_tolerance": 0.3,
        "metabolism_rate": 0.005,
        "growth_partition": 0.45,
        "maintenance_cost": 0.012,
        "storage_partition": 0.4,
        "seed_production": 0.5,
        "seed_size": 2.5,
        "dispersal_radius": 10.0,
        "germination_rate": 0.4,
        "mutation_rate": 0.05,
        "adaptability": 0.3,
        "genetic_stability": 0.9,
    },

    # ────────────────────────────────────────────
    # ❄️ 耐寒型 — 低温适应，低代谢
    # ────────────────────────────────────────────
    "cold_resistant": {
        "max_photosynthesis_rate": 18.0,
        "light_use_efficiency": 0.06,
        "shade_tolerance": 0.4,
        "light_compensation_point": 15.0,
        "light_saturation_point": 450.0,
        "water_use_efficiency": 0.05,
        "nutrient_use_efficiency": 0.5,
        "carbon_storage_efficiency": 0.4,
        "cold_tolerance": 0.9,
        "heat_tolerance": 0.2,
        "drought_tolerance": 0.4,
        "flood_tolerance": 0.2,
        "metabolism_rate": 0.008,
        "growth_partition": 0.5,
        "maintenance_cost": 0.018,
        "storage_partition": 0.25,
        "seed_production": 0.8,
        "seed_size": 1.2,
        "dispersal_radius": 4.0,
        "germination_rate": 0.5,
        "mutation_rate": 0.08,
        "adaptability": 0.6,
        "genetic_stability": 0.8,
    },

    # ────────────────────────────────────────────
    # 🏜️ 耐旱型 — 高水分利用、深根系（通过生长系统体现）
    # ────────────────────────────────────────────
    "drought_resistant": {
        "max_photosynthesis_rate": 10.0,
        "light_use_efficiency": 0.03,
        "shade_tolerance": 0.2,
        "light_compensation_point": 25.0,
        "light_saturation_point": 400.0,
        "water_use_efficiency": 0.12,
        "nutrient_use_efficiency": 0.8,
        "carbon_storage_efficiency": 0.5,
        "cold_tolerance": 0.1,
        "heat_tolerance": 0.8,
        "drought_tolerance": 0.9,
        "flood_tolerance": 0.1,
        "metabolism_rate": 0.006,
        "growth_partition": 0.4,
        "maintenance_cost": 0.012,
        "storage_partition": 0.35,
        "seed_production": 0.5,
        "seed_size": 1.5,
        "dispersal_radius": 6.0,
        "germination_rate": 0.3,
        "mutation_rate": 0.12,
        "adaptability": 0.8,
        "genetic_stability": 0.6,
    },

    # ────────────────────────────────────────────
    # 🌑 耐阴型 — 低光高效、低光补偿点
    # ────────────────────────────────────────────
    "shade_tolerant": {
        "max_photosynthesis_rate": 8.0,
        "light_use_efficiency": 0.12,
        "shade_tolerance": 0.9,
        "light_compensation_point": 5.0,
        "light_saturation_point": 300.0,
        "water_use_efficiency": 0.07,
        "nutrient_use_efficiency": 0.6,
        "carbon_storage_efficiency": 0.3,
        "cold_tolerance": 0.5,
        "heat_tolerance": 0.3,
        "drought_tolerance": 0.4,
        "flood_tolerance": 0.3,
        "metabolism_rate": 0.008,
        "growth_partition": 0.5,
        "maintenance_cost": 0.015,
        "storage_partition": 0.2,
        "seed_production": 0.6,
        "seed_size": 1.0,
        "dispersal_radius": 2.0,
        "germination_rate": 0.6,
        "mutation_rate": 0.1,
        "adaptability": 0.5,
        "genetic_stability": 0.7,
    },

    # ────────────────────────────────────────────
    # 💧 水生型 — 高耐涝、低水分利用效率（水分充足）
    # ────────────────────────────────────────────
    "aquatic": {
        "max_photosynthesis_rate": 25.0,
        "light_use_efficiency": 0.07,
        "shade_tolerance": 0.4,
        "light_compensation_point": 20.0,
        "light_saturation_point": 550.0,
        "water_use_efficiency": 0.02,
        "nutrient_use_efficiency": 0.5,
        "carbon_storage_efficiency": 0.3,
        "cold_tolerance": 0.3,
        "heat_tolerance": 0.6,
        "drought_tolerance": 0.1,
        "flood_tolerance": 0.9,
        "metabolism_rate": 0.015,
        "growth_partition": 0.55,
        "maintenance_cost": 0.02,
        "storage_partition": 0.2,
        "seed_production": 1.5,
        "seed_size": 0.8,
        "dispersal_radius": 8.0,
        "germination_rate": 0.8,
        "mutation_rate": 0.1,
        "adaptability": 0.4,
        "genetic_stability": 0.7,
    },

    # ────────────────────────────────────────────
    # 🌵 多肉型 — 极端耐旱、高碳储存、极低代谢
    # ────────────────────────────────────────────
    "succulent": {
        "max_photosynthesis_rate": 6.0,
        "light_use_efficiency": 0.02,
        "shade_tolerance": 0.2,
        "light_compensation_point": 30.0,
        "light_saturation_point": 700.0,
        "water_use_efficiency": 0.18,
        "nutrient_use_efficiency": 0.4,
        "carbon_storage_efficiency": 0.7,
        "cold_tolerance": 0.2,
        "heat_tolerance": 0.9,
        "drought_tolerance": 0.95,
        "flood_tolerance": 0.1,
        "metabolism_rate": 0.003,
        "growth_partition": 0.3,
        "maintenance_cost": 0.008,
        "storage_partition": 0.5,
        "seed_production": 0.3,
        "seed_size": 2.0,
        "dispersal_radius": 2.0,
        "germination_rate": 0.2,
        "mutation_rate": 0.08,
        "adaptability": 0.9,
        "genetic_stability": 0.85,
    },

    # ────────────────────────────────────────────
    # 🌿 藤本型 — 高生长分配、快速覆盖
    # ────────────────────────────────────────────
    "vine": {
        "max_photosynthesis_rate": 22.0,
        "light_use_efficiency": 0.06,
        "shade_tolerance": 0.5,
        "light_compensation_point": 15.0,
        "light_saturation_point": 500.0,
        "water_use_efficiency": 0.05,
        "nutrient_use_efficiency": 0.5,
        "carbon_storage_efficiency": 0.3,
        "cold_tolerance": 0.3,
        "heat_tolerance": 0.6,
        "drought_tolerance": 0.3,
        "flood_tolerance": 0.2,
        "metabolism_rate": 0.018,
        "growth_partition": 0.7,
        "maintenance_cost": 0.025,
        "storage_partition": 0.15,
        "seed_production": 1.2,
        "seed_size": 0.6,
        "dispersal_radius": 6.0,
        "germination_rate": 0.7,
        "mutation_rate": 0.12,
        "adaptability": 0.6,
        "genetic_stability": 0.6,
    },

    # ────────────────────────────────────────────
    # 🌲 松树型 — 常绿针叶、极长寿、耐寒
    # ────────────────────────────────────────────
    "pine": {
        "max_photosynthesis_rate": 8.0,
        "light_use_efficiency": 0.03,
        "shade_tolerance": 0.3,
        "light_compensation_point": 20.0,
        "light_saturation_point": 700.0,
        "water_use_efficiency": 0.04,
        "nutrient_use_efficiency": 0.4,
        "carbon_storage_efficiency": 0.7,
        "cold_tolerance": 0.85,
        "heat_tolerance": 0.3,
        "drought_tolerance": 0.6,
        "flood_tolerance": 0.2,
        "metabolism_rate": 0.004,
        "growth_partition": 0.35,
        "maintenance_cost": 0.008,
        "storage_partition": 0.5,
        "seed_production": 0.4,
        "seed_size": 3.0,
        "dispersal_radius": 15.0,
        "germination_rate": 0.3,
        "mutation_rate": 0.03,
        "adaptability": 0.4,
        "genetic_stability": 0.95,
    },

    # ────────────────────────────────────────────
    # 🌸 花卉型 — 高繁殖、短命、吸引传粉
    # ────────────────────────────────────────────
    "flower": {
        "max_photosynthesis_rate": 28.0,
        "light_use_efficiency": 0.08,
        "shade_tolerance": 0.3,
        "light_compensation_point": 25.0,
        "light_saturation_point": 600.0,
        "water_use_efficiency": 0.04,
        "nutrient_use_efficiency": 0.5,
        "carbon_storage_efficiency": 0.15,
        "cold_tolerance": 0.2,
        "heat_tolerance": 0.5,
        "drought_tolerance": 0.2,
        "flood_tolerance": 0.3,
        "metabolism_rate": 0.02,
        "growth_partition": 0.65,
        "maintenance_cost": 0.03,
        "storage_partition": 0.1,
        "seed_production": 2.5,
        "seed_size": 0.3,
        "dispersal_radius": 4.0,
        "germination_rate": 0.85,
        "mutation_rate": 0.18,
        "adaptability": 0.8,
        "genetic_stability": 0.4,
    },

    # ────────────────────────────────────────────
    # 🌿 蕨类型 — 孢子繁殖、耐阴、原始植物
    # ────────────────────────────────────────────
    "fern": {
        "max_photosynthesis_rate": 12.0,
        "light_use_efficiency": 0.1,
        "shade_tolerance": 0.8,
        "light_compensation_point": 8.0,
        "light_saturation_point": 250.0,
        "water_use_efficiency": 0.08,
        "nutrient_use_efficiency": 0.4,
        "carbon_storage_efficiency": 0.25,
        "cold_tolerance": 0.4,
        "heat_tolerance": 0.3,
        "drought_tolerance": 0.3,
        "flood_tolerance": 0.6,
        "metabolism_rate": 0.012,
        "growth_partition": 0.55,
        "maintenance_cost": 0.018,
        "storage_partition": 0.2,
        "seed_production": 3.0,
        "seed_size": 0.1,
        "dispersal_radius": 2.0,
        "germination_rate": 0.6,
        "mutation_rate": 0.15,
        "adaptability": 0.5,
        "genetic_stability": 0.5,
    },
}


#: 物种寿命预设（仅保留 max_age，其余生命周期参数由基因推导）
#: key   : 物种标识名
#: value : 最大寿命（小时）
SPECIES_LIFECYCLE: Dict[str, Dict] = {
    "basic":          {"max_age": 8760},
    "fast":           {"max_age": 4320},
    "tree":           {"max_age": 175200},
    "cold_resistant": {"max_age": 13140},
    "drought_resistant": {"max_age": 26280},
    "shade_tolerant": {"max_age": 17520},
    "aquatic":        {"max_age": 8760},
    "succulent":      {"max_age": 26280},
    "vine":           {"max_age": 13140},
    "pine":           {"max_age": 262800},
    "flower":         {"max_age": 2160},
    "fern":           {"max_age": 17520},
}

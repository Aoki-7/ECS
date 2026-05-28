# plant/presets.py
"""
植物物种基因预设与生命周期模板

本模块集中维护所有植物物种的基础基因配置与生命周期参数。
新增物种时，只需在 SPECIES_PRESETS 和 SPECIES_LIFECYCLE 中添加条目即可，
无需修改 PlantFactory 的核心创建逻辑。

基因维度（按功能分类）：
    ─ 光合系统：max_photosynthesis_rate, light_use_efficiency, shade_tolerance
    ─ 温度响应：optimal_temp, cold_tolerance, heat_tolerance
    ─ 水分利用：water_use_efficiency
    ─ 代谢分配：metabolism_rate, growth_partition
    ─ 形态分配：leaf_bias, root_bias, stem_bias, max_height, stem_thickness_factor
    ─ 繁殖策略：seed_production, dispersal_radius
"""

from typing import Dict

#: 物种基因预设表（16 个核心基因）
#: key   : 物种标识名 (str)
#: value : {基因表达目标 -> 基础强度值 (Dict[str, float])}
SPECIES_PRESETS: Dict[str, Dict[str, float]] = {
    # ---- 🌿 基础草本 ----
    # 各项能力均衡，适合作为默认对照组
    "basic": {
        # 光合系统
        "max_photosynthesis_rate": 20.0,   # 最大光合速率
        "light_use_efficiency": 0.05,      # 光能利用效率
        "shade_tolerance": 0.3,            # 耐阴系数
        # 温度响应
        "optimal_temp": 25.0,              # 最佳生长温度 (°C)
        "cold_tolerance": 0.4,             # 耐寒系数
        "heat_tolerance": 0.5,             # 耐热系数
        # 水分利用
        "water_use_efficiency": 0.05,      # 水分利用效率
        # 代谢分配
        "metabolism_rate": 0.01,           # 基础代谢速率
        "growth_partition": 0.6,           # 能量用于生长的分配比例
        # 形态分配
        "leaf_bias": 1.0,                  # 叶片发育偏向
        "root_bias": 1.0,                  # 根系发育偏向
        "stem_bias": 1.0,                  # 茎干发育偏向
        "max_height": 60.0,                # 最大高度 (cm)
        "stem_thickness_factor": 0.15,     # 茎干粗细系数
        # 繁殖策略
        "seed_production": 1.0,            # 种子产量系数
        "dispersal_radius": 3.0,           # 种子传播半径
    },

    # ---- ⚡ 速生杂草 ----
    # 快速生长、高繁殖，寿命短
    "fast": {
        "max_photosynthesis_rate": 35.0,
        "light_use_efficiency": 0.09,
        "shade_tolerance": 0.2,
        "optimal_temp": 28.0,
        "cold_tolerance": 0.2,
        "heat_tolerance": 0.6,
        "water_use_efficiency": 0.06,
        "metabolism_rate": 0.02,
        "growth_partition": 0.7,
        "leaf_bias": 2.0,
        "root_bias": 0.5,
        "stem_bias": 1.0,
        "max_height": 40.0,
        "stem_thickness_factor": 0.08,
        "seed_production": 2.0,
        "dispersal_radius": 5.0,
    },

    # ---- 🌲 乔木 ----
    # 长寿、高大、低繁殖率
    "tree": {
        "max_photosynthesis_rate": 15.0,
        "light_use_efficiency": 0.04,
        "shade_tolerance": 0.5,
        "optimal_temp": 22.0,
        "cold_tolerance": 0.6,
        "heat_tolerance": 0.4,
        "water_use_efficiency": 0.06,
        "metabolism_rate": 0.005,
        "growth_partition": 0.5,
        "leaf_bias": 1.5,
        "root_bias": 1.5,
        "stem_bias": 3.0,
        "max_height": 300.0,
        "stem_thickness_factor": 0.5,
        "seed_production": 0.5,
        "dispersal_radius": 10.0,
    },

    # ---- ❄️ 耐寒型 ----
    # 适应低温环境，耐热性差
    "cold_resistant": {
        "max_photosynthesis_rate": 18.0,
        "light_use_efficiency": 0.06,
        "shade_tolerance": 0.4,
        "optimal_temp": 15.0,
        "cold_tolerance": 0.9,
        "heat_tolerance": 0.2,
        "water_use_efficiency": 0.05,
        "metabolism_rate": 0.008,
        "growth_partition": 0.5,
        "leaf_bias": 0.8,
        "root_bias": 1.5,
        "stem_bias": 0.5,
        "max_height": 40.0,
        "stem_thickness_factor": 0.12,
        "seed_production": 0.8,
        "dispersal_radius": 4.0,
    },

    # ---- 🏜️ 耐旱型 ----
    # 根系发达，水分利用效率高
    "drought_resistant": {
        "max_photosynthesis_rate": 10.0,
        "light_use_efficiency": 0.03,
        "shade_tolerance": 0.2,
        "optimal_temp": 30.0,
        "cold_tolerance": 0.1,
        "heat_tolerance": 0.8,
        "water_use_efficiency": 0.10,
        "metabolism_rate": 0.005,
        "growth_partition": 0.4,
        "leaf_bias": 0.3,
        "root_bias": 3.0,
        "stem_bias": 0.5,
        "max_height": 20.0,
        "stem_thickness_factor": 0.3,
        "seed_production": 0.5,
        "dispersal_radius": 6.0,
    },

    # ---- 🌑 耐阴型 ----
    # 低光环境下高效光合，叶片大而薄
    "shade_tolerant": {
        "max_photosynthesis_rate": 8.0,
        "light_use_efficiency": 0.12,
        "shade_tolerance": 0.9,
        "optimal_temp": 22.0,
        "cold_tolerance": 0.5,
        "heat_tolerance": 0.3,
        "water_use_efficiency": 0.07,
        "metabolism_rate": 0.008,
        "growth_partition": 0.5,
        "leaf_bias": 2.5,
        "root_bias": 0.8,
        "stem_bias": 0.5,
        "max_height": 30.0,
        "stem_thickness_factor": 0.1,
        "seed_production": 0.6,
        "dispersal_radius": 2.0,
    },

    # ---- 💧 水生型 ----
    # 适应水域环境，叶片漂浮或浸没
    "aquatic": {
        "max_photosynthesis_rate": 25.0,
        "light_use_efficiency": 0.07,
        "shade_tolerance": 0.4,
        "optimal_temp": 28.0,
        "cold_tolerance": 0.3,
        "heat_tolerance": 0.6,
        "water_use_efficiency": 0.03,
        "metabolism_rate": 0.015,
        "growth_partition": 0.6,
        "leaf_bias": 2.0,
        "root_bias": 0.3,
        "stem_bias": 1.5,
        "max_height": 80.0,
        "stem_thickness_factor": 0.08,
        "seed_production": 1.5,
        "dispersal_radius": 8.0,
    },

    # ---- 🌵 多肉型 ----
    # 极端耐旱，代谢缓慢，茎干储水
    "succulent": {
        "max_photosynthesis_rate": 6.0,
        "light_use_efficiency": 0.02,
        "shade_tolerance": 0.2,
        "optimal_temp": 32.0,
        "cold_tolerance": 0.2,
        "heat_tolerance": 0.9,
        "water_use_efficiency": 0.15,
        "metabolism_rate": 0.003,
        "growth_partition": 0.3,
        "leaf_bias": 1.5,
        "root_bias": 1.0,
        "stem_bias": 0.5,
        "max_height": 15.0,
        "stem_thickness_factor": 0.6,
        "seed_production": 0.3,
        "dispersal_radius": 2.0,
    },

    # ---- 🌿 藤本型 ----
    # 攀援生长，高叶面积比，快速覆盖
    "vine": {
        "max_photosynthesis_rate": 22.0,
        "light_use_efficiency": 0.06,
        "shade_tolerance": 0.5,
        "optimal_temp": 26.0,
        "cold_tolerance": 0.3,
        "heat_tolerance": 0.6,
        "water_use_efficiency": 0.05,
        "metabolism_rate": 0.015,
        "growth_partition": 0.7,
        "leaf_bias": 2.5,
        "root_bias": 0.5,
        "stem_bias": 2.0,
        "max_height": 120.0,
        "stem_thickness_factor": 0.06,
        "seed_production": 1.2,
        "dispersal_radius": 6.0,
    },
}

#: 物种生命周期预设
#: key   : 物种标识名
#: value : 生命周期参数字典
#:   - max_age          : 最大寿命（小时）
#:   - stage_durations  : 各阶段持续时间 [种子, 幼苗, 营养生长, 成熟, 衰老]
#:   - gdd_requirements : 各阶段所需积温 {阶段号: 积温值}
SPECIES_LIFECYCLE: Dict[str, Dict] = {
    # ---- 🌿 基础草本 ----
    # 寿命约 1 年
    "basic": {
        "max_age": 8760,
        "stage_durations": [48, 168, 720, 4320, 720],
        "gdd_requirements": {0: 10, 1: 30, 2: 80, 3: 0},
    },

    # ---- ⚡ 速生杂草 ----
    # 寿命约 6 个月，阶段转换快
    "fast": {
        "max_age": 4320,
        "stage_durations": [24, 72, 360, 2160, 360],
        "gdd_requirements": {0: 5, 1: 15, 2: 40, 3: 0},
    },

    # ---- 🌲 乔木 ----
    # 寿命约 20 年，成熟期和衰老期极长
    "tree": {
        "max_age": 175200,
        "stage_durations": [720, 2160, 43200, 86400, 8640],
        "gdd_requirements": {0: 20, 1: 50, 2: 200, 3: 0},
    },

    # ---- ❄️ 耐寒型 ----
    # 寿命约 1.5 年
    "cold_resistant": {
        "max_age": 13140,
        "stage_durations": [72, 240, 1080, 6480, 1080],
        "gdd_requirements": {0: 8, 1: 20, 2: 60, 3: 0},
    },

    # ---- 🏜️ 耐旱型 ----
    # 寿命约 3 年
    "drought_resistant": {
        "max_age": 26280,
        "stage_durations": [120, 360, 2160, 12960, 1440],
        "gdd_requirements": {0: 15, 1: 40, 2: 120, 3: 0},
    },

    # ---- 🌑 耐阴型 ----
    # 寿命约 2 年
    "shade_tolerant": {
        "max_age": 17520,
        "stage_durations": [96, 336, 1440, 8640, 1440],
        "gdd_requirements": {0: 8, 1: 25, 2: 60, 3: 0},
    },

    # ---- 💧 水生型 ----
    # 寿命约 1 年，发芽和幼苗期较短
    "aquatic": {
        "max_age": 8760,
        "stage_durations": [48, 120, 480, 4320, 720],
        "gdd_requirements": {0: 12, 1: 35, 2: 90, 3: 0},
    },

    # ---- 🌵 多肉型 ----
    # 寿命约 3 年，种子期较长
    "succulent": {
        "max_age": 26280,
        "stage_durations": [168, 720, 4320, 12960, 2880],
        "gdd_requirements": {0: 20, 1: 50, 2: 150, 3: 0},
    },

    # ---- 🌿 藤本型 ----
    # 寿命约 1.5 年
    "vine": {
        "max_age": 13140,
        "stage_durations": [72, 240, 1080, 6480, 1080],
        "gdd_requirements": {0: 10, 1: 30, 2: 80, 3: 0},
    },
}

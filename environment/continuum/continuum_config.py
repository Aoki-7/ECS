"""
环境连续统 — 可调参数

所有扩散系数、恢复率、边界条件集中配置，方便调参。
"""

from environment.terrain.config.terrain_types import TerrainType

# ════════════════════════════════════════════════
# 🧭 邻域定义
# ════════════════════════════════════════════════

# 邻域类型: "von_neumann"(4邻域) | "moore"(8邻域)
NEIGHBORHOOD_TYPE = "moore"

# 是否为 4-方向边界的邻居偏移:
# von_neumann: [(0,1),(0,-1),(1,0),(-1,0)]
# moore: 加上对角 [(1,1),(1,-1),(-1,1),(-1,-1)]
NEIGHBOR_OFFSETS_VON_NEUMANN = [(0, 1), (0, -1), (1, 0), (-1, 0)]
NEIGHBOR_OFFSETS_MOORE = [(0, 1), (0, -1), (1, 0), (-1, 0),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)]

# ════════════════════════════════════════════════
# 🌡 热扩散参数
# ════════════════════════════════════════════════

# 空气温度扩散系数 (per hour)
# 空气混合快，扩散系数大
TEMP_DIFFUSION_COEFF: float = 0.15

# 土壤温度扩散系数 (per hour) — 比空气慢得多
SOIL_TEMP_DIFFUSION_COEFF: float = 0.03

# 植被覆盖对热扩散的阻尼 (0~1)
# 森林覆盖区域热交换慢
VEGETATION_THERMAL_DAMPING: float = 0.5

# 水域热缓冲系数 — 水体的热容大，温度变化慢
WATER_THERMAL_BUFFER: float = 0.3

# 最大单步温度变化限制 (°C)，防止数值震荡
MAX_TEMP_CHANGE_PER_STEP: float = 2.0

# ════════════════════════════════════════════════
# 💧 湿度扩散参数
# ════════════════════════════════════════════════

# 空气湿度扩散系数 (per hour)
HUMIDITY_DIFFUSION_COEFF: float = 0.12

# 土壤湿度扩散/渗透系数 (per hour)
# 受地形坡度影响，详见系统代码
SOIL_MOISTURE_DIFFUSION_COEFF: float = 0.08

# ════════════════════════════════════════════════
# 🌊 重力水流参数
# ════════════════════════════════════════════════

# 最大水分下坡流速 (soil_moisture fraction per hour per degree slope)
# 实际的流速 = BASE * slope_angle * moisture_factor
WATER_FLOW_BASE_RATE: float = 0.005

# 坡度敏感性指数 — 坡度对水流速度的非线性增益
WATER_FLOW_SLOPE_EXPONENT: float = 1.5

# 最大单步水分变化 (0~1)
MAX_MOISTURE_CHANGE_PER_STEP: float = 0.05

# ════════════════════════════════════════════════
# 🌱 养分扩散参数
# ════════════════════════════════════════════════

# 氮扩散系数 (per hour) — 非常慢
NITROGEN_DIFFUSION_COEFF: float = 0.005
PHOSPHORUS_DIFFUSION_COEFF: float = 0.002
POTASSIUM_DIFFUSION_COEFF: float = 0.003

# ════════════════════════════════════════════════
# 🌬 风驱平流参数
# ════════════════════════════════════════════════

# 风驱平流系数 — 风速(m/s) → 方向性传递强度
WIND_ADVECTION_COEFF: float = 0.02

# 风对温度/湿度的传递方向权重
# 顺风方向 100% 权重，侧风方向降低
WIND_DIRECTIONAL_WEIGHT: float = 0.7

# ════════════════════════════════════════════════
# 🌿 生态自恢复参数
# ════════════════════════════════════════════════

# 各状态量的恢复速率 (per hour) — 恢复到"顶极状态"的速度
# 恢复慢 = 系统有"记忆"；恢复快 = 环境弹性强
RECOVERY_RATE_TEMPERATURE: float = 0.02      # 气温缓慢回归气候基线
RECOVERY_RATE_HUMIDITY: float = 0.015        # 湿度回归
RECOVERY_RATE_MOISTURE: float = 0.01         # 土壤湿度回归（慢）
RECOVERY_RATE_NITROGEN: float = 0.002        # 氮回归（极慢）
RECOVERY_RATE_PHOSPHORUS: float = 0.001      # 磷回归（极慢）
RECOVERY_RATE_POTASSIUM: float = 0.0015      # 钾回归（极慢）

# 自恢复的 sigmoid 形状因子 — 偏离越大恢复越快
# K = 0: 线性恢复; K > 0: 偏离大时恢复更快
RECOVERY_SIGMOID_K: float = 2.0

# ════════════════════════════════════════════════
# 🏞 地形类型 → 气候顶极状态映射
# ════════════════════════════════════════════════

# 每种地形类型对应的"健康"基准状态
# 单元格会缓慢漂移向这个状态（自恢复）
# (temp, humidity, soil_moisture, nitrogen, phosphorus, potassium)
TERRAIN_CLIMAX_STATE = {
    TerrainType.PLAIN:       (25.0, 0.60, 0.35, 50.0, 20.0, 60.0),
    TerrainType.HILL:        (22.0, 0.55, 0.28, 40.0, 15.0, 50.0),
    TerrainType.MOUNTAIN:    (12.0, 0.45, 0.20, 30.0, 10.0, 35.0),
    TerrainType.VALLEY:      (24.0, 0.70, 0.50, 55.0, 25.0, 65.0),
    TerrainType.WATER:       (22.0, 0.95, 1.00, 10.0,  5.0, 20.0),
    TerrainType.LAKE:        (22.0, 0.90, 0.90, 15.0,  8.0, 25.0),
    TerrainType.RIVER:       (21.0, 0.85, 0.80, 20.0, 10.0, 30.0),
    TerrainType.OCEAN:       (22.0, 0.98, 1.00,  5.0,  3.0, 15.0),
    TerrainType.FOREST:      (23.0, 0.72, 0.45, 60.0, 30.0, 70.0),
    TerrainType.GRASSLAND:   (26.0, 0.50, 0.25, 35.0, 15.0, 45.0),
    TerrainType.JUNGLE:      (27.0, 0.85, 0.60, 70.0, 35.0, 80.0),
    TerrainType.DESERT:      (35.0, 0.10, 0.05,  5.0,  2.0, 10.0),
    TerrainType.SWAMP:       (26.0, 0.90, 0.85, 45.0, 20.0, 50.0),
    TerrainType.TUNDRA:      ( 5.0, 0.40, 0.30, 20.0, 10.0, 25.0),
}

# 默认顶极状态（当 terrain_type 不在映射中时使用）
DEFAULT_CLIMAX = (25.0, 0.60, 0.35, 50.0, 20.0, 60.0)

# ════════════════════════════════════════════════
# 🧪 调试与日志
# ════════════════════════════════════════════════

# 启用详细日志
VERBOSE: bool = False

# 最大邻居数（用于归一化扩散）
# moore=8, von_neumann=4
MAX_NEIGHBORS: int = 8

# animal/presets.py
"""
动物物种基因预设模板

本模块集中维护所有动物物种的基础基因配置。
新增物种时，只需在 SPECIES_PRESETS 中添加新的条目即可，
无需修改 AnimalFactory 的核心创建逻辑。
"""

from typing import Dict

#: 物种基因预设表
#: key   : 物种标识名 (str)，如 "basic", "fast", "tank"
#: value : 基因表达目标 -> 基础强度值 (Dict[str, float])
#:
#: 变异机制说明：
#:   实际基因强度 = base_value ± (base_value * variation)
#:   variation 由工厂调用方传入，控制种群内个体差异幅度。
SPECIES_PRESETS: Dict[str, Dict[str, float]] = {
    # ---- 🐾 基础型 ----
    # 各项能力均衡，适合作为默认对照组
    "basic": {
        "max_hunger_rate": 5.0,   # 最大饥饿速率：高值意味着更容易饥饿
        "metabolism_rate": 0.02,  # 代谢速率：基础能量消耗比例
        "optimal_temp": 37.0,     # 最佳体温 (°C)：偏离此值会影响生理效率
        "growth_partition": 0.4,  # 生长分配比例：能量用于生长的占比
        "speed_factor": 1.0,      # 移动速度系数：1.0 为基准倍率
        "sensing_range": 5.0,     # 感知范围：可探测环境/食物/威胁的半径
        "diet_type": 0.5,         # 食性基因：0=纯草食, 1=纯肉食, 0.5=杂食
    },

    # ---- ⚡ 高速型 ----
    # 高机动、高消耗，适合捕食或快速逃避
    "fast": {
        "max_hunger_rate": 8.0,   # 高饥饿速率：高速移动的代价
        "metabolism_rate": 0.04,  # 高代谢：能量消耗更快
        "optimal_temp": 37.0,     # 体温需求与基础型一致
        "growth_partition": 0.3,  # 生长分配降低：更多能量用于活动
        "speed_factor": 2.5,      # 速度倍率显著提升
        "sensing_range": 10.0,    # 广域感知：提前发现威胁或猎物
        "diet_type": 0.5,         # 高速型可草食可肉食，偏杂食
    },

    # ---- 🛡️ 坦克型 ----
    # 高生存、低机动，适合防御或资源匮乏环境
    "tank": {
        "max_hunger_rate": 3.0,   # 低饥饿速率：耐饿
        "metabolism_rate": 0.01,  # 低代谢：能量消耗缓慢
        "optimal_temp": 36.0,     # 略低的最佳体温
        "growth_partition": 0.6,  # 高生长分配：更快积累体型/防御
        "speed_factor": 0.5,      # 速度减半：机动性差
        "sensing_range": 3.0,     # 感知范围缩小：更依赖近距离反应
        "diet_type": 0.3,         # 坦克型偏草食（靠防御吃草）
    },

    # ---- 🐺 捕食者型 ----
    # 顶级食肉动物，高攻击、高消耗、低繁殖
    "predator": {
        "max_hunger_rate": 10.0,  # 极高饥饿速率：肉食获取不稳定
        "metabolism_rate": 0.05,  # 高代谢：维持捕猎所需的高能量
        "optimal_temp": 38.0,     # 较高的最佳体温
        "growth_partition": 0.25, # 低生长分配：更多能量用于捕猎
        "speed_factor": 2.0,      # 高速度：追击猎物
        "sensing_range": 15.0,    # 广域感知：发现远处猎物
        "diet_type": 0.85,        # 捕食者纯肉食
    },

    # ---- 🦌 食草动物型 ----
    # 温和食草，中等速度，适合群居
    "herbivore": {
        "max_hunger_rate": 6.0,   # 中等饥饿速率
        "metabolism_rate": 0.025, # 中等代谢
        "optimal_temp": 37.0,     # 标准体温
        "growth_partition": 0.5,  # 均衡生长分配
        "speed_factor": 1.5,      # 中等偏快速度：逃避捕食者
        "sensing_range": 8.0,     # 中等感知：发现捕食者
        "diet_type": 0.15,        # 食草动物纯草食
    },

    # ---- 🐇 小型食草动物型 ----
    # 小型啮齿类，高繁殖、高警觉、寿命短
    "grass_eater": {
        "max_hunger_rate": 4.0,   # 低饥饿速率：体型小消耗少
        "metabolism_rate": 0.035, # 高代谢率（相对体重）
        "optimal_temp": 37.5,     # 略高体温
        "growth_partition": 0.55, # 较高生长分配：快速成熟
        "speed_factor": 1.8,      # 较快：逃避天敌
        "sensing_range": 6.0,     # 警觉范围
        "diet_type": 0.1,         # 小型食草动物偏草食
    },
}

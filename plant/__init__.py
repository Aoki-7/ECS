#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物系统 — 植物实体、光合作用、种子传播、水分吸收、地形适应

目录结构:
    plant/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── plant_factory.py         # PlantFactory: 按物种预设创建植物实体
    ├── presets.py               # SPECIES_PRESETS / SPECIES_LIFECYCLE: 物种模板与生命周期
    ├── components/              # 植物组件包
    │   ├── plant_component.py     # PlantComponent: 可收获属性 (产量/成熟度/可收获状态)
    │   ├── canopy_component.py    # CanopyComponent: 冠层结构 (叶面积指数/光合效率/遮阴率)
    │   └── root_component.py      # RootComponent: 根系形态 (深度/广度/吸水能力/固土能力)
    ├── systems/               # 植物系统包
    │   ├── photosynthesis_system.py   # PlantPhotosynthesisSystem: PAR → 光合速率
    │   ├── seed_dispersal_system.py   # SeedDispersalSystem: 成熟期种子传播 (圆形散布/边界检查)
    │   ├── water_uptake_system.py     # PlantWaterUptakeSystem: 土壤水分吸收 (根系深度→吸水率)
    │   └── terrain_adaptation_system.py # TerrainAdaptationSystem: 地形生长修正 (海拔/坡度/土壤)
    └── tests/                 # 植物测试包 (10 测试)

核心职责:
    1. 植物实体创建:
       - PlantFactory.create_plant(): 按物种预设创建完整植物实体 (16 组件)
       - PlantFactory.create_batch(): 批量创建
       - PlantFactory.create_plant_from_genome(): 基于亲代基因组的无性繁殖
       - SPECIES_PRESETS: 9 种预设 (basic/fast/tree/cold_resistant/drought_resistant/
         shade_tolerant/aquatic/succulent/vine)
       - 每种包含 23 个纯基因参数，无外观硬编码
       - 生命周期阶段时长由基因实时推导，非硬编码

    2. 植物专属系统:
       - PlantPhotosynthesisSystem (tick=20): 基于 LightReceiverComponent 计算有效 PAR
         与冠层修正光合速率，写入 PhenotypeComponent
       - SeedDispersalSystem (tick=50): 成熟期植物消耗能量进行圆形散布，含边界检查
         与土壤适宜性过滤 (湿度/温度/光照)
       - PlantWaterUptakeSystem (tick=20): 基于根系深度与土壤水分计算吸水率，
         干旱时触发萎蔫/死亡
       - TerrainAdaptationSystem (tick=100): 根据海拔/坡度/土壤类型修正生长速率，
         高海拔/陡坡/贫瘠土壤降低生长

    3. 与环境的深度耦合:
       - 光照: LightFieldSystem → LightReceiverComponent → 光合速率
       - 土壤: SoilSystem → SoilWaterBalanceSystem → 水分吸收
       - 气候: ClimateSystem/PhysicalWeatherSystem → 温度/降水 → 生长/死亡
       - 地形: TerrainSystem → 海拔/坡度 → 生长修正

与其他模块的关系:
    - core/: 依赖 ECS 框架
    - biology/: 复用 Genome/Energy/LifeCycle/Morphology 组件
    - biology/systems/: 统一调度生长/衰老/死亡
    - environment/: 深度耦合 (光照/土壤/气候/地形)
    - animal/: GrazingSystem 读取 PlantComponent，消耗植物产量
    - resource/: PlantComponent 继承 ResourceComponent (可收获资源)
    - space/: 使用 SpatialIndex 进行位置管理和邻居查询

设计原则:
    - 基因驱动: 所有植物属性由基因表达，无外观硬编码
    - 环境响应: 植物生长完全由环境因子驱动 (光照/水分/温度/土壤)
    - 能量守恒: 光合作用产生能量，所有活动消耗能量
    - 生命周期: 种子→发芽→生长→成熟→繁殖→衰老→死亡

版本: v4.0
"""

from .plant_factory import PlantFactory
from .presets import SPECIES_PRESETS, SPECIES_LIFECYCLE

# 组件
from .components.plant_component import PlantComponent
from .components.canopy_component import CanopyComponent
from .components.root_component import RootComponent

# 系统
from .systems.photosynthesis_system import PlantPhotosynthesisSystem
from .systems.seed_dispersal_system import SeedDispersalSystem
from .systems.water_uptake_system import PlantWaterUptakeSystem
from .systems.terrain_adaptation_system import TerrainAdaptationSystem

__all__ = [
    # 工厂与预设
    "PlantFactory",
    "SPECIES_PRESETS",
    "SPECIES_LIFECYCLE",
    # 组件
    "PlantComponent",
    "CanopyComponent",
    "RootComponent",
    # 系统
    "PlantPhotosynthesisSystem",
    "SeedDispersalSystem",
    "PlantWaterUptakeSystem",
    "TerrainAdaptationSystem",
]

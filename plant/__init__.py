#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物系统模块 — 植物实体的创建、组件管理与生态模拟

Plant 模块是 ECS 世界模拟系统中负责植物生态的核心子系统，
涵盖从实体创建、基因表达、光合作用、水分吸收到种子传播的完整生命周期。

─────────────────────────────────────────────────────────────────
目录结构
─────────────────────────────────────────────────────────────────
plant/
├── __init__.py                    # 本文件：模块入口与公共接口导出
├── plant_factory.py               # PlantFactory：植物实体工厂
├── presets.py                     # SPECIES_PRESETS / SPECIES_LIFECYCLE
├── components/
│   ├── plant_component.py         # PlantComponent：可收获属性
│   ├── canopy_component.py        # CanopyComponent：冠层结构与光合效率
│   └── root_component.py          # RootComponent：根系形态与吸水能力
├── systems/
│   ├── photosynthesis_system.py   # PlantPhotosynthesisSystem：PAR → 光合速率
│   ├── seed_dispersal_system.py   # SeedDispersalSystem：成熟期种子传播
│   ├── water_uptake_system.py     # PlantWaterUptakeSystem：土壤水分吸收
│   └── terrain_adaptation_system.py  # TerrainAdaptationSystem：地形生长修正
└── tests/
    └── test_plant.py              # 52 项单元测试（工厂/组件/系统全覆盖）

─────────────────────────────────────────────────────────────────
核心职责
─────────────────────────────────────────────────────────────────
1. 实体创建
   - PlantFactory.create_plant()      : 按物种预设创建完整植物实体（16 组件）
   - PlantFactory.create_batch()      : 批量创建
   - PlantFactory.create_plant_from_genome() : 基于亲代基因组的无性繁殖

2. 物种预设（9 种）
   - basic, fast, tree, cold_resistant, drought_resistant,
     shade_tolerant, aquatic, succulent, vine
   - 每种包含 23 个纯基因参数，无任何外观硬编码
   - 生命周期阶段时长由基因实时推导，非硬编码

3. 植物专属系统（4 个）
   - PlantPhotosynthesisSystem (tick=20) : 基于 LightReceiverComponent 计算
     有效 PAR 与冠层修正光合速率，写入 PhenotypeComponent
   - SeedDispersalSystem (tick=50)       : 成熟期植物消耗能量进行圆形散布，
     含边界检查与土壤适宜性过滤（湿度 < 凋萎点则跳过）
   - PlantWaterUptakeSystem (tick=20)    : 从 SoilComponent 吸收水分，计算
     水分胁迫并写入 PhenotypeComponent，同步降低土壤湿度
   - TerrainAdaptationSystem (tick=20)   : 根据 TerrainComponent 类型与坡度
     修正 max_photosynthesis_rate，并调整水分胁迫基线

4. 植物专属组件（3 个）
   - PlantComponent  : 可收获量、产量类型、是否多年生、木材产出
   - CanopyComponent : 叶面积指数(LAI)、冠层半径、遮光率、光合效率
   - RootComponent   : 根深、根半径、吸水速率、养分吸收速率、当前吸水量

─────────────────────────────────────────────────────────────────
与外部模块的关系
─────────────────────────────────────────────────────────────────
与 biology/ 的关系：
    - 植物是最基础的生物实体，直接体现 gene → phenotype → growth 管线
    - 依赖 GenomeComponent、PhenotypeComponent、LifeCycleComponent、
      EnergyComponent、MorphologyComponent 等生物学基础组件
    - 种子繁殖由 BiologyReproductionSystem（基础短距离）与
      SeedDispersalSystem（策略性长距离）双系统协同

与 environment/ 的关系：
    - 光合作用依赖 environment/light_field/ 的 LightReceiverComponent
    - 水分吸收读取 environment/soil/ 的 SoilComponent（湿度/凋萎点/田间持水量）
    - 地形适应读取 environment/terrain/ 的 TerrainComponent（类型/坡度）

与 resource/ 的关系：
    - 成熟植物挂载 ResourceComponent，可被人类砍伐转化为木材（resource/wood/）
    - 果实可作为食物（resource/food/），产量由 PlantComponent.harvestable_yield 决定
    - 植物本身也是动物的觅食目标（animal/grazing_system.py）

与 human/ 的关系：
    - 人类通过 SearchSystem 发现植物，HarvestSystem 采集收获
    - PlantingSystem 可主动种植（调用 PlantFactory）
    - 成熟植物的 SpaceComponent 参与空间索引查询

─────────────────────────────────────────────────────────────────
测试
─────────────────────────────────────────────────────────────────
单元测试位于 plant/tests/test_plant.py，共 52 个用例，覆盖：
    - PlantFactory（创建/批量/遗传/异常/可复现性）
    - Presets（完整性/基因范围/物种多样性）
    - Components（默认值 / __slots__）
    - PlantPhotosynthesisSystem（零光照/遮光/公式计算/trait 标记）
    - SeedDispersalSystem（条件判定/边界/干旱过滤/能量消耗/子代继承）
    - PlantWaterUptakeSystem（无土壤/吸水/湿度下降/胁迫分级/trait 标记）
    - TerrainAdaptationSystem（各地形修正/坡度惩罚/水分奖励/trait 标记）
    - Integration（完整流水线 / 多物种共存 / 批量稳定性）
"""

from .plant_factory import PlantFactory
from .presets import SPECIES_PRESETS, SPECIES_LIFECYCLE

from .components.plant_component import PlantComponent
from .components.canopy_component import CanopyComponent
from .components.root_component import RootComponent

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

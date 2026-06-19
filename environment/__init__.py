#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境系统 — 多层级物理环境模拟（大气/气候/光照/土壤/地形）

目录结构:
    environment/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── components/              # 环境组件包
    │   ├── environment_component.py   # EnvironmentComponent: 环境状态 (温度/湿度/光照/天气)
    │   ├── climate_component.py     # ClimateComponent: 气候参数 (年均温/降水/季节强度)
    │   ├── soil_component.py        # SoilComponent: 土壤状态 (水分/温度/肥力/养分)
    │   ├── terrain_component.py     # TerrainComponent: 地形参数 (海拔/坡度/类型/通行性)
    │   └── water_component.py       # WaterComponent: 水体状态 (水位/流速/水质)
    ├── systems/               # 环境系统包 (5 层 DAG 管线)
    │   ├── solar_position_system.py   # SolarPositionSystem: 太阳位置计算 (赤纬角/时角)
    │   ├── solar_radiation_system.py  # SolarRadiationSystem: TOA 辐射量
    │   ├── season_system.py           # SeasonSystem: 季节驱动 (天文参数/日长变化)
    │   ├── climate_system.py          # ClimateSystem: 长期气候趋势 (Ornstein-Uhlenbeck)
    │   ├── physical_weather_system.py # PhysicalWeatherSystem: 物理天气 (温度/湿度/云量/降水/风速)
    │   ├── light_atmosphere_coupling_system.py # LightAtmosphereCouplingSystem: 光-大气耦合
    │   ├── light_field_system.py      # LightFieldSystem: 辐射场 (直射/散射/地表光照)
    │   ├── weather_event_system.py    # WeatherEventSystem: 天气事件生成 (暴雨/干旱/风暴)
    │   ├── weather_lifetime_system.py # WeatherLifetimeSystem: 天气事件生命周期
    │   ├── soil_temperature_system.py # SoilTemperatureSystem: 土壤温度 (热传导)
    │   ├── soil_water_balance_system.py # SoilWaterBalanceSystem: 土壤水分平衡 (降水/蒸发/径流)
    │   ├── soil_system.py             # SoilSystem: 土壤综合状态 (肥力/养分/生物活性)
    │   ├── environment_sync_system.py # EnvironmentSyncSystem: 环境状态同步
    │   └── environmental_continuum_system.py # EnvironmentalContinuumSystem: 空间平滑 (扩散/平流)
    ├── atmosphere/            # 大气子模块
    │   └── ...                  # 气压/风场/对流/热力学
    ├── climate/               # 气候子模块
    │   └── ...                  # 长期气候趋势/随机过程
    ├── season/                # 季节子模块
    │   └── ...                  # 天文参数/日长变化
    ├── physics_weather/       # 物理天气子模块
    │   └── ...                  # 连续物理量天气系统
    ├── light_field/           # 光场子模块
    │   ├── components/            # 光场组件
    │   ├── system/                # 光场系统
    │   └── systems/               # 光场系统群
    ├── soil/                  # 土壤子模块
    │   ├── components/            # 土壤组件
    │   └── systems/               # 土壤系统
    ├── terrain/               # 地形子模块
    │   └── systems/               # 地形系统
    ├── continuum/             # 连续统子模块
    │   └── ...                  # 相邻单元格间物理扩散与平流
    ├── observation/           # 观测子模块
    │   └── ...                  # 天气状态推导/异常检测
    ├── memory/                # 环境历史子模块
    │   └── ...                  # 历史数据存储与统计
    └── tests/                 # 环境测试包

核心职责:
    1. 环境实体管理:
       - 每个空间单元格对应一个 EnvironmentEntity
       - 环境实体包含: 温度/湿度/光照/天气/土壤/地形/水体
       - 环境状态供所有生物系统查询

    2. 5 层 DAG 环境管线 (按 SystemScheduler 依赖图排序):
       Layer 1 — 外部强迫:
         SolarPositionSystem → SolarRadiationSystem → SeasonSystem → ClimateSystem
       Layer 2 — 大气物理:
         PhysicalWeatherSystem → LightAtmosphereCouplingSystem
       Layer 3 — 辐射:
         LightFieldSystem
       Layer 4 — 地表层:
         WeatherEventSystem → WeatherLifetimeSystem → SoilTemperatureSystem
         → SoilWaterBalanceSystem → SoilSystem → EnvironmentSyncSystem
       Layer 5 — 空间平滑:
         EnvironmentalContinuumSystem (热扩散/湿度扩散/水流/风驱平流)

    3. 连续物理世界观:
       - 摒弃硬编码状态机，所有天气/季节由物理量实时推导
       - 空间连续性: 通过 continuum 模块使相邻单元格互相影响
       - 时间连续性: Season/Climate 提供长期趋势，Weather 提供短期波动

与其他模块的关系:
    - core/: 依赖 ECS 框架
    - space/: 使用 SpatialIndex 进行空间单元格管理
    - time_module/: 使用 TimeModule 进行时间推进和事件调度
    - biology/: 环境因素驱动生物生长/健康/能量 (温度→代谢/光照→光合)
    - animal/: 环境因素驱动动物行为 (天气→迁徙/温度→能量消耗)
    - plant/: 环境因素驱动植物生长 (光照→光合/土壤→水分/温度→生长)
    - human/: 环境因素驱动人类生理需求 (温度→体温/天气→行动限制)
    - civilization/: 气候影响农业产量，进而影响文明发展

设计原则:
    - 连续物理: 摒弃离散状态机，所有状态由物理量连续推导
    - 空间耦合: 相邻单元格互相影响 (扩散/平流/辐射)
    - 时间耦合: 长期趋势 + 短期波动 = 完整环境动态
    - 可查询: 所有生物系统可随时查询任意位置的环境状态

版本: v4.0
"""

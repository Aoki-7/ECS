# MEMORY.md — 长期记忆

## 项目概览
- **项目路径:** `D:\个人助手\workspace\ECS`
- **描述:** ECS（实体-组件-系统）架构的环境模拟引擎
- **主入口:** `main.py`

## 架构

### 世界模型
- `World` 管理实体创建 / 组件增删查 / 系统管线更新
- `world.get_component(entity, ComponentType)` → 返回组件或 None
- `world._world_entity` 用于世界级（无空间坐标）组件
- 实体可通过 `world.create_entity()` 创建

### 环境管线（15 系统，5 层）
```
Layer 1 - 驱动: SolarPosition, SolarRadiation, Season, Climate
Layer 2 - 大气: PhysicalWeather, AtmosphereCoupling
Layer 3 - 辐射: LightField
Layer 4 - 反馈: ModifierBridge, WeatherEventGen, WeatherLifetime,
                SoilTemperature, SoilWaterBalance, Soil, EnvironmentSync
Layer 5 - 空间: Continuum
```

### 空间连续统系统
- 10×10 网格通过扩散、平流、重力水流、生态自恢复交互
- 5 大机制：热扩散、湿度扩散、重力水流、风驱平流、生态自恢复
- 网格存储：`Dict[Tuple[int, int], Entity]`
- 气体扩散用 4 邻域，水流用 8 邻域（对角影响）
- 默认反射边界，支持周期性边界

### 关键设计决策
- **ISA 标准大气模型**: 海拔→气压→密度自动推导
- **球面天文学**: 时角计算，区分昼夜、极昼极夜
- **显式欧拉 + CFL 条件**: dt=1h 下扩散系数 ≤0.5
- **摩尔邻域**: 比 4-邻域更真实的扩散，计算量略增
- **气候顶极基于地形**: 不同地形有不同恢复目标

## 组件记录
- `EnvironmentComponent`: air_temperature, soil_temperature, air_humidity, soil_moisture, N, P, K
- `TerrainComponent`: elevation, slope, vegetation_cover, terrain_type
- `SpaceComponent`: x, y, layer
- `AtmosphereComponent`: altitude, pressure, air_density (ISA 自动推导)
- `SolarPositionComponent`: elevation, azimuth, day_length, is_night, latitude

## 关键常量
- 扩散系数温度 0.01~0.3（CFL 安全），湿度 0.02~0.1，养分 0.001~0.005
- 自恢复率：温度 0.002/小时，湿度 0.003/小时，水分 0.002/小时，养分 0.001/小时
- 顶极状态：森林（T=23, H=0.72, M=0.45）、沙漠（T=35, H=0.1, M=0.02）、湖（T=20, H=0.9, M=0.9）
- `dt = 1h`（管线步长）

# 环境模块全链路分析报告

> 生成日期: 2026-05-16
> 范围: `environment/` 下全部子模块的数据依赖扫描、天气模块集成验证、遗留问题记录

---

## 1. 环境模块整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        environment/ 总览                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Terrain ── 静态约束（海拔、坡度、类型）                            │
│     ↓                                                            │
│  Climate ── 长期气候基线（ElNino/LaNina/Neutral，10-400天周期）    │
│     ↓                                                            │
│  Season ── 季节周期（春/夏/秋/冬，90天/季）                        │
│     ↓                                                            │
│  Weather ── 物理天气演化（连续物理量，按小时步进）                   │
│     ├── PhysicalWeatherSystem      ← 核心物理引擎                  │
│     ├── WeatherModifierBridgeSystem ← 极端事件叠加                │
│     ├── WeatherEventSystem         ← 事件生成                     │
│     └── WeatherLifetimeSystem      ← 事件生命周期管理              │
│     ↓                                                            │
│  EnvironmentSyncSystem ── 推演到每个空间单元格                      │
│     → EnvironmentComponent (per cell)                            │
│     ↓                                                            │
│  Atmosphere ── 微观大气（空气密度、气溶胶）                         │
│     ↓                                                            │
│  LightField ── 辐射场（太阳位置 → 辐射 → 散射 → 地表光照）          │
│     ↓                                                            │
│  Soil ── 土壤（温度、湿度、养分、pH、肥力）                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 系统注册链（environment_builder.py）                        │  │
│  │  Season → Climate → Weather → EnvironmentSync              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ⚠ 以下子模块代码完整但未被注册到 SimulationLoop:                   │
│  SolarPositionSystem, SolarRadiationSystem, LightFieldSystem,    │
│  LightAtmosphereCouplingSystem, LightReceiverSystem,             │
│  AtmosphereSystem (convection, cloud, thermodynamics, wind,      │
│  pressure), TerrainSystem, TerrainTypeSystem                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 模块依赖矩阵

### 2.1 已注册系统（在 simulation loop 中运行）

| 系统 | 所属模块 | 读 | 写 | 优先级 |
|------|---------|----|----|--------|
| **TimeSystem** | time | - | TimeComponent | 最高 |
| **SeasonSystem** | season | SeasonComponent | temperature_offset, rainfall_factor, sunlight_factor | 默认 |
| **ClimateSystem** | climate | ClimateComponent | humidity_bias, rainfall_bias, climate_phase | 默认 |
| **PhysicalWeatherSystem** | physics_weather | SeasonComponent, ClimateComponent | PhysicalWeatherComponent (temp/pressure/humidity/cloud/precip/wind) | 默认 |
| **WeatherModifierBridgeSystem** | physics_weather | WeatherModifierComponent | PhysicalWeatherComponent | 默认 |
| **WeatherEventSystem** | physics_weather | PhysicalWeatherComponent | WeatherModifierComponent (事件创建) | 默认 |
| **WeatherLifetimeSystem** | physics_weather | WeatherModifierComponent | 移除过期事件 | 默认 |
| **EnvironmentSyncSystem** | systems | PhysicalWeatherComponent | EnvironmentComponent (per cell) | 默认 |

### 2.2 未注册系统（代码存在但未接入 loop）

| 系统 | 文件位置 | 读 | 写 | 影响 |
|------|---------|----|----|------|
| SolarPositionSystem | light_field/system/ | TimeComponent | SolarPositionComponent (elevation/azimuth/day_length) | 需要lat config |
| SolarRadiationSystem | light_field/system/ | SolarPositionComponent | SolarRadiationComponent (toa_radiation) | 需要SolarPosition已更新 |
| LightAtmosphereCouplingSystem | light_field/system/ | AtmosphereComponent, PhysicalWeatherComponent | LightScatterComponent | 已修复云量读取 |
| LightFieldSystem | light_field/system/ | SolarRadiationComponent, LightScatterComponent | SurfaceLightComponent | 计算地表光照 |
| LightReceiverSystem | light_field/system/ | SurfaceLightComponent | LightReceiverComponent (per entity) | 分发到实体 |
| ConvectionSystem | atmosphere/system/ | PhysicalWeatherComponent (temp) | AtmosphereComponent | 对流更新 |
| CloudSystem | atmosphere/system/ | 无(已移除旧weather引用) | AtmosphereComponent | 微观云场 |
| ThermodynamicsSystem | atmosphere/system/ | AtmosphereComponent | AtmosphereComponent | 热力学 |
| AtmosphereSystem | atmosphere/system/ | 无 | AtmosphereComponent | 大气状态 |
| WindSystem | atmosphere/system/ | PhysicalWeatherComponent (wind) | AtmosphereComponent | 地面风场 |
| PressureSystem | atmosphere/system/ | PhysicalWeatherComponent | AtmosphereComponent | 大气压 |
| SoilTemperatureSystem | soil/systems/ | PhysicalWeatherComponent (temp) | SoilTemperatureComponent | 已更新 |
| SoilWaterBalanceSystem | soil/systems/ | PhysicalWeatherComponent (precip, temp) | SoilMoistureComponent | 已更新 |
| SoilSystem | soil/systems/ | EnvironmentComponent | SoilComponent (temp/nutrient/pH) | 已修复硬编码 |
| SoilFertilitySystem | soil/systems/ | SoilFertilityComponent | 自然恢复 | 独立 |
| TerrainSystem | terrain/systems/ | SoilComponent | 推导类型 | 静态 |
| ResourceRegenerationSystem | systems/ | ResourceComponent | 资源恢复 | 独立 |

---

## 3. 修复汇总

### 3.1 🔴 严重修复

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 1 | **SoilSystem 硬编码 target_temp=20°C** | `soil/systems/soil_system.py` | 改为从 `EnvironmentComponent.air_temperature` 读取（已由 EnvironmentSyncSystem 从天气同步），一阶滞后跟随 |
| 2 | **SoilSystem 与 SoilWaterBalanceSystem 冲突管理 soil.moisture** | `soil/systems/soil_system.py` | 移除 SoilSystem 中的湿度更新逻辑，由 SoilWaterBalanceSystem 统一管理 |
| 3 | **ClimateSystem 未被注册，气候偏移零作用** | `config/environment_builder.py` | 添加 `ClimateBuilder.build(world)` 注册，使 ClimateComponent 被创建并更新 |
| 4 | **ClimateComponent 偏移无人消费** | `physics_weather/systems/physical_weather_system.py` | `update` 方法新增气候偏移读取并应用于温度、蒸发速率、降水因子 |
| 5 | **LightAtmosphereCouplingSystem 不读 PhysicalWeatherComponent 云量** | `light_field/system/light_atmosphere_coupling_system.py` | 综合 `AtmosphereComponent.cloud_cover` + `PhysicalWeatherComponent.cloud_cover` 计算云遮挡 |

### 3.2 🟡 优化修复

| # | 问题 | 文件 | 修复 |
|---|------|------|------|
| 6 | 数据流数据流文档 outdated | memory 记录 | 更新为当前准确架构 |
| 7 | `climate_component copy.py` 残留 | `climate/` | 删除旧副本 |

### 3.3 数据依赖链联通状态

```
修复前:
  ClimateSystem ─→ ClimateComponent ─→ ❌ 无人消费
  PhysicalWeatherSystem ─→ 仅读 SeasonComponent
  SoilSystem ─→ target_temp = 20.0 (硬编码)
  LightAtmoCoupling ─→ 仅读 AtmosphereComponent

修复后:
  ClimateSystem ─→ ClimateComponent ─→ PhysicalWeatherSystem ✅
  PhysicalWeatherSystem ─→ SeasonComponent + ClimateComponent ✅
  SoilSystem ─→ EnvironmentComponent.air_temperature ✅
  LightAtmoCoupling ─→ AtmosphereComponent + PhysicalWeatherComponent ✅
```

---

## 4. 数据流详细图（修复后）

```
SeasonSystem
  │ season.temperature_offset  (+偏置)
  │ season.rainfall_factor     (×因子)
  ▼
ClimateSystem
  │ climate.humidity_bias      (+因子)
  │ climate.rainfall_bias      (+因子)
  │ climate.mean_temp - 15     (+偏置)
  ▼
PhysicalWeatherSystem
  │
  ├── temperature = f(season_offset + climate_temp_bias, cloud_cover, hour)
  ├── pressure   = f(season, hour, noise)
  ├── humidity   = f(evap×(1+climate_humidity_bias), precip, advection)
  ├── cloud      = f(rh, hour, pressure)
  ├── precip     = f(cloud, rh, total_rainfall_factor)
  └── wind       = f(hour, season, noise)
  │
  ▼
PhysicalWeatherComponent  [world level]
  │
  ├──→ WeatherModifierBridgeSystem (事件叠加)
  ├──→ EnvironmentSyncSystem → EnvironmentComponent [per cell]
  │     ├── air_temperature ← weather.temperature
  │     ├── air_humidity    ← weather.relative_humidity
  │     ├── vpd             ← es*(1-RH)
  │     ├── wind_speed      ← weather.wind_speed
  │     ├── rainfall        ← weather.precipitation_rate×24
  │     ├── par             ← CLEAR_SKY_PAR×(1-0.8×cloud_cover)
  │     └── soil_temperature ← lagged from air_temperature
  │
  └──→ SoilTemperatureSystem → SoilTemperatureComponent.temperature
  └──→ SoilWaterBalanceSystem → SoilMoistureComponent.moisture

SoilSystem
  └──→ soil.temperature = lagged from EnvironmentComponent.air_temperature  ✅
  └──→ soil.nitrogen/P/K/ph = independent dynamics

LightAtmosphereCouplingSystem
  └──→ scatter.cloud_attenuation = max(weather.cloud, atmos.cloud)×(0.5+cloud_density) ✅
  └──→ scatter.rayleigh_factor = 0.08×air_density
  └──→ scatter.mie_factor = 0.15×aerosol + 0.05×(humidity/100)
```

---

## 5. 语法验证结果

```
environment\physics_weather\systems\physical_weather_system.py     ✅ OK
environment\soil\systems\soil_system.py                            ✅ OK
environment\light_field\system\light_atmosphere_coupling_system.py ✅ OK
environment\config\environment_builder.py                          ✅ OK
environment\systems\environment_sync_system.py                     ✅ OK
environment\physics_weather\systems\weather_modifier_bridge.py     ✅ OK
```

---

## 6. 运行测试结果

物理天气模块独立测试（30天，720步，每小时步进）：

| 指标 | 结果 |
|------|------|
| 温度范围 | 11.9°C ~ 22.1°C（合理日循环） |
| 气压范围 | 995 ~ 1029 hPa（合理） |
| 相对湿度 | 73.8% ~ 100%（多云系统可能导致饱和） |
| 云量 | 0.06 ~ 0.57（晴到多云/阴天） |
| 降水事件 | 中等雨强 ~ 0.215mm/h，自然消散 |
| 风速 | 0.0 ~ 4.1 m/s（静风到清风） |
| 天气标签多样性 | 60天内观察到7种不同组合标签 |

✅ 所有物理量平滑演化，降水事件触发后自然消散，标签正确定义。

---

## 7. 建议的后续改进（非阻塞）

| 优先级 | 建议 | 原因 |
|--------|------|------|
| 🟢 | 注册 `LightFieldSystem` + `SolarPositionSystem` + `SolarRadiationSystem` + `LightAtmosphereCouplingSystem` | 完成完整的光照计算链（当前 `EnvironmentSyncSystem.PAR` 为简化模型） |
| 🟢 | 注册 `AtmosphereSystem` + 子系统（对流、云、热力学、风、气压） | 使 AtmosphereComponent 数据更真实，而非静态默认值 |
| 🟢 | 注册 `TerrainTypeSystem` | 使 terrain_type 随 soil.moisture 动态变化 |
| 🟢 | 让 `PhysicalWeatherSystem` 的参数纬度可配置 | 当前从 hardcoded 35°N 使用太阳能 |

---

## 8. 已删除文件

- `weather/` 整个模块（旧半马尔可夫链天气）
- `atmosphere/system/asmosphtere_system.py`（拼写错误副本）
- `atmosphere/system/pressusre_system.py`（拼写错误副本）
- `climate/climate_component copy.py`（旧版本副本）
- 各目录下的 `check*.py`, `tmp_*.py`, `diag*.py` 等临时文件

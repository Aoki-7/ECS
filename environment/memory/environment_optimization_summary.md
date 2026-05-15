# 环境模块全链路优化 — 优化总结

## 优化目标

> "有确定的输入输出变量，有随时间推移变化的互相影响的真实环境物理量，整体逻辑自洽且方便扩展"

## 一、架构变革

### 优化前
```
系统各自独立运行，无协调器
执行顺序由 builder 硬编码列表隐式决定
光照链路断开（SolarPosition → SolarRadiation → LightField 未被注册）
两套重复 LightFieldSystem（system/ + systems/）
ClimateSystem 未继承 System 基类
```

### 优化后
```
EnvironmentPipeline (pipeline.py) — 统一编排 14 个子系统
  4 层 DAG 数据流：
  Layer 1: 外部强迫 [SolarPosition → SolarRadiation → Season → Climate]
  Layer 2: 大气物理 [PhysicalWeather → AtmosphereCoupling → LightField]
  Layer 3: 极端事件 [ModifierBridge → WeatherEventGen → WeatherLifetime]
  Layer 4: 地表层   [SoilTemperature → SoilWaterBalance → Soil → EnvironmentSync]
```

## 二、核心改动

| 文件 | 改动 |
|------|------|
| `environment/pipeline.py` | **新文件** — `EnvironmentPipeline` 管线编排器 |
| `environment/config/environment_builder.py` | 重写 — 创建所有 world-level 组件 + 14 系统管线条目 |
| `main.py` | `env_systems` 列表 → `env_pipeline.update()` |
| `environment/climate/climate_system.py` | 继承 `System` 基类，添加 `Neutral` 偏置归零 |
| `environment/light_field/components/surface_light_component.py` | 修复 dataclass slots 缺少类型注解的 bug |
| `light_field/systems/` | **删除** — 重复的 per-cell LightFieldSystem |
| `environment/physics_weather/systems/physical_weather_system.py` | 前序修复：气候偏置 + ClimateComponent 耦合 |

## 三、14 系统管线 I/O 契约

| # | 系统 | 输入 | 输出 |
|---|------|------|------|
| 0 | SolarPosition | TimeComponent | SolarPositionComponent (elevation, azimuth, day_length) |
| 1 | SolarRadiation | SolarPositionComponent | SolarRadiationComponent (toa_radiation) |
| 2 | Season | TimeComponent | SeasonComponent (temp_offset, rain_factor, sun_factor) |
| 3 | Climate | TimeComponent | ClimateComponent (bias, phase) |
| 4 | PhysicalWeather | SeasonComponent + ClimateComponent | PhysicalWeatherComponent (T, P, RH, cloud, precip, wind) |
| 5 | AtmosphereCoupling | AtmosphereComponent + PhysicalWeatherComponent | LightScatterComponent |
| 6 | LightField | SolarRadiationComponent + LightScatterComponent | SurfaceLightComponent |
| 7 | ModifierBridge | WeatherModifierComponent | PhysicalWeatherComponent (叠加 deltas) |
| 8 | WeatherEventGen | PhysicalWeatherComponent | WeatherModifierComponent (创建事件) |
| 9 | WeatherLifetime | WeatherModifierComponent | 清理过期事件 |
| 10 | SoilTemperature | PhysicalWeatherComponent.temperature | SoilTemperatureComponent |
| 11 | SoilWaterBalance | PhysicalWeatherComponent.precip/temp | SoilMoistureComponent |
| 12 | Soil | EnvironmentComponent.air_temp | SoilComponent (N, P, K, pH) |
| 13 | EnvironmentSync | PhysicalWeatherComponent + SurfaceLightComponent | EnvironmentComponent (per-cell) |

## 四、物理反馈链路

```
温度 ──→ 饱和水汽压 ──→ 相对湿度 ──→ 云量
  ↑                                        │
  └──────── 云量阻尼 (cloud_damping) ───────┘

云量 + RH ──→ 降水 ──→ 绝对湿度下降
            │
            └──→ 云遮挡 ──→ 衰减 PAR ──→ 地表光照

气压梯度 ──→ 风速 ──→ 蒸发 ──→ 湿度 (下一帧)

季节偏置 + 气候偏置 ──→ 温度/降雨基准线

(来自外部强迫层) 太阳赤纬 ──→ 太阳高度角 ──→ TOA辐射
                                             │
                     云量遮挡 ←──────────────┤
                          │                  │
                     地表直射光           地表散射光
```

## 五、扩展指南

在 `environment_builder.py` 的 `build()` 方法中添加新系统只需 3 步：

```python
# 1. 创建组件（如果需要）
world._world_entity.add_component(XxxComponent())

# 2. 创建系统实例
xxx_system = XxxSystem(params...)

# 3. 插入管线条目列表的对应 LAYER 位置
entries.append((xxx_system, "XxxName", "输入 → 输出说明"))
```

无需修改 `pipeline.py`、`main.py` 或任何其他文件。

## 六、验证结果

- 所有 9 个修改/新建文件通过 `py_compile` 语法验证 ✅
- 管线加载：14 个系统全部注册，顺序正确 ✅
- 物理天气测试：30 天模拟通过，物理量平滑演化 ✅
- 已删除 2 个重复/冗余文件 + 1 个空目录 + 1 个临时文件 ✅

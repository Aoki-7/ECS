# 环境子模块集成判断 — 分析结论

> 判断标准：**模块创建的数据是否有外部消费者？**
> 没有消费者的模块注册后只是在空转 CPU。

---

## ✅ 已集成（正常运转）

| 模块 | 数据流向 | 消费者 |
|------|---------|--------|
| **Season** | SeasonComponent → PhysicalWeatherSystem | 🌡 温度偏移、降雨因子 |
| **Climate** | ClimateComponent → PhysicalWeatherSystem | 🌡 气候偏置（刚接通） |
| **Weather (physics_weather)** | PhysicalWeatherComponent ← PhysicalWeatherSystem | 核心天气引擎 |
| **EnvironmentSync** | PhysicalWeatherComponent → EnvironmentComponent (per-cell + world) | 📌 关键桥梁 |
| **Soil** | EnvironmentComponent.air_temperature → SoilComponent.temperature | 土壤养分循环 |
| **SoilWaterBalance** | PhysicalWeatherComponent → SoilMoistureComponent | 水分平衡 |
| **Observation** | PhysicalWeatherComponent → 观测记录 | 环境感知 |

**数据链路：**
```
Season + Climate
     ↓
PhysicalWeatherSystem ← PhysicalWeatherComponent
     ↓
EnvironmentSyncSystem
     ↓
EnvironmentComponent (per-cell) ← 生理系统、土壤系统实际读这里
```

---

## ❌ 不应当集成（当前版本）

### 1. LightField 模块 ❌

| 组件 | 状态 | 证据 |
|------|------|------|
| `LightFieldComponent` | 被 factory 创建在每个单元格 | ✅ 有数据 |
| `SurfaceLightComponent` | **未被任何 factory/初始化代码创建** | ❌ 无数据 |
| `SolarPositionComponent` | **未被创建** | ❌ 无数据 |
| `SolarRadiationComponent` | **未被创建** | ❌ 无数据 |
| `LightScatterComponent` | **未被创建** | ❌ 无数据 |
| `LightReceiverComponent` | **未被创建** | ❌ 无数据 |

**消费者检查：**

```
human/ → 从不读 LightFieldComponent 或 par
biology/ → 从不读 LightFieldComponent
civilization/ → 从不读 LightFieldComponent
observation/ → 只读 EnvironmentComponent.par（已由 sync 系统维护）
```

**结论：** `LightFieldComponent` 存在数据但无人消费。其余子组件连数据都没有。注册它们的系统只是在空转。

### 2. Terrain 模块 ❌

| 组件 | 状态 | 证据 |
|------|------|------|
| `TerrainComponent` | 被 factory 创建在每个单元格 | ✅ 有数据 |

**消费者检查：** 0 个外部系统读取 TerrainComponent。
- `TerrainSystem`/`TerrainTypeSystem` 读写但它本身就是地形系统（注册也没外部消费者）
- `LightFieldSystem` 读它 → 但 LightFieldSystem 本身不运行

**结论：** 地形数据无人问津，注册无意义。

### 3. Atmosphere 模块 ❌

| 组件 | 状态 | 证据 |
|------|------|------|
| `AtmosphereComponent` | **未被 factory 创建** | ❌ 无数据 |

**消费者检查：** 0 个外部系统读取 AtmosphereComponent。

**结论：** 数据都不存在，注册啥？

---

## ✅ 真正需要关注的核心链路（已就绪）

```
PhysicalWeatherSystem
  → PhysicsWeatherComponent (温度、压强、湿度、云量、降水、风速)
    → EnvironmentSyncSystem
      → EnvironmentComponent (per-cell & world)
        → physiology_needs_system.py
           读取: env.water_stress_index → 口渴
           读取: env.air_temperature → 疲劳 (超过25°C)
        → growth_system.py
           读取: world.get_environment() (站级环境)
        → soil_system.py
           读取: env.air_temperature → 土壤温度
```

**这三个消费者就是全模拟中**环境数据的出口**。当前链路已完全覆盖。**

---

## 📊 总结表

| 子模块 | 有数据 | 有消费者 | 应注册？ | 理由 |
|--------|--------|---------|---------|------|
| Season | ✅ | ✅ | ✅ | 已注册 |
| Climate | ✅(刚接通) | ✅(刚接通) | ✅ | 已注册 |
| Weather | ✅ | ✅ | ✅ | 已注册 |
| EnvironmentSync | ✅ | ✅ | ✅ | 已注册 |
| Soil | ✅ | ✅ | ✅ | 已修复 |
| **LightField** | ❌(部分) | ❌ | **否** | 组件未创建，无人消费 |
| **Terrain** | ✅ | ❌ | **否** | 数据闲置，无人消费 |
| **Atmosphere** | ❌ | ❌ | **否** | 组件未创建，无人消费 |
| **DayNightSystem** | ❌ | ❌ | **否** | 逻辑已被注释 |

---

## 🔮 未来集成时机

当以下场景出现时，才需要注册对应的模块：

| 模块 | 触发条件 |
|------|---------|
| **LightField** | 植物需要**逐格光照分布**（遮阴/向阳差异），或实体需要**阴影检测** |
| **Terrain** | 地形影响**移动速度**、**水径流**、**局部气候** |
| **Atmosphere** | 需要**微观大气变量**（气溶胶、空气密度）影响**视觉能见度**或**呼吸模型** |
| **DayNightSystem** | 需要除 TimeSystem 之外的**额外昼夜驱动逻辑** |

目前这些场景在 codebase 中均不存在对应的系统代码。

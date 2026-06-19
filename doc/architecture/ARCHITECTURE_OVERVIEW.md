# ECS 世界模拟系统 — 全架构总览

**版本：** v3.6
**统计：** 146 个 Component，173 个 System，~57,000 行代码
**测试：** 497/497 ✅

---

## 一、模块优先级矩阵

### P0 — 核心基础设施（必须运行）

| 模块 | 组件数 | 系统数 | 说明 |
|------|--------|--------|------|
| **core** | 4 | 8 | World, Entity, Component, System, EntityPool |
| **space** | 2 | 4 | 位置、碰撞、移动 |
| **time** | 1 | 2 | 时间推进、tick调度 |

### P1 — 基础环境（生态模拟基础）

| 模块 | 组件数 | 系统数 | 说明 |
|------|--------|--------|------|
| **environment** | 8 | 12 | 温度、湿度、光照、天气 |
| **atmosphere** | 1 | 7 | 气压、风、云、化学成分 |
| **light_field** | 6 | 5 | PAR、辐射、光谱、UV |
| **soil** | 5 | 5 | 湿度、肥力、温度、质量 |
| **terrain** | 4 | 2 | 海拔、坡度、植被覆盖 |
| **hydrology** | 2 | 1 | 水体、地下水、水循环 |
| **geology** | 1 | 1 | 地层、侵蚀 |
| **climate** | 2 | 1 | 气候、气候振荡 |
| **season** | 1 | 2 | 季节变化 |

### P2 — 生物系统（生命模拟）

| 模块 | 组件数 | 系统数 | 说明 |
|------|--------|--------|------|
| **biology** | 12 | 15 | 基因组、免疫、营养、生命周期 |
| **plant** | 5 | 6 | 生长、光合作用、根系、物候 |
| **animal** | 8 | 12 | 感知、需求、社交、学习、迁徙 |
| **human** | 15 | 25 | 认知、情感、社会、文明 |
| **phenology** | 1 | 1 | 物候期（积温驱动） |

### P3 — 高级系统（可选增强）

| 模块 | 组件数 | 系统数 | 说明 |
|------|--------|--------|------|
| **ocean** | 2 | 1 | 洋流、潮汐 |
| **astronomy** | 1 | 1 | 天体、引力潮汐 |
| **pollution** | 1 | 1 | 污染扩散 |
| **extreme_weather** | 1 | 1 | 风暴（气压驱动） |
| **civilization** | 8 | 10 | 建筑、农业、技术 |
| **memory_layer** | 6 | 5 | 统一记忆层 |
| **save_load** | 0 | 3 | 存档、序列化、迁移 |

---

## 二、系统依赖图

```
P0 核心层
├── World (tick调度)
├── Entity (创建/销毁)
├── Space (位置更新)
└── Time (时间推进)
    ↓
P1 环境层
├── Atmosphere (气压/风/化学成分)
│   └── 依赖: Temperature, Humidity
├── LightField (PAR/UV/辐射)
│   └── 依赖: Atmosphere, SolarPosition
├── Soil (湿度/肥力)
│   └── 依赖: Hydrology, Climate
├── Hydrology (水循环)
│   └── 依赖: Soil, Environment
├── Geology (侵蚀)
│   └── 依赖: Terrain, Hydrology
├── Terrain (海拔/坡度)
│   └── 依赖: Geology
├── Climate (温度/降雨)
│   └── 依赖: Atmosphere, Season
└── Season (季节)
    └── 依赖: Astronomy
    ↓
P2 生物层
├── Biology (基因组/免疫)
├── Plant (生长/光合作用)
│   └── 依赖: LightField, Soil, Phenology
├── Animal (感知/行为)
│   └── 依赖: Biology, Environment
├── Phenology (物候)
│   └── 依赖: Environment, Season
├── Human (认知/社会)
│   └── 依赖: Animal, Civilization
└── Migration (迁徙)
    └── 依赖: Animal, Season, Environment
    ↓
P3 高级层
├── Ocean (洋流)
│   └── 依赖: Atmosphere, Astronomy
├── Astronomy (潮汐)
│   └── 依赖: Ocean
├── Pollution (扩散)
│   └── 依赖: Atmosphere
├── ExtremeWeather (风暴)
│   └── 依赖: Atmosphere, Ocean
├── Civilization (建筑/农业)
│   └── 依赖: Human, Plant
└── MemoryLayer (记忆)
    └── 依赖: Human, Animal
```

---

## 三、系统 tick_interval 分布

| 间隔 | 系统数 | 代表系统 |
|------|--------|----------|
| 1（每帧） | ~15 | Movement, Circadian, Collision, Death |
| 2-5 | ~25 | Migration, Smell, WaterCycle, Farm |
| 10-20 | ~80 | Growth, Reproduction, Social, Weather |
| 50-100 | ~30 | Population, Ecology, Speciation |
| 未设置 | ~23 | 基础系统 |

---

## 四、组件兼容性矩阵

| 组件 | 新增于 | 序列化 | 迁移 | 注册到存档 |
|------|--------|--------|------|------------|
| WaterBodyComponent | v3.5 | ✅ | 自动 | 动态解析 |
| GroundwaterComponent | v3.5 | ✅ | 自动 | 动态解析 |
| StrataComponent | v3.5 | ✅ | 自动 | 动态解析 |
| PollutionComponent | v3.5 | ✅ | 自动 | 动态解析 |
| OceanCurrentComponent | v3.5 | ✅ | 自动 | 动态解析 |
| TideComponent | v3.5 | ✅ | 自动 | 动态解析 |
| CelestialBodyComponent | v3.5 | ✅ | 自动 | 动态解析 |
| StormComponent | v3.5 | ✅ | 自动 | 动态解析 |
| PhenologyComponent | v3.6 | ✅ | 自动 | 动态解析 |
| MigrationComponent | v3.6 | ✅ | 自动 | 动态解析 |

**所有新组件支持动态类型解析，旧存档自动兼容。**

---

## 五、性能热点分析

| 模块 | 每帧执行 | 计算复杂度 | 优化建议 |
|------|----------|------------|----------|
| Space/Collision | ✅ | O(n²) | 空间分区 |
| LightField | ✅ | O(n) | 批量计算 |
| Atmosphere | ✅ | O(n) | 缓存 |
| WaterCycle | 每5帧 | O(n²) | 距离优化 |
| PollutionDiffusion | 每5帧 | O(n²) | 空间索引 |
| OceanCurrent | 每10帧 | O(n²) | 空间索引 |
| TidalSystem | 每10帧 | O(n²) | 空间索引 |
| StormSystem | 每5帧 | O(n²) | 空间索引 |
| PhenologySystem | 每10帧 | O(n) | 无 |
| MigrationSystem | 每2帧 | O(n) | 无 |

---

## 六、缺失的关键连接

| 连接 | 状态 | 说明 |
|------|------|------|
| Hydrology ↔ Plant | ❌ | 植物根系未从地下水吸水 |
| Ocean ↔ Climate | ❌ | 洋流未影响气候系统 |
| Astronomy ↔ Season | ❌ | 天文参数未驱动季节 |
| Pollution ↔ Biology | ❌ | 污染未影响生物健康 |
| UV ↔ Biology | ❌ | UV未影响生物DNA/维生素D |
| Phenology ↔ Plant | ⚠️ | 已部分实现（growth_rate） |
| Migration ↔ Animal | ⚠️ | 需要集成到Animal行为 |

---

## 七、推荐启用顺序

### 阶段1：环境闭环（P1完整）
1. ✅ WaterCycleSystem — 水循环基础
2. ✅ ErosionSystem — 地形演化
3. ✅ PollutionDiffusionSystem — 污染扩散
4. ✅ OceanCurrentSystem — 洋流温度
5. ✅ TidalSystem — 天文潮汐
6. ✅ StormSystem — 极端天气

### 阶段2：生物增强（P2增强）
7. ✅ PhenologySystem — 植物物候
8. ✅ MigrationSystem — 动物迁徙
9. ⬜ UVSystem → Biology — UV影响生物
10. ⬜ Pollution → Biology — 污染影响健康

### 阶段3：系统联动（P3集成）
11. ⬜ Ocean → Climate — 洋流影响气候
12. ⬜ Astronomy → Season — 天文驱动季节
13. ⬜ Hydrology → Plant — 根系吸水

---

## 八、风险区域

| 区域 | 风险 | 缓解措施 |
|------|------|----------|
| 系统数量（173） | 性能下降 | tick_interval 分层 |
| 组件数量（146） | 内存占用 | EntityPool + 延迟加载 |
| 循环依赖 | 导入失败 | 延迟导入 + 接口抽象 |
| 存档兼容性 | 数据丢失 | ComponentMigrator |
| 未注册系统 | 功能未启用 | 手动注册到SimulationLoop |

---

*报告生成时间：2026-06-10*
*ECS 世界模拟系统版本：v3.6*

# ECS 世界模拟系统 — 模块架构图

**版本：** v3.9  
**日期：** 2026-06-11  
**统计：** 149 Component / 181 System / 598 文件 / 542 测试

---

## 一、总体架构（分层视图）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           应用层 (Application)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │SimulationLoop│  │EcosystemLoop │  │FullSimulation│  │WorldServer   │   │
│  │  主模拟循环   │  │  生态循环    │  │  全盘模拟    │  │ WebSocket    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           核心层 (Core)                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  World   │  │  Entity  │  │Component │  │  System  │  │EventBus  │     │
│  │ 世界容器  │  │ 实体     │  │ 组件     │  │ 系统     │  │ 事件总线  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │EntityPool│  │Generation│  │Dataclass │  │Tick调度  │  │SpatialIdx│   │
│  │ 实体池   │  │ 世代管理  │  │ 数据类   │  │ tick_interval│  │ 空间索引 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │QueryAPI  │  │PerfMon   │  │WorldConfig│  │Serializer│  │Migrator  │   │
│  │ 查询API  │  │ 性能监控  │  │ 世界配置  │  │ 序列化   │  │ 迁移器   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           基础设施层 (Infrastructure)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Space   │  │  Time    │  │Save/Load │  │Pathfinding│  │Collision │     │
│  │ 空间系统  │  │ 时间系统  │  │ 存档系统  │  │ 路径规划  │  │ 碰撞检测  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │SpaceComp │  │TimeComp  │  │Serializer│  │  A*算法  │  │Collider  │   │
│  │SpaceSys  │  │Scheduler │  │Migrator  │  │ 视线检测  │  │Obstacle  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           环境层 (Environment)                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Atmosphere│  │LightField│  │  Soil    │  │  Water   │  │  Terrain │     │
│  │ 大气系统  │  │ 光场系统  │  │ 土壤系统  │  │ 水文系统  │  │ 地形系统  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Weather   │  │SolarRad  │  │Moisture  │  │WaterCycle│  │Erosion   │   │
│  │PhysicsWx │  │UV/PAR    │  │Fertility │  │Groundwater│  │Sediment  │   │
│  │Chem/Storm│  │Phenology │  │RootZone  │  │Hydrology │  │Geology   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Climate  │  │  Season  │  │  Ocean   │  │ Pollution│  │ExtremeWx │     │
│  │ 气候系统  │  │ 季节系统  │  │ 海洋系统  │  │ 污染系统  │  │ 极端天气  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │OU Process│  │Astronomy │  │Current   │  │Diffusion │  │Storm     │   │
│  │Continuum │  │Tidal     │  │Tide      │  │Chemistry │  │Physical  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           生物层 (Biology)                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Plant   │  │  Animal  │  │  Human   │  │Lifecycle │  │  Ecology │     │
│  │ 植物系统  │  │ 动物系统  │  │ 人类系统  │  │ 生命周期  │  │ 生态系统  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Photosynth│  │Perception│  │Cognitive │  │Birth/Death│  │FoodChain │   │
│  │Root/Water│  │Memory    │  │Emotion   │  │Growth    │  │Population│   │
│  │Phenology │  │Social    │  │Decision  │  │Reproduce │  │Speciation│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │Physiology│  │Immune    │  │Genome    │  │Circadian │  │Smell     │     │
│  │ 生理系统  │  │ 免疫系统  │  │ 基因组   │  │ 昼夜节律  │  │ 气味扩散  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           文明层 (Civilization)                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Building │  │ Crafting │  │  Farm    │  │  Economy │  │  Culture │     │
│  │ 建筑系统  │  │ 制作系统  │  │ 农业系统  │  │ 经济系统  │  │ 文化系统  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Inventory │  │Knowledge │  │Irrigation│  │Trade     │  │TechPool  │   │
│  │Workshop  │  │Recipe    │  │Harvest   │  │Resource  │  │Evolution │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           元层 (Meta)                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │MemoryLayer│  │Identity  │  │Reputation│  │  Rules   │  │Presentation│   │
│  │ 记忆层    │  │ 身份系统  │  │ 声望系统  │  │ 规则系统  │  │ 可视化   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │            │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Concept   │  │Name/Age  │  │Fame      │  │Transform │  │Dashboard │   │
│  │MemoryInst│  │Shift     │  │Role      │  │Condition │  │WebSocket │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、模块统计

| 层级 | 模块 | 组件 | 系统 | 文件 | 说明 |
|------|------|------|------|------|------|
| **核心** | core | 1 | 1 | 23 | World, Entity, Component, System, EventBus, EntityPool, SpatialIndex, QueryAPI, PerformanceMonitor |
| **基础设施** | space | 3 | 2 | 8 | 位置、碰撞、路径规划 |
| | time_module | 1 | 1 | 4 | 时间推进、调度器 |
| | save_load | 1 | 2 | 8 | 序列化、迁移、增量存档 |
| **环境** | environment | 35 | 48 | 134 | 大气、光场、土壤、水文、地形、气候、季节、海洋、污染、极端天气、物候、天文、连续统 |
| **生物** | biology | 28 | 43 | 84 | 基因组、免疫、营养、生命周期、昼夜节律、气味、健康状态 |
| | plant | 4 | 5 | 13 | 光合作用、根系、生长、物候 |
| | animal | 9 | 11 | 25 | 感知、记忆、社交、学习、迁徙 |
| | human | 31 | 62 | 136 | 认知、情感、决策、社会、文明 |
| **文明** | civilization | 7 | 10 | 14 | 建筑、制作、农业、经济、文化 |
| **元层** | memory_layer | 0 | 1 | 16 | 统一记忆层 |
| | identity | 4 | 1 | 9 | 身份、分类、事件日志 |
| | physiology | 8 | 6 | 15 | 生理需求、健康 |
| | resource | 7 | 5 | 23 | 食物、水、材料 |
| | equipment | 1 | 0 | 5 | 装备 |
| | garbage | 1 | 1 | 5 | 垃圾清理 |
| | decomposer | 1 | 1 | 5 | 分解者 |
| | death_archive | 1 | 1 | 4 | 死亡档案 |
| | rules | 0 | 1 | 5 | 变换规则 |
| | presentation | 1 | 1 | 11 | 可视化、仪表盘 |
| **应用** | application | 0 | 2 | 4 | 模拟循环、生态循环、并行执行 |

---

## 三、系统依赖图

```
TimeSystem ──┬──► SpaceSystem ──┬──► CollisionSystem
             │                  │
             ├──► EnvironmentPipeline ──┬──► AtmospherePhysics
             │                          ├──► WeatherEffects
             │                          ├──► SeasonChange
             │                          ├──► ClimateSystem
             │                          ├──► WaterCycle
             │                          ├──► OceanCurrent
             │                          ├──► PollutionDiffusion
             │                          ├──► StormSystem
             │                          └──► TidalSystem
             │
             ├──► PlantSystems ──┬──► Photosynthesis
             │                   ├──► WaterUptake
             │                   ├──► RootSystem
             │                   └──► Phenology
             │
             ├──► AnimalSystems ──┬──► Perception
             │                    ├──► Memory
             │                    ├──► Social
             │                    ├──► Learning
             │                    ├──► Needs
             │                    ├──► Migration
             │                    └──► Reproduction
             │
             ├──► HumanSystems ──┬──► Cognitive
             │                   ├──► Decision
             │                   ├──► Emotion
             │                   ├──► Action
             │                   ├──► Social
             │                   ├──► Economy
             │                   └──► Crafting
             │
             ├──► BiologySystems ──┬──► Genome
             │                     ├──► Immune
             │                     ├──► Circadian
             │                     ├──► Growth
             │                     ├──► Death
             │                     └──► SmellDiffusion
             │
             ├──► CivilizationSystems ──┬──► Building
             │                          ├──► Farming
             │                          ├──► Technology
             │                          └──► Trade
             │
             ├──► EcologySystems ──┬──► FoodChain
             │                     ├──► Population
             │                     ├──► Speciation
             │                     └──► Balance
             │
             └──► MetaSystems ──┬──► MemoryLayer
                                ├──► EventLog
                                ├──► SaveLoad
                                └──► Visualization
```

---

## 四、数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                        输入层 (Input)                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ 初始配置 │  │ 实体工厂 │  │ 环境预设 │  │ 用户指令 │           │
│  │ Config  │  │ Factory │  │ Preset  │  │ Command │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
└───────┼────────────┼────────────┼────────────┼─────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        处理层 (Process)                          │
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│   │  World Tick │───►│ System Update│───►│ Event Dispatch│     │
│   │  (每帧执行)  │    │ (按优先级)   │    │ (事件分发)   │      │
│   └─────────────┘    └─────────────┘    └─────────────┘      │
│          │                  │                  │               │
│          ▼                  ▼                  ▼               │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│   │ Component   │◄──►│  System     │◄──►│  Entity     │      │
│   │ 数据更新    │    │ 状态计算    │    │ 生命周期    │      │
│   └─────────────┘    └─────────────┘    └─────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        输出层 (Output)                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ 世界状态 │  │ 事件日志 │  │ 存档数据 │  │ 可视化  │           │
│  │ State   │  │ EventLog│  │ SaveData│  │ Visual  │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、关键设计模式

### 1. ECS 核心模式
```
Entity = ID + Generation
Component = 纯数据 (Dataclass)
System = 业务逻辑 (update(world, dt))
World = 组件字典 + 系统列表 + 实体集合
```

### 2. 事件驱动模式
```
Publisher ──► EventBus ──► [Subscriber1, Subscriber2, ...]
   │                            │
   │                            ▼
   │                      MemoryLayer
   │                      EventLog
   │                      SystemTrigger
   │
   └── EntityCreated / EntityDestroyed / ComponentChanged
```

### 3. 数据驱动模式
```
System 不直接调用 System
    │
    ├── 读取 Component A
    ├── 计算逻辑
    └── 写入 Component B

下一个 System 读取 Component B
    │
    └── 继续处理
```

### 4. 分层 tick 模式
```
tick_interval = 1:  Movement, Collision, Circadian, DeathTrigger, Action, Perception
tick_interval = 2:  SmellDiffusion, Migration, UV, Emotion, Phenology
tick_interval = 5:  WaterCycle, Farm, Decision, Thought, CombatAI, Crafting
tick_interval = 10: Weather, Pollution, Storm, DiseaseSpread, RootSystem
tick_interval = 20: Disaster, SeedDispersal, Growth, Reproduction, PhysicalWeather
tick_interval = 50: Population, Ecology, Tidal, OceanCurrent
tick_interval = 100: Speciation, Balance, Astronomy
```

---

## 六、模块耦合度分析

### 高耦合区域（需关注）

| 区域 | 耦合模块 | 风险 |
|------|----------|------|
| Human ↔ Civilization | 人类系统直接操作建筑/农业/经济 | 中 |
| Animal ↔ Environment | 动物感知依赖环境组件 | 低 |
| Plant ↔ Soil/Water | 植物生长依赖土壤/水文 | 低 |
| Climate ↔ Ocean/Astronomy | 气候受洋流/天文影响 | 低 |

### 低耦合设计（良好）

| 设计 | 说明 |
|------|------|
| EventBus 解耦 | System 间通过事件通信，不直接调用 |
| Component 纯数据 | 无业务逻辑，无方法依赖 |
| World 中心化 | 所有数据通过 World 访问，接口统一 |
| tick_interval 分层 | 不同频率更新，减少相互影响 |

---

## 七、扩展点

### 已预留扩展

| 扩展点 | 位置 | 说明 |
|--------|------|------|
| 新 Component | `*/components/` | 继承 Component，自动序列化 |
| 新 System | `*/systems/` | 继承 System，注册到 SimulationLoop |
| 新处理器 | `*/processors.py` | 独立物理/业务逻辑单元，便于测试和替换 |
| 新环境类型 | `environment/` | 新增子模块，自动集成 |
| 新生物类型 | `biology/` / `animal/` / `plant/` | 新增组件+系统 |
| 新文明系统 | `civilization/` | 新增组件+系统 |
| 新可视化 | `presentation/` | 新增面板/图表 |

### 插件化设计

```
Plugin Interface:
  - on_init(world): 初始化
  - on_tick(world, dt): 每帧更新
  - on_event(event): 事件响应
  - on_save(): 序列化
  - on_load(data): 反序列化
```

---

*架构图生成时间：2026-06-11*  
*ECS 世界模拟系统版本：v3.9*

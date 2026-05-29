# ECS 世界模拟系统 — 项目架构

> 项目路径: `D:\个人助手\workspace\ECS`
> 核心架构: Entity-Component-System
> 模拟粒度: 1 步 = 1 小时，300 步 ≈ 12.5 天

---

## 一、核心层 (Core Layer)

```
core/
├── entity.py        # Entity: id(自增) + generation(防悬挂引用)
├── component.py     # Component: 数据基类(dataclass)
├── system.py        # System: 逻辑基类(priority排序)
├── world.py         # World: Entity/Component 双向索引, get_components 多组件查询
├── category.py      # 分类枚举
└── subcategory.py   # 子分类枚举
```

**关键接口：**
- `world.create_entity()` → 返回 Entity
- `world.add_component(entity, comp)` → 自动注册 SpaceComponent 到 SpaceSystem
- `world.get_components(CompType1, CompType2, ...)` → 联合查询
- `world.get_system(SystemType)` → 获取已注册的系统实例
- `world.query_entity(eid)` → 按 ID 查询实体
- `world.get_environment()` → 获取 world_entity 上的 EnvironmentComponent
- `world._world_entity` → 世界级单例实体（存储全局组件）

---

## 二、模块架构

### 2.1 空间系统 (Space)

```
space/
├── space_component.py    # x, y, layer, dirty 标记
├── space_system.py       # 空间索引管理, query_radius() 范围查询
└── spatial_index.py      # 稀疏网格索引(字典套集合)
```

**工作流：**
```
add_component(entity, SpaceComponent)
    → World 自动调用 space_system.add_entity(entity.id, comp)

query_radius(x, y, r)
    → 返回 r 范围内所有 entity_id 的集合
```

### 2.2 时间系统 (Time)

```
time_module/
├── time_system.py          # 年/日/时推进，支持时间倍率
├── time_component.py       # 时间数据（day_of_year, hour, year, total_hours）
└── time_component_v2/v3.py # 历史版本
```

### 2.3 环境系统 (Environment)

**设计理念：** 底层只有连续物理量的自然演化，所有离散状态（晴/雨/季节/事件）都是物理量的实时视图，不存储、不驱动逻辑。

```
environment/
├── environment_component.py       # 全局环境数据（温度/湿度/光照/风速/降水）
├── environment_factory.py
├── config/
│   ├── environment_builder.py     # 构建环境管线（15 系统 DAG）
│   ├── environment_profile.py     # 环境配置对象
│   └── weather_builder.py
│
├── light_field/                   # 光照系统
│   ├── components/                # SolarPosition, SolarRadiation, LightScatter, SurfaceLight
│   └── system/                    # SolarPositionSystem, SolarRadiationSystem, LightFieldSystem, LightAtmosphereCouplingSystem
│
├── season/                        # 季节系统 — 纯天文版
│   ├── season_component.py        # 仅保存年份进度（无季节枚举）
│   ├── season_state.py            # 天文计算函数（太阳赤纬角、日地距离、辐射因子）
│   └── season_system.py           # 只推进年份进度
│
├── climate/                       # 气候系统 — OU 随机过程版
│   ├── climate_component.py       # 长期趋势（temp_trend, humidity_trend, rainfall_trend）
│   └── climate_system.py          # Ornstein-Uhlenbeck 过程驱动
│
├── physics_weather/               # 物理天气系统 — 核心
│   ├── components/
│   │   ├── physical_weather_component.py   # 6 个连续物理量（T, P, AH, RH, cloud, precip, wind）
│   │   └── weather_event_components.py     # PhysicalAnomalyComponent（通用异常，无预定义事件类型）
│   ├── systems/
│   │   ├── physical_weather_system.py      # 温度/气压/湿度/云量/降水/风速 物理演化
│   │   ├── weather_event_system.py         # 滑动窗口统计异常检测（无固定阈值）
│   │   └── weather_lifetime_system.py      # 异常超时清理（无生命周期状态机）
│   ├── utils/
│   │   └── weather_classifier.py           # 纯视图层：物理量→离散标签（不影响逻辑）
│   └── config/
│       ├── physics_constants.py            # 物理常数与辅助函数
│       └── weather_thresholds.py           # 分类器阈值（纯显示用）
│
├── soil/                          # 土壤系统
│   ├── components/                # SoilMoisture, SoilTemperature, SoilFertility, SoilQuality
│   └── systems/                   # SoilTemperatureSystem, SoilWaterBalanceSystem, SoilSystem
│
├── terrain/                       # 地形系统
│   ├── components/                # TerrainComponent, PlateComponent, SedimentComponent
│   └── config/                    # 地形分类器、生成器、类型定义
│
├── continuum/                     # 环境连续统 — 空间平滑
│   ├── environmental_continuum_system.py   # 热扩散/湿度扩散/重力水流/风驱平流/生态自恢复
│   └── continuum_config.py
│
├── atmosphere/                    # 大气系统（散射耦合）
│   ├── components/
│   └── system/
│
└── systems/
    └── environment_sync_system.py   # PhysicalWeatherComponent → EnvironmentComponent 同步
```

#### 环境管线数据流（5 层 DAG）

```
Layer 1: 外部强迫
    SolarPositionSystem     Time → 太阳位置 (elevation, azimuth, day_length)
    SolarRadiationSystem    太阳位置 → 大气顶辐射 (TOA)
    SeasonSystem            Time → 年份进度（无固定季节枚举）
    ClimateSystem           OU 过程 → 气候趋势 (temp/humidity/rainfall trend)

Layer 2: 大气物理
    PhysicalWeatherSystem   天文参数+气候趋势 → 连续天气物理量 (T, P, RH, cloud, precip, wind)
    LightAtmosphereCouplingSystem  云量+气溶胶 → 光学散射参数

Layer 3: 辐射
    LightFieldSystem        TOA辐射+散射 → 地表光照 (直射/散射)

Layer 4: 异常检测 + 地表层
    WeatherEventSystem      滑动窗口统计 → 物理异常检测（无预定义事件类型）
    WeatherLifetimeSystem   异常超时清理
    SoilTemperatureSystem   天气温度 → 土壤温度
    SoilWaterBalanceSystem  天气降水 → 土壤水分
    SoilSystem              环境温度 → 土壤养分/pH
    EnvironmentSyncSystem   天气+光照 → EnvironmentComponent 同步

Layer 5: 空间平滑
    EnvironmentalContinuumSystem  相邻单元格扩散/平流/水流/自恢复
```

#### 物理天气演化机制

| 物理量 | 演化机制 | 驱动因素 |
|--------|---------|---------|
| 温度 | 日循环(正弦波) + 天文季节因子(赤纬角×日地距离) + 云量阻尼 + 随机游走 | 太阳辐射、气候趋势 |
| 气压 | 年周期 + 中周期(~5天天气系统) + 随机噪声 | 内在振荡 |
| 绝对湿度 | 蒸发 - 降水消耗 + 平流回归 + 土壤蒸发回馈 | 风速、温度、土壤湿度 |
| 相对湿度 | 从绝对湿度和温度**实时计算**（Clausius-Clapeyron） | 温度、绝对湿度 |
| 云量 | RH滞后驱动 + 气压下降促进 + 日间太阳消散 | 相对湿度、气压梯度 |
| 降水 | 云量+RH超阈值触发，正比于超出量，消耗水汽自抑制 | 云量、湿度 |
| 风速 | 气压梯度驱动 + 季节基线 + 随机回归 | 气压异常 |

#### 异常检测机制（替代旧事件系统）

```
旧系统：预定义事件类型（台风/暴雪/热浪...）+ 固定阈值
新系统：滑动窗口统计 + 实时偏离检测

维护每个物理量的 720 样本滑动窗口（约30天）
    → 计算均值 μ 和标准差 σ
    → 当 |当前值 - μ| > 2.5σ 时创建异常记录
    → 当偏离回到 1.5σ 内时结束异常
    → 异常标签 = "{物理量}_{high/low}"（无预定义类型）
```

### 2.4 人类系统 (Human)

```
human/
├── components/
│   ├── basic/              # HumanComponent, AgeComponent(默认18岁), GenderComponent, BodyComponent, IdentityComponent
│   ├── physiological/      # PhysiologyNeedsComponent(饥/渴/能/疲/社交/舒适), HealthComponent
│   ├── cognitive/          # 
│   │   ├── intent_component.py     # 高层意图 (EAT/DRINK/SLEEP/EXPLORE/SOCIALIZE/PAIR...)
│   │   ├── task_component.py       # 中层任务 (FIND_FOOD/DRINK_WATER/SLEEP/...)
│   │   ├── goal_component.py       # 长期目标 (字符串描述, 按人生阶段生成)
│   │   ├── brain_component.py      # 思维状态 (current_thought, mental_state, behavior_mode, decision_confidence)
│   │   ├── memory_component.py     # 事件/地点/人物记忆 + 成功记录
│   │   ├── personality_component.py # 性格五维 (bravery, greed, kindness, curiosity, discipline)
│   │   └── emotion_component.py    # 情绪系统 v2.0
│   │       ├── 基础情绪: happiness, anger, fear, joy, sadness, disgust, surprise
│   │       └── 复合情绪: stress, calmness, trust, loneliness, excitement, hope, frustration
│   ├── action/             # ActionComponent(当前动作+队列+进度+目标)
│   ├── abilities/          # VelocityComponent(speed=1.5), VisionComponent(radius=12), SkillComponent, SearchComponent
│   ├── economic/           # InventoryComponent(背包, 20格), EconomyComponent
│   └── social/             # SocialComponent, RelationshipComponent, ReproductionComponent
│
├── systems/
│   ├── core/               # 行为流水线
│   │   ├── intent_system.py      # Need → Intent (紧急度评分, EAT>DRINK>SLEEP>SOCIALIZE>EXPLORE)
│   │   ├── planning_system.py    # Intent → ActionQueue
│   │   └── action_system.py      # 调度器: 出队/进度检查/切换
│   ├── cognitive/          # 认知层 (新增)
│   │   ├── preception_system.py  # 视野填充: SpaceSystem.query_radius → vision.entities
│   │   ├── emotion_system.py     # 情绪演化: 生理→情绪, 环境→情绪, 行为→情绪, 社交→情绪
│   │   ├── thought_system.py     # 思维生成: 根据情绪+需求+行为生成内心独白
│   │   ├── goal_system.py        # 目标管理: 按人生阶段(童年/青少年/成年/老年)生成长期目标
│   │   └── decision_system.py    # 多层决策: 生理+情绪+性格+记忆+目标 → 意图调整
│   ├── action/             # 执行层
│   │   ├── movement_system.py    # MOVE_TO: 欧几里得距离移动, 1.5单位/步, 同步 dirty 标记到空间索引
│   │   ├── search_system.py      # SEARCH: 视野内找资源; 饮水支持全局半径30搜索+远距离漫游(15格)
│   │   ├── pickup_system.py      # PICKUP: 拾取→背包→设置所有权→移除空间索引
│   │   ├── eat_system.py         # EAT: 从背包找食物, 消耗减饥饿
│   │   ├── drink_system.py       # DRINK: 背包优先, 地面水源匹配范围1格
│   │   ├── sleep_system.py       # SLEEP: 3h恢复能量/疲劳, 额外恢复口渴/饥饿
│   │   └── socialize_system.py   # SOCIALIZE: 社交质量(性格+情绪), 影响双方情绪, 记录记忆
│   ├── physiological/      # 生理层
│   │   ├── physiology_needs_system.py  # 每步更新: 饥饿+8/h, 口渴+12/h, 能量-7/h(耦合项)
│   │   │                          # 环境耦合：干热加剧口渴，极端温度消耗能量
│   │   │                          # 睡眠代谢倍率 0.2, 社交需求自然衰减 0.3/h
│   │   └── health_system.py            # 健康状态
│   └── social/             # 社交层
│       ├── social_system.py
│       ├── pairing_system.py       # social<60 且非紧急生存意图时触发配对, 互斥检查避免重复
│       └── reproduction_system.py  # 仅限女性怀孕, 概率 0.005×dt, 周期72h/冷却168h
│
├── entities/
│   └── human_entity.py     # 模板: create_components() 创建所有组件实例(含EmotionComponent)
│
└── human_factory.py        # 创建人类: 实体+组件+初始水壶+初始食物
```

### 2.5 资源系统 (Resource)

```
resource/
├── food/
│   ├── components/food_component.py   # FoodComponent(amount, food_type, spoilage)
│   ├── food_factory.py                # 创建食物实体
│   └── food_types.py
├── water/
│   ├── components/water_component.py  # WaterComponent(amount, max_amount, temperature, purity)
│   └── water_factory.py               # 创建水源实体
└── components/
    └── resource_component.py          # ResourceComponent(resource_type, amount)
```

### 2.6 生物学系统 (Biology) — 通用层

```
biology/
├── components/
│   ├── genome_component.py       # 基因组：16 维基因 + copy/mutate/crossover 方法
│   ├── life_cycle_component.py   # 生命周期阶段：SEED→SPROUT→VEGETATIVE→MATURE→SENESCENCE→DEAD
│   ├── energy_component.py       # 能量储量组件
│   ├── growth_component.py       # 生长进度组件（biomass, height, growth_rate）
│   ├── morphology_component.py   # 形态表现型组件（height, stem_thickness, canopy_radius）
│   └── phenotype_component.py    # 表现型组件
│
├── systems/
│   ├── life_cycle_system.py      # 生命周期推进：GDD + 年龄双维度
│   ├── growth_system.py          # 光合/呼吸/生长：读取 16 维基因响应环境
│   ├── morphology_system.py      # 形态生长：身高/茎粗/冠幅因子
│   ├── reproduction_system.py    # 繁殖系统：遗传+变异+空间分布
│   ├── senescence_system.py      # 衰老系统：光合效率退化、黄化枯萎
│   ├── mutation_system.py        # 基因变异系统：随机漂变
│   ├── death_system.py           # 死亡判定系统
│   └── gene_expression_system.py # 基因表达：基因→表现型映射
│
├── genetics/
│   └── gene.py                   # Gene 数据类（name, strength, mutation_rate）
│
└── traits/
    └── trait.py                  # 性状定义
```

#### 16 维基因体系

| 基因 | 维度 | 影响系统 | 说明 |
|------|------|---------|------|
| `max_photosynthesis_rate` | 光合 | GrowthSystem | 最大光合速率上限 |
| `light_use_efficiency` | 光合 | GrowthSystem | 光照利用效率斜率 |
| `shade_tolerance` | 光合 | GrowthSystem | 低光补偿点，降低光饱点 |
| `optimal_temp` | 温度 | GrowthSystem | 最适光合温度 |
| `cold_tolerance` | 温度 | GrowthSystem | 低温光合停止阈值 |
| `heat_tolerance` | 温度 | GrowthSystem | 高温光合停止阈值 |
| `water_use_efficiency` | 水分 | GrowthSystem | CO₂/H₂O 交换比 |
| `metabolism_rate` | 代谢 | GrowthSystem | 呼吸速率倍率 |
| `growth_partition` | 代谢 | MorphologySystem | 光合产物生长/维持分配比 |
| `leaf_bias` | 形态 | MorphologySystem | 叶生物量分配比例 |
| `root_bias` | 形态 | MorphologySystem | 根生物量分配比例 |
| `stem_bias` | 形态 | MorphologySystem | 茎生物量分配比例 |
| `max_height` | 形态 | MorphologySystem | 最大株高上限 |
| `stem_thickness_factor` | 形态 | MorphologySystem | 茎粗/株高比因子 |
| `seed_production` | 繁殖 | ReproductionSystem | 单次种子产量倍率 |
| `dispersal_radius` | 繁殖 | ReproductionSystem | 种子扩散网格半径 |

#### 生命周期推进机制

采用 **GDD（Growing Degree Days）+ 年龄双维度**推进：

```
每小时累积 GDD：
  effective_temp = max(0, air_temp - base_temp)  # base_temp = 5°C
  accumulated_gdd += effective_temp / 24          # 小时折算到天

阶段推进阈值：
  SEED → SPROUT:         accumulated_gdd ≥ 50 + 随机偏移
  SPROUT → VEGETATIVE:   accumulated_gdd ≥ 150 + 随机偏移
  VEGETATIVE → MATURE:   accumulated_gdd ≥ 400 + 随机偏移
  MATURE → SENESCENCE:   accumulated_gdd ≥ 800 + 随机偏移（或年龄兜底）
  SENESCENCE → DEAD:     年龄 ≥ 生存期 × 1.5 或 biomass ≤ 0
```

#### 繁殖与遗传变异模型

```
无性繁殖流程：
  亲本 GenomeComponent
      ↓ genome.copy()          # 深度复制 16 维基因数组
  子代 GenomeComponent
      ↓ 遍历每个基因
  以 mutation_rate 概率变异
      ↓ gene.strength *= random.uniform(0.8, 1.2)  # ±20%
  变异后的子代基因组
      ↓ PlantFactory.create_plant_from_genome()
  子代实体（继承亲本策略 + 随机变异）

有性繁殖（预留）：
  亲本A × 亲本B → genome.crossover(genomeB) → 子代
```

### 2.7 植物系统 (Plant)

```
plant/
├── plant_factory.py   # 植物实体工厂：9 种物种预设 + 基因继承创建
└── __init__.py        # 模块入口
```

#### 9 种物种预设

| 预设 | 基因特征 | 适用环境 |
|------|---------|----------|
| `basic` | 各项均衡（光合25, 适温25°C, 耐寒5°C, 耐热35°C） | 一般陆地 |
| `fast` | 高光合(35)，早熟(种子80)，短寿，高扩散 | 扰动环境 |
| `tree` | 低光合(18)，高大(15m)，晚熟(种子15)，长寿 | 稳定森林 |
| `cold_resistant` | 耐寒(-10°C)，适温15°C，高冷耐受(0.8) | 高寒地区 |
| `drought_resistant` | 高水效(0.9)，深根(root_bias 0.45) | 干旱区 |
| `succulent` | 极高水效(1.5)，高耐热(45°C)，极低代谢(0.03) | 沙漠 |
| `aquatic` | 喜水(水效0.15)，耐阴(0.8)，高代谢(0.15) | 水域 |
| `shade_tolerant` | 极高耐阴(1.5)，低光效(12)，低矮(1.5m) | 林下 |
| `pioneer` | 高光合(40)，阳性(耐阴0.15)，高扩散(12) | 裸地/灾后 |

### 2.7 动物系统 (Animal)

```
animal/
├── animal_factory.py   # 动物实体工厂：3 种物种预设
└── __init__.py         # 模块入口
```

#### 3 种物种预设

| 预设 | 特点 | 应用场景 |
|------|------|----------|
| `basic` | 基础型，各项均衡 | 通用动物模型 |
| `fast` | 高敏捷，高代谢，短寿命 | 小型掠食者/食草动物 |
| `tank` | 高防御，高耐力，慢速 | 大型动物/防御型 |

### 2.8 文明系统 (Civilization)

```
civilization/
├── systems/
│   ├── civilization_system.py         # 文明阶段检测
│   ├── construction_system.py         # 建筑
│   ├── resource_gathering_system.py   # 资源采集
│   ├── technology_system.py           # 技术树
│   └── trade_system.py                # 贸易
```

### 2.8 规则系统 (Rules)

```
rules/
├── transformation_system.py   # 条件变换(如食物腐败)
├── transformation_rule.py     # 规则引擎
├── rules_config.py            # 预设规则
└── main.py                    # 规则入口
```

---

## 三、执行流水线 (SimulationLoop)

`main.py` 中的系统执行顺序 (每步调用):

```
更新顺序 → 系统                                  → 作用
─────────────────────────────────────────────────────────────
 0. SpaceSystem.update()   同步 dirty 位置到空间索引
─────────────────────────────────────────────────────────────
 1. TimeSystem             推进时间: hour += delta, day_of_year 循环
─────────────────────────────────────────────────────────────
 2. 环境管线(15系统)        见上文环境管线 DAG
    - SolarPosition → SolarRadiation → Season → Climate
    - PhysicalWeather → LightAtmosphereCoupling → LightField
    - WeatherEventGen → WeatherLifetime
    - SoilTemperature → SoilWaterBalance → Soil → EnvironmentSync
    - Continuum
─────────────────────────────────────────────────────────────
 3. 人类流水线
    PreceptionSystem       视野: SpaceSystem.query_radius → vision.entities
    IntentSystem           需求→意图: 紧急度评分, 选最高
    PlanningSystem         意图→动作队列
    ActionSystem           调度: 出队下一个动作
    SearchSystem           执行 SEARCH: 视野内找 Food/WaterComponent
    MovementSystem         执行 MOVE_TO: 向 target_pos 移动
    EatSystem              执行 EAT: 背包找 FoodComponent → 消耗
    DrinkSystem            执行 DRINK: 背包→地面水源
    SleepSystem            执行 SLEEP: 3h 恢复 100 能量
    PickupSystem           执行 PICKUP: 拾取→背包→所有权→移出空间索引
    SocializeSystem        执行 SOCIALIZE
    SocialSystem           社交关系更新
    PairingSystem          配对
    ReproductionSystem     繁衍
    DecisionSystem         高层决策
─────────────────────────────────────────────────────────────
 4. 生理系统
    PhysiologyNeedsSystem  生理需求更新: 饥+8/h, 渴+12/h, 能-7/h(耦合项)
    HealthSystem           健康状态
─────────────────────────────────────────────────────────────
 5. 生物学系统
    LifeCycleSystem         生命周期推进：GDD + 年龄双维度
    GrowthSystem            光合/呼吸：读取 16 维基因响应环境
    MorphologySystem        形态生长：身高/茎粗/冠幅
    SenescenceSystem        衰老降解：光合效率退化、黄化枯萎
    ReproductionSystem      繁殖系统：遗传+变异+空间分布
    MutationSystem          基因变异：随机漂变
    GeneExpressionSystem    基因表达
    DeathSystem             死亡判定
─────────────────────────────────────────────────────────────
 6. 规则系统
    TransformationSystem   规则变换(腐败等)
─────────────────────────────────────────────────────────────
 7. 文明系统
    CivilizationSystem     文明阶段
─────────────────────────────────────────────────────────────
 8. 资源再生
    _regenerate_resources  # 食物<15时自动补充，水源缓慢恢复
```

---

## 四、人类行为流水线

```
PhysiologyNeedsSystem
    ↓ 更新饥/渴/能，环境耦合（干热/极端温度）
IntentSystem
    ↓ 计算紧急度: EAT(×1.0), DRINK(×1.15), SLEEP(×1.3), SOCIALIZE(×0.8)
PlanningSystem
    ↓ 转换为动作队列
ActionSystem (调度器)
    ↓ 循环出队执行
┌────────────────────────────────────────────┐
│ EAT:    SEARCH → MOVE_TO → PICKUP → EAT   │
│ DRINK:  SEARCH → MOVE_TO → DRINK          │
│ SLEEP:  MOVE_TO → SLEEP                   │
│ EXPLORE: MOVE_TO (随机目标)                │
└────────────────────────────────────────────┘
    ↓ 每个动作由对应 System 处理
MovementSystem / SearchSystem / PickupSystem / EatSystem / DrinkSystem / SleepSystem
    ↓ 动作完成或失败 → ActionSystem 标记 IDLE → 下一循环
```

---

## 五、组件依赖图

```
Entity
├── SpaceComponent          ← 被 SpaceSystem 索引
├── HumanComponent          ← 人类标识
├── PhysiologyNeedsComponent ← IntentSystem 读取
│   ├── hunger (0-100)
│   ├── thirst (0-100)
│   ├── energy (0-100)
│   ├── fatigue
│   └── social
├── IntentComponent         ← IntentSystem 写入, PlanningSystem 读取
├── TaskComponent           ← PlanningSystem 写入, action systems 读取
├── ActionComponent         ← ActionSystem 管理
│   ├── current_action (ActionType)
│   ├── action_queue (list)
│   ├── progress (0-1)
│   └── target_pos / target_entity
├── InventoryComponent      ← PickupSystem 写入, EatSystem/DrinkSystem 读取
│   └── items[] → 可包含 FoodComponent / WaterComponent 实体
├── VisionComponent         ← PreceptionSystem 写入, SearchSystem 读取
│   └── entities[] (视野内的实体)
├── SearchComponent         ← SearchSystem 使用
└── VelocityComponent       ← MovementSystem 使用

WorldEntity（世界级单例）
├── TimeComponent           ← TimeSystem 读写
├── EnvironmentComponent    ← EnvironmentSyncSystem 写入, 人类/生物系统读取
├── PhysicalWeatherComponent ← PhysicalWeatherSystem 读写
│   ├── temperature, pressure, absolute_humidity
│   ├── relative_humidity, cloud_cover
│   ├── precipitation_rate, wind_speed
│   └── _temp_noise, _pressure_phase, _wind_noise
├── SolarPositionComponent  ← SolarPositionSystem 写入
├── SolarRadiationComponent ← SolarRadiationSystem 写入
├── LightScatterComponent   ← LightAtmosphereCouplingSystem 写入
├── SurfaceLightComponent   ← LightFieldSystem 写入
├── SeasonComponent         ← SeasonSystem 读写（年份进度）
├── ClimateComponent        ← ClimateSystem 读写（OU 趋势）
├── SoilMoistureComponent   ← SoilWaterBalanceSystem 读写
├── SoilTemperatureComponent ← SoilTemperatureSystem 读写
└── AtmosphereComponent     ← LightAtmosphereCouplingSystem 读取
```

---

## 六、关键数据流

### 食物流
```
World.create_entity() → add_component(FoodComponent+SpaceComponent)
    → SearchSystem.vision 发现 → MovementSystem 移动到位置
    → PickupSystem 拾取 → InventoryComponent
    → EatSystem 从背包消耗 → hunger -= 减少值
```

### 水流
```
WaterFactory.create_water() → add_component(WaterComponent+SpaceComponent)
    → Inventory 水壶(初始) / 地面水源
    → DrinkSystem: 背包查找优先, 地面水源备选(曼哈顿距离≤1)
    → thirst -= 50
    → 水源聚落化分布(5-8个聚落中心), 水量 100-300
```

### 能量流
```
PhysiologyNeedsSystem 每步: energy -= (4 + hunger_coupling + thirst_coupling)
    → energy < 40 → IntentSystem 选中 SLEEP(权重1.3)
    → SleepSystem: 3h后 add_energy(30) + add_fatigue(-10) + add_thirst(-10) + add_hunger(-5)
    → 睡眠时代谢倍率 0.2(口渴/饥饿增长大幅降低)
    → 唤醒后 energy ≈ 60-80 → 继续活动 ~12-18h
```

### 环境数据流（物理驱动）
```
TimeSystem (day_of_year, hour)
    ↓
SolarPositionSystem → 太阳赤纬角 + 高度角
    ↓
SolarRadiationSystem → TOA辐射
    ↓
PhysicalWeatherSystem → 6个连续物理量（温度/气压/湿度/云量/降水/风速）
    │   季节温度由太阳赤纬角和日地距离实时计算
    │   气候偏移由 OU 随机过程驱动
    ↓
EnvironmentSyncSystem → EnvironmentComponent（供人类/生物系统读取）
    ↓
PhysiologyNeedsSystem → 干热加剧口渴，极端温度消耗能量
```

---

## 七、当前已验证的状态

| 指标 | 值 |
|------|-----|
| 模拟步数 | 300 步 (12.5 天) |
| 程序稳定性 | 300 步无异常，完整运行 |
| 环境管线 | 15 系统全部正常执行 |
| 人口存活率 | **10/10（全部存活）** |
| 实体总数 | ~290 |
| 地图大小 | 100 × 100 |
| 天气物理演化 | 温度/气压/湿度/云量/降水/风速 连续演化正常 |
| 季节系统 | 天文参数驱动，无固定枚举 |
| 气候系统 | OU 随机过程驱动，无 ENSO 硬编码 |
| 异常检测 | 滑动窗口统计检测，无预定义事件类型 |
| 环境同步 | PhysicalWeather → EnvironmentComponent 正确同步 |
| 环境连续统 | 10×10 网格实体已创建，Continuum 系统正常运行 |
| Atmosphere 子系统 | 5 个子系统（气压/热力学/云/风/对流）经协调器正确加载 |
| 模拟速度 | ~40 步/秒 |

### 生物学系统验证状态

| 验证项 | 状态 | 说明 |
|--------|------|------|
| 植物模块创建 | ✅ | 9 种物种预设全部可创建，含 LifeCycleComponent + SpaceComponent |
| 生命周期推进 | ✅ | GDD 累积推进阶段：SEED → SPROUT → VEGETATIVE → ... |
| 环境响应 | ✅ | 高温(40°C)、低温(5°C)、阴蔽(50PAR)、干旱等条件对各物种影响合理 |
| 衰老系统 | ✅ | 成熟后光合效率逐步下降，黄化枯萎 |
| 繁殖/遗传/变异 | ✅ | 子代继承亲本 16 维基因，变异 ±20%，多代积累多样性 |
| 基因表达 | ✅ | 基因→表现型映射正确 |
| 形态生长 | ✅ | 读取 max_height、stem_thickness_factor 等基因 |
| 动物模块创建 | ✅ | 3 种物种预设全部可创建 |

---

## 八、待修复/优化的模块

### 已修复（近期）
- ✅ **环境模块崩溃**：`WeatherEventDiagnosticComponent` frozen dataclass 继承错误
- ✅ **环境同步失效**：`EnvironmentSyncSystem` 不同步 `world_entity` 的环境数据
- ✅ **main.py 属性错误**：`WaterComponent.max_amount` 缺失
- ✅ **季节系统硬编码**：移除 `Season` 枚举和 `SEASON_EFFECT`，改为天文参数驱动
- ✅ **气候系统硬编码**：移除 ENSO 三相位，改为 OU 随机过程
- ✅ **极端事件硬编码**：移除 6 种预定义事件类型和固定阈值，改为统计异常检测
- ✅ **事件生命周期状态机**：移除 `EventPhase` 四阶段，异常存在由物理偏离决定
- ✅ **PhysicalWeatherSystem 季节耦合**：温度计算直接基于太阳赤纬角和日地距离

### 已修复（本次）
- ✅ **MovementSystem 空间索引同步**：添加 `space.dirty = True`，修复移动后 SpatialIndex 永不更新的致命 bug
- ✅ **SearchSystem 水源搜索**：移除饮水任务 3 格距离限制；增加全局半径 30 搜索；无目标时 15 格远距离漫游
- ✅ **DrinkSystem 地面水源**：匹配条件从严格坐标相等放宽为曼哈顿距离 ≤ 1
- ✅ **SleepSystem 效率**：睡眠代谢倍率 0.4 → 0.2；完成后额外恢复口渴/饥饿
- ✅ **年龄初始化 bug**：`HumanEntity.create_components` 默认年龄 0 → 18，修复 `is_reproductive_age()` 永远为 False
- ✅ **SearchSystem 配对搜索**：新增 `FIND_PARTNER → HumanComponent` 目标解析，修复配对动作直接失败
- ✅ **PairingSystem 条件**：`social < 50` 放宽为 `< 60`；允许 `EXPLORE/PAIR` 等意图时配对
- ✅ **PairingSystem 互斥检查**：添加 `paired_this_frame` 集合，避免多人在同一帧配对到同一伴侣
- ✅ **ReproductionSystem 性别检查**：添加 `gender == FEMALE` 限制；怀孕概率 0.001 → 0.005
- ✅ **ReproductionSystem 生育周期**：`pregnancy_duration` 6480h → 72h（3天）；`birth_cooldown` 8760h → 168h（7天）
- ✅ **ReproductionSystem 新生儿初始资源**：`give_birth` 改用 `HumanFactory.create_human`，确保新生儿拥有初始水/食物
- ✅ **PhysiologyNeedsSystem**：添加社交需求自然衰减 0.3/h
- ✅ **资源分布**：初始水源 40 → 80；聚落化分布；再生阈值 10 → 25；人类初始位置限制在中央 20-79
- ✅ **AtmosphereSystem API 修复**：`get_component_by_type` → `get_world_component`
- ✅ **weather_classifier.py 动态阈值**：新增 `classify_adaptive()` 和 `AdaptiveWeatherClassifier`，基于历史滑动窗口分位数（percentile）动态计算阈值；保留原有 `classify()` 纯函数作为向后兼容 fallback
- ✅ **认知系统 v2.0 重构**：
  - `EmotionComponent` 新增复合情绪（stress, calmness, trust, loneliness, excitement, hope, frustration）
  - `BrainComponent` 新增思维系统（current_thought, mental_state, behavior_mode, thought_history）
  - `MemoryComponent` 增强事件/地点/人物记忆，支持情感影响和成功记录
  - `HumanEntity` 添加 `EmotionComponent` 到默认组件列表
- ✅ **EmotionSystem v2.0**：重写为四层驱动（生理→环境→行为→社交），情绪自然衰减与复合情绪联动
- ✅ **ThoughtSystem 新增**：根据情绪+需求+行为生成内心独白，更新心理状态和行为模式
- ✅ **GoalSystem 整合**：接入人类系统流水线，目标根据人生阶段和性格动态生成
- ✅ **SocializeSystem v2.0**：社交质量由性格和情绪决定，互动后更新双方情绪、关系强度和记忆
- ✅ **DecisionSystem v2.0**：多层决策模型（生理+情绪+性格+记忆+目标），与 IntentSystem 协同工作
- ✅ **人类系统流水线重组**：感知→情绪→思维→目标→意图→决策→规划→执行→社交

### 仍存在问题 / 待优化
- **weather_classifier.py** 自适应分类器目前为模块级全局状态，如需支持多世界/多气候区，可扩展为 `AdaptiveWeatherClassifier` 实例化版本
- `weather_classifier.py` 固定阈值版本仍保留在代码中作为保底 fallback，不影响物理演化
- **DecisionSystem** 中的部分意图（WORK, BUILD, CRAFT, ATTACK, DEFEND, COLLECT, STORE）尚未配置对应的执行系统，当前仅影响意图选择权重
- **ThoughtSystem** 的思维生成目前为规则模板，后续可接入 LLM 生成更丰富的内心独白

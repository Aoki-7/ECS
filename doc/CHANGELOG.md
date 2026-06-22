# Changelog

## v4.1 (2026-06-18)

### ClimateSystem V2 重构

- **标准 OU 过程**：移除 `_temp_velocity` / `_humidity_velocity` / `_rainfall_velocity`，
  改为标准离散 Ornstein-Uhlenbeck 更新 `x += θ * (μ - x) * dt + noise`。
- **目标均值（Target Mean）**：新增 `_compute_target_temperature()` / `_compute_target_humidity()` / `_compute_target_rainfall()`，
  先计算目标均值，再执行均值回归。
- **洋流解耦**：暖流/寒流只影响温度目标均值，不再直接修改 `climate.temp_trend`，
  消除长期累积和硬限制触发问题。
- **气候变量耦合**：
  - 温度 → 湿度：`target_humidity += temp_trend * 0.05`
  - 湿度 → 降雨：`target_rainfall += humidity_trend * 0.4`
- **外部驱动扩展接口**：新增 `_get_external_temperature_forcing()`，
  为未来火山、太阳活动、冰期等系统预留接入点。
- **参数更新**：按 V2 建议调整 `THETA_*` 与 `SIGMA_*`。
- **天气系统修复**：`PhysicalWeatherSystem` 正确读取 `temp_trend` / `humidity_trend` / `rainfall_trend`。

## v4.0 (2026-06-12)

### 架构重构 — P0/P1/P2 问题解决

#### World 拆分（P0）
- 新增 `core/entity_manager.py` — Entity 生命周期管理
- 新增 `core/archetype_store.py` — Archetype-based 组件存储
- 新增 `core/system_scheduler.py` — System 依赖图 + 拓扑排序
- 重构 `core/world.py` — 从 ~500 行上帝对象变为 ~350 行协调者
- **向后兼容**：v3.9 API 完全保留，542 测试全部通过

#### Archetype 存储（P0）
- 列式存储：组件按类型连续内存存放
- 查询优化：直接遍历匹配 Archetype，无需集合交集
- 自动迁移：实体添加/移除组件时自动迁移 Archetype
- **性能提升**：内存局部性更好，查询效率提升

#### System 依赖图（P1）
- 声明式依赖：`dependencies_after` / `dependencies_before`
- 自动拓扑排序：Kahn 算法 + 优先级排序
- 循环依赖检测：运行时验证
- **向后兼容**：旧 `priority` 字段仍有效

#### Component 纯数据化（P1）
- `MemoryComponent` → `MemoryManagementSystem`（15 个方法迁移）
- `WorldConfigComponent` → `WorldConfigSystem`（2 个方法迁移）
- `ActionComponent` → `ActionManagementSystem`（1 个方法迁移）
- `CircadianComponent` 已纯数据（无需迁移）

#### 测试补充（P1）
- human 模块：+28 测试（MemoryManagementSystem 15 + ActionManagementSystem 8 + 其他）
- core 模块：+9 测试（WorldConfigSystem）
- plant 模块：+2 测试（PhotosynthesisSystem）
- **总计：576 测试全部通过**（新增 34）

#### 事件总线隔离（P2）
- 新增 `core/world_event_bus.py` — 每 World 独立事件总线
- 支持：订阅/发布/优先级/过滤/历史记录
- **向后兼容**：全局 EventBus 仍可用

#### 统一序列化（P2）
- 新增 `core/component_serializer.py` — 统一组件序列化框架
- `@register_component` 装饰器自动注册
- 版本迁移：支持 3.9 → 4.0 数据迁移
- 更新 `save_load/serializers/world_serializer.py` 使用新框架

---

## v3.9 (2026-06-11)

### System 文件拆分

#### PhysicalWeatherSystem 处理器拆分
- 新增 `environment/physics_weather/systems/weather_processors.py`
- 6 个独立处理器：
  - `TemperatureProcessor`：温度（日循环+季节+云量阻尼+噪声）
  - `PressureProcessor`：气压（年周期+中周期+噪声）
  - `HumidityProcessor`：湿度（蒸发+降水消耗+平流）
  - `CloudCoverProcessor`：云量（RH驱动+气压下降促进）
  - `PrecipitationProcessor`：降水（云量+湿度条件触发）
  - `WindSpeedProcessor`：风速（基线+气压梯度+噪声）
- `PhysicalWeatherSystem` 从 490 行简化为 ~120 行
- 适配 `SeasonComponent` 新 API（year_progress/year_length_hours）

### 性能监控系统
- 新增 `core/performance_monitor.py`
- 单例模式，全局监控所有 System 性能
- 装饰器 `@monitored_update`：自动包装 `System.update()`
- 统计指标：count/avg_ms/max_ms/min_ms/total_ms
- 慢系统检测：`get_slow_systems(threshold_ms)`
- 帧耗时摘要：`get_frame_summary()`
- 11 个测试全部通过

### 新增测试
- 性能监控：`core/tests/test_performance_monitor.py`（11 个测试）
- 总测试数：**542** 个（全部通过）

## v3.8 (2026-06-11)

### System 文件拆分

#### EnvironmentalContinuumSystem 处理器拆分
- 新增 `environment/continuum/continuum_processors.py`
- 5 个独立处理器：
  - `ThermalDiffusionProcessor`：热扩散（傅里叶热传导）
  - `HumidityDiffusionProcessor`：湿度扩散
  - `GravityWaterFlowProcessor`：重力水流
  - `WindAdvectionProcessor`：风驱平流
  - `SelfRecoveryProcessor`：生态自恢复
- `EnvironmentalContinuumSystem` 从 552 行简化为 ~100 行
- 6 个处理器测试全部通过

### Component 纯数据化

#### LifeCycleComponent
- 移除所有方法（is_seed / is_mature / is_dead / stage_name / set_stage 等）
- 新增 `biology/lifecycle/systems/life_cycle_system.py`
- 静态工具方法：`LifeCycleSystem.is_mature()` / `is_seed()` / `is_dead()` / `stage_name()`
- 适配 `animal_reproduction_system.py` / `seed_dispersal_system.py` / `plant/tests/test_plant.py`

### EntityPool 自动调优优化
- `auto_tune()` 添加调用计数器，每 100 次调用执行一次
- 避免每帧都调整池大小
- 调优后重置命中/未命中计数器
- 5 个测试全部通过

### 新增测试
- 连续统处理器：`environment/continuum/tests/test_continuum_processors.py`（6 个测试）
- EntityPool 自动调优：`core/tests/test_entity_pool_auto_tune.py`（5 个测试）
- 总测试数：**531** 个（全部通过）

## v3.7 (2026-06-11)

### 核心重构

#### Query API
- 新增 `core/query_api.py` — 声明式查询接口
- `world.query(ComponentA, ComponentB)` — 多组件查询
- `world.query_one(Component)` — 单组件快捷查询
- 查询缓存：同一 tick 内相同查询复用结果
- 11 个测试全部通过

#### SearchSystem 策略拆分
- 新增 `human/systems/action/search_strategies.py`
- 4 个独立策略类：VisualSearchStrategy / SmellSearchStrategy / MemorySearchStrategy / ExploreSearchStrategy
- SearchSystem 从 461 行简化为 ~200 行
- 策略注册表模式，便于扩展新搜索策略

#### DecisionSystem 策略拆分
- 新增 `human/systems/cognitive/decision_strategies.py`
- 8 个独立策略类：Physiology / Emotion / Personality / Memory / Goal / Social / Circadian / Emergency
- DecisionSystem 从 374 行简化为 ~150 行
- 策略模式便于单元测试和 A/B 测试

#### Component 纯数据化（示例）
- `HealthStatusComponent`：移除所有方法（add_wound / update_wounds / remove_healed_wounds / get_total_severity）
- 新增 `biology/systems/health_status_system.py` — 业务逻辑迁移到 System
- `UVBiologySystem` 适配新 API（使用 HealthStatusSystem.add_wound 静态方法）
- 8 个测试全部通过

### 新增测试
- Query API：`core/tests/test_query_api.py`（11 个测试）
- HealthStatusSystem：`biology/tests/test_health_status_system.py`（8 个测试）
- 总测试数：**520** 个（全部通过）

## v3.6 (2026-06-11)

### 系统联动修复
- **Hydrology ↔ Plant**：`RootSystem` 优先从 `GroundwaterComponent` 吸水，其次从 `SoilComponent`
- **Ocean ↔ Climate**：`ClimateSystem` 新增 `_apply_ocean_current_effects()`，暖流/寒流影响温度趋势
- **Astronomy ↔ Season**：`SeasonChangeSystem` 新增 `_calculate_astronomical_day()`，轨道偏心率影响季节推进
- **Pollution ↔ Biology**：新增 `PollutionHealthSystem`，PM2.5/臭氧/SO2/NO2 损伤健康
- **UV ↔ Biology**：新增 `UVBiologySystem`，UV-B 导致 DNA 损伤，UV-A 促进维生素 D 合成
- **Migration ↔ Animal**：`AnimalMigrationSystem` 集成 `MigrationComponent`，同步动物移动状态

### 新系统注册
- `SimulationLoop` 注册 11 个新系统：WaterCycle/Erosion/PollutionDiffusion/OceanCurrent/Tidal/Storm/Phenology/AtmosphericChemistry/UV/PollutionHealth/UVBiology

### 性能优化
- **SpatialIndex**：均匀网格空间索引，O(1) 插入/O(k) 范围查询
- 修复 `core/tests/test_performance.py` 适配新 API

### 代码巡检修复
- **集合迭代修改**：`disaster_system.py` `list(disasters)`、`garbage_cleanup_system.py` `list(garbage_entities[:excess])`
- **内存泄漏**：`EnvironmentObservationComponent` 添加 `max_history=1000`，超出自动裁剪
- **并发安全**：`ParallelSystemExecutor` 添加线程安全警告注释

### 新增测试
- 集成测试：`integration_tests/test_system_integration.py`（6 个测试全部通过）
- 空间索引测试：`core/tests/test_spatial_index.py`（4 个测试）
- 总测试数：**501** 个（全部通过）

## v3.5 (2026-06-10)

### 环境模块补全 — 6 大子系统

#### 水文系统（Hydrology）— P0
- **WaterBodyComponent**：河流/湖泊/湿地/池塘，水量/流速/水质
- **GroundwaterComponent**：含水层类型/地下水位/孔隙度/渗透系数
- **WaterCycleSystem**：降雨→土壤→渗透→径流→地下水→河流流动闭环
- **物理驱动**：蒸发量∝温度，径流∝土壤饱和度，河流流动∝流速

#### 地质系统（Geology）— P0
- **StrataComponent**：多层地层/基岩深度/断层线/矿床
- **ErosionSystem**：水蚀（河流冲刷）、风蚀（干旱地区）、沉积物搬运
- **物理驱动**：侵蚀速率∝流速/风速，沉积∝坡度差

#### 污染系统（Pollution）— P1
- **PollutionComponent**：空气/水/土壤三维度污染度 + 污染物浓度
- **PollutionDiffusionSystem**：空气随风扩散、水随流扩散、土壤缓慢渗透
- **物理驱动**：扩散速率∝风速/水流，自然降解∝时间

#### 海洋系统（Ocean）— P1
- **OceanCurrentComponent**：暖流/寒流、流速向量、盐度、深度层
- **TideComponent**：潮汐类型/潮差/高潮低潮水位
- **OceanCurrentSystem**：暖流加热空气、寒流冷却、盐度平衡
- **物理驱动**：温度影响∝距离，盐度扩散∝浓度差

#### 天文系统（Astronomy）— P2
- **CelestialBodyComponent**：质量/距离/轨道周期/偏心率/相位
- **TidalSystem**：天体引力计算潮汐力，轨道相位推进
- **纯物理公式**：F_tidal = M/d³，r = a(1-e²)/(1+e·cosθ)
- **无硬编码**：潮汐高度由引力和地形共同决定

#### 极端天气（ExtremeWeather）— P2
- **StormComponent**：气压梯度/温度梯度/湿度/科里奥利参数
- **StormSystem**：风暴生成（物理条件）→ 演化 → 影响环境 → 消散
- **纯物理驱动**：
  - 风速 = (1/ρf)·(ΔP/Δn) 地转风公式
  - 强度 = f(气压梯度, 温度梯度, 湿度)
  - 科里奥利力 = 2Ω·sin(φ)
- **无硬编码阈值**：风暴类型由温度/湿度自发决定

### 新增测试：38 个
- hydrology: 8 | geology: 4 | pollution: 4 | ocean: 6 | astronomy: 7 | extreme_weather: 9

## v3.4 (2026-06-10)

### 实体池监控
- **统计跟踪**：命中率、峰值池大小、获取/释放次数
- **自动调优**：根据命中率动态扩容/缩容
- **历史记录**：最近 100 次命中率平均值

### PlantComponent 迁移
- **组件迁移框架**：`ComponentMigrator`，注册表模式
- **自动迁移**：旧存档加载时自动升级 PlantComponent
- **向后兼容**：v1.0 → v2.0 自动添加 health/water/nutrients/energy

## v3.3 (2026-06-10)

### 新增系统
- **季节变化系统**：`SeasonChangeSystem`，四季影响温度/降雨/湿度/光照
- **多线程执行器**：`ParallelSystemExecutor`，并行执行无依赖 System

### 实体池默认启用
- `World.create_entity()` 优先从池获取
- `World.remove_entity()` 优先回收到池
- `SimulationLoop` 初始化时自动启用

### 植物 Component 补全
- 新增 `health`, `water`, `nutrients`, `energy` 字段
- `RootSystem` 现在可以真正修改植物状态

## v3.2 (2026-06-10)

### 新增系统
- **实体池系统**：`EntityPool` + `PooledEntity` 上下文管理器，减少 GC 压力
- **根系系统**：`RootComponent` + `RootSystem`，植物地下竞争水分/养分

### 环境模块优化
- **集中管理常量**：新增 `environment/config/environment_constants.py`，替代 210 处魔法值
- **连续统系统性能优化**：预计算组件缓存，减少 50% get_component 调用
- 新增 8 个环境常量测试

### 修复
- 修复 `memory_layer/tests/test_phase4.py` 性能测试除零错误

## v3.1 (2026-06-10)

### 系统集成
- **昼夜节律集成到决策系统**：夜间降低活动意图得分，白天增加，高睡眠债务强制睡眠
- **气味感知集成到搜索系统**：搜索策略新增嗅觉感知步骤（visual → smell → memory → explore）
- 新增 5 个集成测试（3 个昼夜节律 + 2 个气味感知）

## v3.0.3 (2026-06-10)

### 严重 BUG 修复
- 修复 4 处集合迭代修改（`list()` 复制后再删除）
- 修复 EventBus `_dispatch()` 迭代安全性（`list(subs)`）
- 修复内存泄漏风险（`stats_history` / `yield_history` 限制上限）

### 新增系统
- **昼夜节律系统**：`CircadianComponent` + `CircadianSystem`
  - 24小时节律相位管理
  - 睡眠债务累积/恢复
  - 强制睡眠/自然醒来
  - 支持昼行性/夜行性
  - 11 个测试全部通过
- **气味扩散系统**：`SmellComponent` + `SmellDiffusionSystem`
  - 气味源释放到网格
  - 4方向扩散 + 衰减
  - 动物嗅觉感知（5x5范围）
  - 7 个测试全部通过

## v3.0.2 (2026-06-09)

### 行为调度链路修复
- 修复 `SearchSystem` 找到目标后直接设置 `current_action = MOVE_TO` 的问题
- `SearchSystem` 现在只设置 `target_pos` 和 `target_entity`，让 `ActionSystem` 调度下一个动作
- `PlanningSystem._plan_eat()` 为附近植物设置 `target_entity`
- 新增端到端测试验证：饥饿 → 寻找食物 → 移动 → 进食 完整链路

### 系统 tick_interval 优化
- `DecisionSystem`: 1→5（决策不需要每帧）
- `ThoughtSystem`: 1→5（思维不需要每帧）
- `EmotionSystem`: 1→2（情绪变化较慢）
- `CombatAISystem`: 1→3（战斗AI不需要每帧）
- `DiseaseSpreadSystem`: 10→5（疾病传播适中频率）
- `CraftingSystem`: 1→2（制作行为不需要每帧）
- `DisasterSystem`: 10→20（灾害检查频率降低）
- 每帧执行系统数从 ~55 降至 ~45，测试运行时间从 1.52s 降至 1.30s

## v3.0.1 (2026-06-09)

### 通用路径规划服务
- 新增 `space/pathfinding.py` — A* 寻路、视线检测、路径平滑、流场生成
- 新增 `space/tests/test_pathfinding.py`（14 个测试）
- `animal/systems/animal_migration_system.py` — 迁移到通用路径规划服务

### 碰撞检测系统
- 新增 `space/collision_system.py` — ColliderComponent、ObstacleComponent、碰撞检测与自动分离
- 新增 `space/tests/test_collision_system.py`（11 个测试）
- `config/system_priorities.py` — 新增 COLLISION 优先级
- `application/simulation_loop.py` — 注册 CollisionSystem

### 建筑实体化
- 新增 `civilization/components/building_component.py` — BuildingComponent、BuildingInventoryComponent
- 新增 `civilization/building_factory.py` — 创建建筑实体（hut/workshop/storage/farm）
- 新增 `civilization/tests/test_building.py`（12 个测试）
- 建筑自动挂载 Collider + Obstacle，与碰撞系统集成

### 自然演化制作系统（无硬编码配方）
- 新增 `civilization/components/crafting_knowledge_component.py`
  - CraftingKnowledgeComponent：从实践中学习配方，无预设配方
  - CulturalTechPoolComponent：文明群体技术池，技术从个体汇聚
- 新增 `civilization/systems/crafting_system.py`
  - 产出从材料物理属性 emergent 决定（硬度/柔性/耐久/可加工性）
  - 成功/失败都产生学习数据
  - 技术熟练度递减增长
- 新增 `civilization/systems/technology_evolution_system.py`
  - 技术从个体实践中发现（非解锁）
  - 技术通过社会学习传播（观察、模仿、教导）
  - 技术可能失传或独立发明
  - 不同文明可能发展出完全不同的技术路线
- 新增 `civilization/tests/test_crafting_system.py`（11 个测试）

### 农业系统（自然演化版）
- 新增 `civilization/components/farm_component.py`
  - FarmPlotComponent：农田地块，生长从环境条件自然计算
  - FarmingKnowledgeComponent：农业知识从实践中积累
  - IrrigationComponent：灌溉系统
- 新增 `civilization/systems/farm_system.py`
  - FarmSystem：作物生长更新（温度/光照/水分影响）
  - HarvestSystem：收割行为，记录农业知识
  - IrrigationSystem：水源管理
- 新增 `civilization/tests/test_farm_system.py`（14 个测试）
- 作物产量从土壤质量、健康度、水分水平 emergent 计算
- 农业知识：最佳作物选择、灌溉水平、轮作效果

### 环境灾害系统（P1）
- 新增 `environment/systems/disaster_system.py`
  - 火灾：高温 + 干旱 + 风 → 火势蔓延
  - 洪水：暴雨 + 低洼 → 积水扩散
  - 干旱：长期无雨 + 高温 → 土壤干裂
  - 灾害从环境条件自然涌现，非随机事件
- 新增 `environment/tests/test_disaster_system.py`（8 个测试）

### 烹饪系统（P1）
- 新增 `human/systems/action/cooking_system.py`
  - 无硬编码食谱，食物效果从温度/时间计算
  - 生食/熟食/烧焦/过熟，从烹饪程度 emergent
  - 烹饪知识从实践中积累
- 新增 `human/tests/test_cooking_system.py`（6 个测试）

### 衣物系统（P1）
- 新增 `human/components/clothing_component.py`
  - ClothingComponent：单件衣物（保暖/耐久/湿度）
  - OutfitComponent：着装管理
- 新增 `human/systems/clothing_system.py`
  - 衣物磨损、湿度影响保暖、温度适应
- 新增 `human/tests/test_clothing_system.py`（7 个测试）

### 时间事件调度器（P1）
- 新增 `core/time_scheduler.py`
  - 基于最小堆的高效事件调度
  - 支持一次性、周期性、条件性事件
  - 事件取消和清理
- 新增 `core/tests/test_time_scheduler.py`（7 个测试）

### 增量存档系统（P1）
- 新增 `save_load/incremental_save_system.py`
  - 只保存与上次快照的差异
  - 自动压缩（zlib）
  - 支持增量读档（合并基础 + 增量）
  - 自动清理旧增量
- 新增 `save_load/tests/test_incremental_save.py`（7 个测试）

### 世界模拟实时可视化
- 新增 `presentation/visualization/world_server.py`
  - WebSocket 服务器：后端实时计算 ECS 世界
  - 每 tick 收集世界状态并推送到前端
  - 支持暂停/继续/调速控制
- 新增 `presentation/visualization/world_realtime_dashboard.html`
  - 实时可视化前端：WebSocket 连接后端
  - Canvas 世界地图：6 种实体类型实时更新
  - Chart.js 趋势图：生态 + 文明双面板
  - 环境指标：温度/湿度/降雨/风速实时显示
  - 知识积累进度条
  - 事件日志
  - 连接状态指示器 + 自动重连
- 新增 `presentation/visualization/README.md` — 实时可视化使用说明
- 新增 `presentation/visualization/world_simulation_dashboard.py`
  - WorldSnapshot：完整世界快照
  - WorldSimulationDashboard：数据收集 + HTML 导出
- 新增 `presentation/visualization/world_simulation_dashboard.html`
  - 静态可视化版本（无 WebSocket）
- 新增 `presentation/visualization/run_world_simulation.py`
  - 完整世界模拟运行器
- 新增 `presentation/tests/test_world_simulation_dashboard.py`（5 个测试）

### 文明演化仪表盘
- 新增 `presentation/visualization/civilization_dashboard.py`
  - 生成文明繁衍的实时监控仪表盘 HTML
- 新增 `presentation/visualization/civilization_dashboard.html`
  - 完整前端实现：Canvas 世界地图、Chart.js 趋势图
  - 暗色主题、响应式布局
- 新增 `presentation/tests/test_civilization_dashboard.py`（3 个测试）

### 测试
- 总测试数: **364** 个（全部通过）

---

## v3.0 (2026-06-08)

### 统一记忆层（Phase 1-4 完成）
- 新增 `memory_layer/` 目录（15 个文件，53 个测试）
- 核心类：Concept、MemoryInstance、MemoryLayer
- 认知框架：注意力/解释/威胁/重构滤镜
- 记忆扭曲引擎：信息损失/认知偏差/情感传染
- 持久化：存档/读档/自动保存

### 事件总线系统
- 新增 `core/event_bus.py`（12 个测试）
- 全局单例：订阅/发布/优先级/过滤

### 空间索引
- 新增 `core/spatial_index.py`（6 个测试）
- 均匀网格：O(1)~O(k) 查询

### 可视化工具
- 新增 `presentation/visualization/world_visualizer.py`（9 个测试）
- 5 种可视化：热力图/系统监控/关系网络/记忆网络/事件时间轴

### 统一存档
- 新增 `save_load/unified_save_system.py`（8 个测试）
- 整合 World 序列化 + MemoryLayer 持久化

---

## v2.3 (2026-06-07)

### Animal 模块全面重构
- 从 7 文件扩展到 27 文件
- 新增 5 个系统：Needs/Social/Memory/Territory/Migration
- 新增 Perception/Learning 系统

---

## v2.0 (2026-06-05)

### 初始架构
- core：Entity/Component/System/World
- application：SimulationLoop
- human：认知/行为/社交系统
- plant：生长/光合作用
- environment：天气/土壤

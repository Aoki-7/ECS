# ECS 世界模拟系统 — 迭代路线图

> 当前版本: v4.0
> 最后更新: 2026-06-12

---

## 已完成的里程碑

### ✅ v1.0 核心框架（2026-05）
- ECS 核心（Entity/Component/System/World）
- 空间系统、时间系统、环境系统

### ✅ v1.5 生物模块（2026-05）
- 生命周期系统、能量系统、疾病系统

### ✅ v2.0 Animal 重构 + 记忆层（2026-06-08）
- Animal 模块全面重构（7→27 文件，3→10 系统）
- 统一记忆层 Phase 1-4 完成

### ✅ v2.1 架构文档 + 清理（2026-06-08）
- `doc/architecture/ARCHITECTURE.md`、`doc/ROADMAP.md`、`doc/CHANGELOG.md`

### ✅ v2.2 Human 集成 + Plant 增强（2026-06-08）
- Human 感知/对话系统对接记忆层
- Plant 感知系统（光/水/化学）

### ✅ v2.3 存档统一 + 旧系统迁移（2026-06-08）
- UnifiedSaveSystem（World + MemoryLayer）

### ✅ v3.0 正式发布（2026-06-08）
- 事件总线系统
- 可视化工具（5 种可视化类型）
- 空间索引优化（5x+ 加速）
- 260 个测试全部通过

---

## 未来迭代

### v3.0.1 基础设施（2026-06-09）✅
- [x] 通用路径规划服务（A* / 视线 / 流场）
- [x] 碰撞检测系统（Collider / Obstacle / 自动分离）
- [x] 建筑实体化（hut / workshop / storage / farm）
- [x] AnimalMigrationSystem 迁移到通用路径规划
- [x] 自然演化制作系统（无硬编码配方）
- [x] 农业系统（生长从环境条件自然计算）
- [x] 环境灾害系统（火灾/洪水/干旱）
- [x] 烹饪系统（无硬编码食谱）
- [x] 衣物系统（保暖/耐久/湿度）
- [x] 时间事件调度器（最小堆）
- [x] 增量存档系统（快照对比）
- [x] 文明演化仪表盘（实时监控）

### v3.0.2 行为调度修复 + 性能优化（2026-06-09）✅
- [x] 修复 SearchSystem 直接设置 current_action 导致动作队列中断
- [x] 修复 PlanningSystem EAT 意图未设置 target_entity
- [x] 系统 tick_interval 优化（55→45 系统每帧执行）
- [x] 端到端行为链路测试（饥饿→寻找→移动→进食）

### v3.0.3 集合迭代修复 + 昼夜节律 + 气味扩散（2026-06-10）✅
- [x] 修复 4 处集合迭代修改（`list()` 复制后再删除）
- [x] 修复 EventBus `_dispatch()` 迭代安全性
- [x] 修复内存泄漏风险（历史记录限制上限）
- [x] 昼夜节律系统（CircadianComponent + CircadianSystem，11 测试）
- [x] 气味扩散系统（SmellComponent + SmellDiffusionSystem，7 测试）

### v3.1 系统集成（2026-06-10）✅
- [x] 昼夜节律集成到决策系统（夜间降低活动，白天增加）
- [x] 气味感知集成到搜索系统（visual → smell → memory → explore）
- [x] 新增 5 个集成测试

### v3.2 性能优化 + 生态深化（2026-06-10）✅
- [x] 实体池系统（EntityPool + PooledEntity，8 测试）
- [x] 根系系统（RootComponent + RootSystem，7 测试）
- [x] 修复性能测试除零错误

### v3.3 全功能迭代（2026-06-10）✅
- [x] 实体池默认启用并集成到 World.create_entity()
- [x] 植物 Component 补全（health/water/nutrients/energy）
- [x] 季节变化系统（SeasonChangeSystem，5 测试）
- [x] 多线程 System 更新（ParallelSystemExecutor，6 测试）

### v3.4 监控 + 兼容性（2026-06-10）✅
- [x] 实体池性能监控（命中率、自动调优，5 测试）
- [x] PlantComponent 旧存档迁移（ComponentMigrator，4 测试）

### v3.5 环境模块补全（2026-06-10）✅
- [x] 水文系统（Hydrology）：水循环闭环，8 测试
- [x] 地质系统（Geology）：侵蚀/沉积，4 测试
- [x] 污染系统（Pollution）：三维扩散，4 测试
- [x] 海洋系统（Ocean）：洋流/潮汐，6 测试
- [x] 天文系统（Astronomy）：引力潮汐，7 测试
- [x] 极端天气（ExtremeWeather）：风暴物理，9 测试

### v3.6 系统联动 + 性能优化（2026-06-11）✅
- [x] 物候学系统（PhenologyComponent + PhenologySystem，10 测试）
- [x] 候鸟迁徙系统（MigrationComponent + MigrationSystem，10 测试）
- [x] atmosphere 化学成分（CO/NO2/SO2/O3/PM2.5/PM10）
- [x] light_field 紫外线（UV-A/UV-B/UV-C/UV指数）
- [x] 系统集成测试：6 个联动测试全部通过
- [x] 系统联动修复：Hydrology↔Plant / Ocean↔Climate / Astronomy↔Season / Pollution↔Biology / UV↔Biology / Migration↔Animal
- [x] 新系统注册：SimulationLoop 注册 11 个系统
- [x] 性能优化：SpatialIndex 空间索引
- [x] 代码巡检修复：集合迭代修改 / 内存泄漏 / 并发安全警告

### v3.7 核心重构（2026-06-11）✅
- [x] Query API（`world.query()` 声明式查询，11 测试）
- [x] SearchSystem 策略拆分（4 策略类，461→200 行）
- [x] DecisionSystem 策略拆分（8 策略类，374→150 行）
- [x] Component 纯数据化示例（HealthStatusComponent → HealthStatusSystem，8 测试）
- [x] 第 11 次巡检问题修复（集合迭代 / 内存泄漏 / 并发安全）

### v3.8 核心重构深化（2026-06-11）✅
- [x] EnvironmentalContinuumSystem 处理器拆分（5 处理器，552→100 行）
- [x] LifeCycleComponent 纯数据化（方法迁移到 LifeCycleSystem）
- [x] EntityPool 自动调优定时触发（每 100 次调用）
- [x] 适配现有系统（animal_reproduction / seed_dispersal / plant_tests）

### v3.9 核心重构完成（2026-06-11）✅
- [x] PhysicalWeatherSystem 处理器拆分（6 处理器，490→120 行）
- [x] 性能监控系统（PerformanceMonitor + @monitored_update，11 测试）
- [x] 适配 SeasonComponent 新 API（year_progress/year_length_hours）

### ✅ v4.0 架构重构（2026-06-12）
- [x] World 拆分：EntityManager + ArchetypeStore + SystemScheduler
- [x] Archetype 存储：列式存储，查询性能提升
- [x] System 依赖图：声明式依赖，自动拓扑排序
- [x] Component 纯数据化：MemoryComponent / WorldConfigComponent / ActionComponent
- [x] 测试补充：human +28 / core +9 / plant +2 = +39 测试
- [x] WorldEventBus：每 World 独立事件总线
- [x] ComponentSerializer：统一序列化框架

### v4.1 计划
- [ ] 更多 Component 纯数据化（剩余 40+ 个含方法 Component）
- [ ] 各模块 README 补充
- [ ] API 文档自动生成
- [ ] 季节系统细化（纬度、海拔影响）

### v5.0 分布式模拟
- [ ] 多进程/多机分布式
- [ ] 机器学习驱动的行为系统
- [ ] 3D 可视化支持
- [ ] 插件系统

### v4.0 分布式模拟
- [ ] 多进程/多机分布式
- [ ] 机器学习驱动的行为系统
- [ ] 3D 可视化支持
- [ ] 插件系统

---

## 技术债务追踪

| 债务 | 优先级 | 状态 | 计划版本 |
|------|--------|------|----------|
| World 职责过重 | P0 | ✅ v4.0 已拆分 | v4.0 |
| Archetype 存储 | P0 | ✅ v4.0 已实现 | v4.0 |
| System 依赖图 | P1 | ✅ v4.0 已实现 | v4.0 |
| Component 纯数据化 | P1 | ✅ v4.0 已迁移核心组件 | v4.0 |
| 测试覆盖均衡 | P1 | ✅ v4.0 已补充 | v4.0 |
| 事件总线隔离 | P2 | ✅ v4.0 已实现 | v4.0 |
| 统一序列化 | P2 | ✅ v4.0 已实现 | v4.0 |
| 各模块 README 缺失 | 低 | ⚠️ 待补充 | v4.1 |
| API 文档自动生成 | 低 | ⚠️ 待实现 | v4.1 |
| 类型注解覆盖率提升 | 中 | ⚠️ 待提升 | v4.1 |

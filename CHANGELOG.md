# 更新日志

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

### 文明演化仪表盘
- 新增 `presentation/visualization/civilization_dashboard.py`
  - 生成文明繁衍的实时监控仪表盘 HTML
  - 支持世界地图、趋势图、知识进度、事件日志
- 新增 `presentation/visualization/civilization_dashboard.html`
  - 完整前端实现：Canvas 世界地图、Chart.js 趋势图
  - 暗色主题、响应式布局、实时动画
- 新增 `presentation/tests/test_civilization_dashboard.py`（3 个测试）

### 世界模拟全生态仪表盘
- 新增 `presentation/visualization/world_simulation_dashboard.py`
  - WorldSnapshot：完整世界快照（实体/生态/文明/环境/灾害）
  - WorldSimulationDashboard：捕获快照、导出 JSON/HTML
  - 支持实体位置获取用于地图显示
- 新增 `presentation/visualization/world_simulation_dashboard.html`
  - 全生态监控：人类/动物/植物/建筑/农田/土壤/灾害
  - Canvas 世界地图：6 种实体类型 + 图层切换
  - Chart.js 双趋势图：生态种群 + 文明发展
  - 环境指标：温度/湿度/降雨/风速进度条
  - 生物多样性面板：丰富度/生物量/健康度
  - 知识积累：制作/农业/建筑技术进度
  - 系统性能监控
  - 事件日志 + 灾害警报
- 新增 `presentation/visualization/run_world_simulation.py`
  - 完整世界模拟运行器（植物/动物/人类/建筑/农田/土壤）
  - 实时导出仪表盘 HTML
- 新增 `presentation/tests/test_world_simulation_dashboard.py`（5 个测试）

### 测试
- 总测试数: **364** 个（全部通过）

---

## v3.0 (2026-06-08)

### 性能优化
- 新增 `core/spatial_index.py` — 均匀网格空间索引，O(1)~O(k) 查询
- 新增 `core/tests/test_performance.py` — 4 个性能基准测试
- 空间索引 vs 暴力查询：**5x+ 加速**

### 可视化工具
- 新增 `presentation/visualization/world_visualizer.py`
  - 实体分布热力图、系统性能监控、实体关系网络
  - 记忆网络图、事件时间轴
  - 导出交互式 HTML（基于 D3.js）
- 新增 `presentation/tests/test_visualization.py`（9 个测试）

### 事件总线系统
- 新增 `core/event_bus.py` — 全局单例事件总线
  - 订阅/发布/取消订阅、优先级处理、一次性订阅、过滤函数
  - 事件历史记录、统计信息
- `core/world.py` 集成：实体创建/销毁自动触发事件

### 测试
- 总测试数: **260** 个（全部通过）

---

## v2.3 (2026-06-08)

### 存档系统统一
- 新增 `save_load/unified_save_system.py`
  - 整合 World 序列化 + MemoryLayer 持久化
  - 统一存档格式：`{version, world, memory_layer, meta}`
- 新增 `save_load/tests/test_unified_save.py`（8 个测试）

### 旧系统迁移
- `memory/` 目录确认为笔记存档
- `memory_layer/` 为唯一活跃记忆系统

---

## v2.2 (2026-06-08)

### Human 模块记忆层集成
- `human/systems/cognitive/perception_system.py` — 感知时自动记录 ContactRecord
- `human/systems/interaction/dialogue_system.py` — 对话时叙述传播给旁观者
- 新增 `human/tests/test_human_memory_integration.py`（5 个测试）

### Plant 模块增强
- 新增 `plant/components/plant_perception_component.py`（光/水/化学/重力感知）
- 新增 `plant/systems/plant_perception_system.py`
- 新增 `plant/tests/test_plant_memory_integration.py`（6 个测试）

---

## v2.1 (2026-06-08)

### 架构优化
- 新增 `ARCHITECTURE.md`、`ROADMAP.md`、`CHANGELOG.md`
- 清理根目录临时文件
- 扫描确认无 `except:pass` 残留、无 `dt` 类型注解缺失

### 统一记忆层 Phase 4
- `memory_persistence.py` — 存档/读档/自动保存
- `test_phase4.py` — 11 个测试（持久化 + 性能 + 压力）

---

## v2.0 (2026-06-08)

### Animal 模块全面重构
- 文件从 7 → 27 个，系统从 3 → 10 个
- 新增组件：AnimalNeeds, AnimalSocial, AnimalMemory, AnimalTerritory, AnimalReproduction
- 新增系统：AnimalNeedsSystem, AnimalSocialSystem, AnimalMemorySystem, AnimalTerritorySystem, AnimalMigrationSystem, AnimalPerceptionSystem, AnimalLearningSystem
- 25/25 测试通过

### 统一记忆层 Phase 1-3
- Phase 1: 核心骨架（16 核心类，23 个测试）
- Phase 2: ECS 集成（World 钩子 + Perception/Social 系统，6 个集成测试）
- Phase 3: 高级特性（认知框架 + 扭曲引擎 + 传话游戏，13 个测试）

---

## v1.5 (2026-05)

### 生物模块
- 生命周期系统（出生/成长/死亡）
- 能量系统
- 疾病传播系统

---

## v1.0 (2026-05)

### 核心框架
- ECS 核心（Entity/Component/System/World）
- 空间系统、时间系统、环境系统

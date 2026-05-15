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
- `world.get_environment()` → 获取环境组件

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
├── time_system.py          #  年/月/日/时 推进
├── time_component.py       #  时间数据
└── time_utils.py           #  辅助函数
```

### 2.3 人类系统 (Human)

```
human/
├── components/
│   ├── basic/              # HumanComponent, AgeComponent, GenderComponent, BodyComponent, IdentityComponent
│   ├── physiological/      # PhysiologyNeedsComponent(饥/渴/能/疲/社交), HealthComponent
│   ├── cognitive/          # IntentComponent, TaskComponent, GoalComponent, BrainComponent, MemoryComponent, PersonalityComponent
│   ├── action/             # ActionComponent(当前动作+队列+进度)
│   ├── abilities/          # VelocityComponent, VisionComponent(radius=12), SkillComponent, SearchComponent
│   ├── economic/           # InventoryComponent(背包, 20格), EconomyComponent
│   └── social/             # SocialComponent, RelationshipComponent, ReproductionComponent
│
├── systems/
│   ├── core/               # 行为流水线
│   │   ├── intent_system.py      # Need → Intent (紧急度评分)
│   │   ├── planning_system.py    # Intent → ActionQueue
│   │   └── action_system.py      # 调度器: 出队/进度检查/切换
│   ├── action/             # 执行层
│   │   ├── movement_system.py    # MOVE_TO: 欧几里得距离移动, 1单位/步
│   │   ├── search_system.py      # SEARCH: 视野内找资源, 失败则随机漫游
│   │   ├── pickup_system.py      # PICKUP: 拾取→背包→设置所有权→移除空间索引
│   │   ├── eat_system.py         # EAT: 从背包找食物, 消耗减饥饿
│   │   ├── drink_system.py       # DRINK: 背包→地面水源
│   │   ├── sleep_system.py       # SLEEP: 3h恢复全部能量
│   │   └── socialize_system.py   # SOCIALIZE
│   ├── cognitive/          # 感知层
│   │   ├── preception_system.py  # 视野填充: SpaceSystem.query_radius → vision.entities
│   │   └── decision_system.py    # 高层决策
│   ├── physiological/      # 生理层
│   │   ├── physiology_needs_system.py  # 每步更新: 饥饿+8/h, 口渴+12/h, 能量-7/h(耦合项)
│   │   └── health_system.py            # 健康状态
│   └── social/             # 社交层
│       ├── social_system.py
│       ├── pairing_system.py
│       └── reproduction_system.py
│
├── entities/
│   └── human_entity.py     # 模板: create_components() 创建所有组件实例
│
└── human_factory.py        # 创建人类: 实体+组件+初始水壶
```

### 2.4 资源系统 (Resource)

```
resource/
├── food/
│   ├── components/food_component.py   # FoodComponent(amount, food_type, spoilage)
│   ├── food_factory.py                # 创建食物实体
│   └── food_types.py
├── water/
│   ├── components/water_component.py  # WaterComponent(amount, temperature, purity)
│   └── water_factory.py               # 创建水源实体
└── components/
    └── resource_component.py          # ResourceComponent(resource_type, amount)
```

### 2.5 环境系统 (Environment)

```
environment/
├── environment_component.py    # 全局环境数据
├── environment_factory.py
├── day_night_system.py         # 昼夜循环
├── weather__init__.py
├── config/
│   └── environment_builder.py  # 构建所有环境子系统
├── atmosphere/                 # (部分损坏, 已跳过初始化)
├── weather/                    # 部分工作
│   ├── weather_system.py
│   └── ... (weather_lifetime_system, 等)
└── season/                     # 季节系统
```

### 2.6 生物学系统 (Biology)

```
biology/
├── components/    # EnergyComponent, GenomeComponent, GrowthComponent, MorphologyComponent, PhenotypeComponent
├── systems/       # DeathSystem, GeneExpressionSystem, GrowthSystem, MorphologySystem, MutationSystem, ReproductionSystem
├── genetics/      # Gene
├── traits/        # Trait
└── factories/
    └── plant_factory.py   # 植物工厂
```

### 2.7 文明系统 (Civilization)

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
└── ...
```

---

## 三、执行流水线 (SimulationLoop)

`main.py` 中的系统执行顺序 (每步调用):

```
更新顺序 → 系统                                  → 作用
─────────────────────────────────────────────────────────────
 1. PreceptionSystem      视野: SpaceSystem.query_radius → vision.entities
 2. IntentSystem          需求→意图: 紧急度评分, 选最高
 3. PlanningSystem        意图→动作队列
 4. ActionSystem          调度: 出队下一个动作
 5. SearchSystem          执行 SEARCH: 视野内找 Food/WaterComponent
 6. MovementSystem        执行 MOVE_TO: 向 target_pos 移动
 7. EatSystem             执行 EAT: 背包找 FoodComponent → 消耗
 8. DrinkSystem           执行 DRINK: 背包找 WaterComponent → 消耗
 9. SleepSystem           执行 SLEEP: 3h 恢复 100 能量
10. PickupSystem          执行 PICKUP: 拾取→背包→所有权→移出空间索引
11. SocializeSystem       执行 SOCIALIZE
─────────────────────────────────────────────────────────────
12. SocialSystem          社交关系更新
13. PairingSystem         配对
14. ReproductionSystem    繁衍
15. DecisionSystem        高层决策
─────────────────────────────────────────────────────────────
16. PhysiologyNeedsSystem  生理需求更新: 饥+8/h, 渴+12/h, 能-7/h
17. HealthSystem           健康状态
─────────────────────────────────────────────────────────────
18. GeneExpressionSystem   基因表达
19. GrowthSystem           生长
20. MorphologySystem       形态
21. DeathSystem            死亡判定
─────────────────────────────────────────────────────────────
22. TransformationSystem   规则变换(腐败等)
─────────────────────────────────────────────────────────────
23. CivilizationSystem     文明阶段
─────────────────────────────────────────────────────────────
24. SpaceSystem.update()   同步 dirty 位置
```

---

## 四、人类行为流水线

```
PhysiologyNeedsSystem
    ↓ 更新饥/渴/能
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
    → DrinkSystem: 背包查找优先, 地面水源备选
    → thirst -= 50
```

### 能量流
```
PhysiologyNeedsSystem 每步: energy -= (4 + hunger_coupling + thirst_coupling)
    → energy < 40 → IntentSystem 选中 SLEEP(权重1.3)
    → SleepSystem: 3h后 add_energy(100)
    → 唤醒后 energy=93(扣除生理衰减) → 继续活动 ~8h
```

---

## 七、当前已验证的状态 (2026-04-28)

| 指标 | 值 |
|------|-----|
| 模拟步数 | 300 步 (12.5 天) |
| 人口存活率 | 10/10 |
| 实体总数 | ~105 |
| 地图大小 | 100 × 100 |
| 行为多样性 | EAT / DRINK / SLEEP / EXPLORE 交替 |
| 饮水验证 | 口渴从 100 → 61 (背包水壶) |
| 进食验证 | SEARCH → MOVE_TO → PICKUP → EAT 全链路 |
| 睡眠验证 | 3h 能量 0 → 100 |
| 模拟速度 | ~2000 步/秒 |

---

## 八、待修复/优化的模块

- **DeathSystem**: 死亡判定存在但未生效(无饥饿致死的条件检查)
- **Atmosphere/Convection 子系统**: 初始化时抛出异常，已跳过
- **ReproductionSystem**: 配对逻辑存在但未触发(社交需求不被优先响应)
- **TransformationSystem**: 食物腐败规则存在但未验证
- **资源再生**: 消耗完的食物/水源不会刷新
- **SleepSystem 效率**: 3h 睡眠期间生理需求继续增长，导致醒来后立即触发其它需求

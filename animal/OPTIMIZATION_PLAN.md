# Animal 模块全面重构计划（方案 C）

## 目标
将 animal 模块从简单的觅食/捕食/繁殖三系统，升级为完整的动物生态模拟系统。

## 阶段划分（全部完成 ✅）

### Phase 1: 基础重构（现有问题修复）✅
- [x] 1.1 拆分 PredationSystem.update() 为子方法
- [x] 1.2 将 System 级 dict 状态改为 Component
- [x] 1.3 优化 GrazingSystem 查询性能
- [x] 1.4 扩展 AnimalComponent 属性

### Phase 2: 需求系统（新增 Needs）✅
- [x] 2.1 创建 AnimalNeedsComponent
- [x] 2.2 创建 AnimalNeedsSystem
- [x] 2.3 集成到现有行为系统

### Phase 3: 社交系统（新增 Social）✅
- [x] 3.1 创建 AnimalSocialComponent
- [x] 3.2 创建 AnimalSocialSystem
- [x] 3.3 群体行为模拟

### Phase 4: 记忆系统（新增 Memory）✅
- [x] 4.1 创建 AnimalMemoryComponent
- [x] 4.2 创建 AnimalMemorySystem
- [x] 4.3 记忆驱动决策

### Phase 5: 高级生态（Migration + Territory）✅
- [x] 5.1 创建 AnimalTerritoryComponent
- [x] 5.2 创建 AnimalTerritorySystem
- [x] 5.3 创建 AnimalMigrationSystem

### Phase 6: 集成与测试 ✅
- [x] 6.1 更新 __init__.py 导出
- [x] 6.2 更新 simulation_loop.py 注册
- [x] 6.3 运行测试验证

## P1 优化（已完成 ✅）
- [x] GrazingSystem 批量查询优化 + 记忆驱动觅食
- [x] AnimalReproductionSystem dict → Component 重构
- [x] 新增 AnimalReproductionComponent（怀孕/冷却期/分娩）

## P2 优化（已完成 ✅）
- [x] AnimalMigrationSystem A* 路径规划
- [x] 感官系统（AnimalPerceptionComponent + PerceptionSystem）
- [x] 学习系统（AnimalLearningComponent + LearningSystem）

## 文件变更清单

### 修改现有文件
- `animal/components/animal_component.py` — 扩展属性
- `animal/systems/predation_system.py` — 拆分方法
- `animal/systems/grazing_system.py` — 优化查询
- `animal/animal_factory.py` — 挂载新组件
- `animal/__init__.py` — 导出新类

### 最终文件结构（25 个 Python 文件）
```
animal/
├── components/                      (8 个 Component)
│   ├── __init__.py
│   ├── animal_component.py          (修改：扩展属性)
│   ├── animal_needs_component.py    (新增)
│   ├── animal_social_component.py   (新增)
│   ├── animal_memory_component.py   (新增)
│   ├── animal_territory_component.py (新增)
│   ├── animal_reproduction_component.py (新增：替代 dict)
│   ├── animal_perception_component.py   (新增：P2)
│   └── animal_learning_component.py     (新增：P2)
├── systems/                         (10 个 System)
│   ├── __init__.py
│   ├── grazing_system.py            (重构：批量查询+记忆驱动)
│   ├── predation_system.py          (重构：拆分方法)
│   ├── animal_reproduction_system.py (重构：Component 化)
│   ├── animal_needs_system.py       (新增)
│   ├── animal_social_system.py      (新增)
│   ├── animal_memory_system.py      (新增)
│   ├── animal_territory_system.py   (新增)
│   ├── animal_migration_system.py   (新增：A* 路径规划)
│   ├── animal_perception_system.py  (新增：P2)
│   └── animal_learning_system.py    (新增：P2)
├── tests/                           (25 个测试)
│   ├── test_animal_module.py        (13 个测试)
│   └── test_animal_module_p2.py     (12 个测试)
├── animal_factory.py                (修改：挂载 8 个组件)
├── presets.py
├── __init__.py                      (修改：导出新类)
├── OPTIMIZATION_PLAN.md             (全部完成)
└── REFACTOR_SUMMARY.md
```

## 设计原则
1. 每个 Component 只存数据，业务逻辑在 System 中
2. 所有新 Component 使用 `@dataclass(slots=True)`
3. System 的 update() 不超过 80 行
4. 使用 logger 替代 print
5. 类型注解完整

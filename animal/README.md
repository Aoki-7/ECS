# Animal 模块 — ECS 世界模拟系统

动物生态模拟子系统，提供完整的动物实体生命周期管理，涵盖生理需求、社交行为、环境感知、学习记忆、领地防御和季节性迁徙。

---

## 目录

- [架构概览](#架构概览)
- [快速开始](#快速开始)
- [组件清单](#组件清单)
- [系统清单](#系统清单)
- [设计原则](#设计原则)
- [扩展指南](#扩展指南)
- [测试](#测试)
- [版本历史](#版本历史)

---

## 架构概览

```
AnimalEntity (8 Components + biology components)
├── AnimalComponent              # 物种/食性/性别/年龄
├── AnimalNeedsComponent         # 饥饿/口渴/睡眠/恐惧/繁殖
├── AnimalSocialComponent        # 群体/配偶/后代/关系
├── AnimalMemoryComponent        # 环境记忆（食物/威胁/庇护所）
├── AnimalTerritoryComponent     # 领地中心/半径/入侵者
├── AnimalReproductionComponent  # 怀孕/冷却期/分娩
├── AnimalPerceptionComponent    # 视觉/听觉/嗅觉
├── AnimalLearningComponent      # 行为记录/习惯化/敏感化
├── EnergyComponent              # (biology)
├── SpaceComponent               # (space)
└── ... other biology components

Systems (10 Systems, 按优先级执行)
├── AnimalPerceptionSystem   (44)  # 多感官感知
├── AnimalNeedsSystem        (44)  # 需求自然增长
├── AnimalSocialSystem       (44)  # 群体形成/配偶配对
├── AnimalMemorySystem       (44)  # 记忆衰减与强化
├── AnimalLearningSystem     (44)  # 行为学习
├── AnimalTerritorySystem    (45)  # 领地巡逻/入侵防御
├── AnimalMigrationSystem    (46)  # A* 路径规划迁徙
├── GrazingSystem            (42)  # 植物觅食（记忆驱动）
├── PredationSystem          (49)  # 捕食行为
└── AnimalReproductionSystem (50)  # 繁衍后代
```

---

## 快速开始

### 创建动物实体

```python
from core.world import World
from animal.animal_factory import AnimalFactory

world = World()

# 创建单个动物
entity = AnimalFactory.create_animal(
    world,
    species="predator",   # 物种：basic / fast / tank / predator / scavenger
    x=10, y=20,           # 初始坐标
    variation=0.15        # 基因变异系数
)

# 批量创建
entities = AnimalFactory.create_batch(
    world, count=10, species="fast"
)
```

### 运行动物系统

```python
from animal.systems import *

# 注册到 World（通常由 SimulationLoop 自动完成）
world.add_system(AnimalNeedsSystem())
world.add_system(AnimalPerceptionSystem())
world.add_system(AnimalLearningSystem())

# 执行一个 tick
world.update(delta_hours=1.0)
```

### 访问动物状态

```python
from animal.components import *

animal = world.get_component(entity, AnimalComponent)
needs = world.get_component(entity, AnimalNeedsComponent)
memory = world.get_component(entity, AnimalMemoryComponent)

print(f"物种: {animal.species}, 饥饿: {needs.hunger:.2f}")
print(f"主导需求: {needs.get_dominant_need()}")

# 回忆最近的食物位置
food_mem = memory.recall_by_type("food")
if food_mem:
    print(f"记忆中的食物: ({food_mem.x}, {food_mem.y})")
```

---

## 组件清单

| 组件 | 核心属性 | 用途 |
|------|---------|------|
| `AnimalComponent` | `species`, `diet`, `gender`, `age`, `is_adult` | 动物基础标识 |
| `AnimalNeedsComponent` | `hunger`, `thirst`, `sleepiness`, `fear`, `reproductive_urge` | 生理需求驱动 |
| `AnimalSocialComponent` | `group_id`, `mate_id`, `offspring_ids`, `relationship_scores` | 社交关系 |
| `AnimalMemoryComponent` | `memories[max=20]`, `decay_rate`, `recall_accuracy` | 环境记忆 |
| `AnimalTerritoryComponent` | `center_x/y`, `radius`, `intruders`, `scent_strength` | 领地管理 |
| `AnimalReproductionComponent` | `is_pregnant`, `cooldown_ticks`, `reproduction_count` | 繁殖状态 |
| `AnimalPerceptionComponent` | `vision_range`, `hearing_range`, `smell_range`, `detected_entities` | 感官输入 |
| `AnimalLearningComponent` | `behavior_records`, `habituation`, `sensitization` | 行为学习 |

---

## 系统清单

### 感知系统 (AnimalPerceptionSystem)
- **tick_interval**: 8
- **功能**: 视觉（昼夜影响）+ 听觉 + 嗅觉融合
- **输出**: `detected_entities` 自动记录到 `AnimalMemoryComponent`

### 需求系统 (AnimalNeedsSystem)
- **tick_interval**: 5
- **功能**: 饥饿/口渴/睡眠/恐惧/繁殖欲望自然增长
- **驱动**: 高需求触发 GrazingSystem / PredationSystem / MigrationSystem

### 学习系统 (AnimalLearningSystem)
- **tick_interval**: 15
- **功能**: 
  - 行为-结果关联（加权平均）
  - 习惯化：重复无害刺激反应减弱
  - 敏感化：强烈负面刺激反应增强
- **输出**: `get_best_behavior(context)` 返回历史最优行为

### 社交系统 (AnimalSocialSystem)
- **tick_interval**: 20
- **功能**: 群体形成、配偶配对、关系衰减

### 记忆系统 (AnimalMemorySystem)
- **tick_interval**: 10
- **功能**: 记忆衰减、位置强化、过期清理

### 领地系统 (AnimalTerritorySystem)
- **tick_interval**: 25
- **功能**: 领地跟随、入侵检测、边界巡逻、气味标记

### 迁徙系统 (AnimalMigrationSystem)
- **tick_interval**: 30
- **功能**: A* 路径规划 + 记忆引导 + 群体同步迁徙

### 食草系统 (GrazingSystem)
- **tick_interval**: 10
- **优化**: 批量植物缓存 + 记忆驱动觅食

### 捕食系统 (PredationSystem)
- **tick_interval**: 15
- **重构**: update() 拆分为 9 个子方法（每方法 ≤40 行）

### 繁殖系统 (AnimalReproductionSystem)
- **tick_interval**: 20
- **重构**: `dict` 状态 → `AnimalReproductionComponent`
- **机制**: 怀孕 → 冷却期 → 分娩

---

## 设计原则

1. **数据与逻辑分离**: Component 只存数据，System 执行业务逻辑
2. **slots=True**: 所有新 Component 使用 `@dataclass(slots=True)` 提升内存效率
3. **update() ≤ 80 行**: 超长方法拆分为子方法
4. **状态 Component 化**: System 不持有实体状态，全部存储在 Component 中
5. **logger 替代 print**: 所有系统使用 `logging.getLogger(__name__)`
6. **类型注解完整**: 所有公共方法参数和返回值均有类型注解

---

## 扩展指南

### 新增物种

编辑 `presets.py`，添加新的物种预设：

```python
SPECIES_PRESETS = {
    "my_species": {
        "max_hunger_rate": 5.0,
        "metabolism_rate": 0.02,
        "optimal_temp": 37.0,
        "growth_partition": 0.4,
        "speed_factor": 1.0,
        "sensing_range": 5.0,
        "diet_type": 0.5,  # 0=草食, 1=肉食
    },
}
```

### 新增行为

1. 在 `AnimalLearningComponent.BehaviorRecord` 中定义行为名称
2. 在对应 System 中调用 `learning.record_behavior(behavior, context, outcome)`
3. 在 `AnimalLearningSystem._evaluate_recent_behavior` 中添加评估逻辑

### 新增感官类型

1. 在 `AnimalPerceptionComponent` 中添加感官范围属性
2. 在 `AnimalPerceptionSystem` 中添加 `_xxx_perception` 方法
3. 在 `_map_to_memory_type` 中映射到记忆类型

---

## 测试

```bash
# 运行全部测试
cd D:\个人助手\workspace\ECS
python -m pytest animal/tests/ -v

# 运行 P1 测试
python -m pytest animal/tests/test_animal_module.py -v

# 运行 P2 测试
python -m pytest animal/tests/test_animal_module_p2.py -v
```

**当前状态**: 25/25 测试通过

| 测试文件 | 用例数 | 覆盖范围 |
|----------|--------|----------|
| `test_animal_module.py` | 13 | Phase 1-6 + P1 |
| `test_animal_module_p2.py` | 12 | P2 感官/学习/迁徙 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-04 | 初始版本：GrazingSystem + PredationSystem + AnimalReproductionSystem |
| 2.0 | 2026-06-08 | 全面重构（方案 C）：8 个 Component + 10 个 System + 25 个测试 |
| 2.1 | 2026-06-08 | P1 优化：批量查询 + 记忆驱动觅食 + ReproductionComponent 化 |
| 2.2 | 2026-06-08 | P2 优化：A* 路径规划 + 感官系统 + 学习系统 |

---

## 相关模块

- `biology/` — 基因组、生命周期、能量、形态等基础生物学组件
- `plant/` — 植物系统（GrazingSystem 的食物来源）
- `space/` — 空间索引（所有位置查询的基础）
- `environment/` — 环境数据（温度、光照等影响动物生理）

---

*文档版本: 2.2*  
*最后更新: 2026-06-08*  
*作者: Agent `coder`*

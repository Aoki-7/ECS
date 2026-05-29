# 开发者指南 (Developer Guide)

> 面向贡献者：如何向 ECS 世界模拟系统贡献代码、添加新系统、拓展功能。

---

## 📚 目录

- [项目概览 (Project Overview)](#项目概览)
- [代码风格 (Code Style)](#代码风格)
- [ECS 架构开发流程](#ecs-架构开发流程)
- [添加新系统 (Adding New Systems)](#添加新系统)
- [添加新组件 (Adding New Components)](#添加新组件)
- [扩展现有行为](#扩展现有行为)
- [测试最佳实践](#测试最佳实践)
- [性能检查](#性能检查)
- [调试技巧](#调试技巧)
- [贡献流程 (Contribution Flow)](#贡献流程)

---

## 🌍 项目概览

### 项目核心理念

```
连续物理量驱动世界演化
```

**核心理念**：
- 底层只有连续物理量的自然演化
- 所有离散状态（晴/雨/季节/事件）都是物理量的实时视图
- 物理驱动而非随机事件驱动

**ECS 架构**：
- Component：纯数据存储（dataclass）
- System：纯逻辑处理（update 函数）
- World：双向索引中心（管理 Entity↔Component↔System 关系）

---

## 📏 代码风格

### Python 代码规范

**遵循 PEP 8**：
- 4 空格缩进
- 函数名使用 snake_case
- 类名使用 PascalCase
- 常量使用大写

**示例代码风格**：

```python
# ❌ 不符合风格
class Entity:
  position = [0,0]
  velocity= [0.0,0.0]
  def update(self):
    self.position[0]+= self.velocity[0]

# ✅ 符合风格
@dataclass
class PositionComponent(Component):
    x: float = 0.0
    y: float = 0.0

class MovementSystem(System):
    def update(self, world: World, dt: float):
        """更新所有具有位置组件的实体"""
        for entity_id, pos in world.get_components(PositionComponent):
            pos.x = self.velocity.x * dt
            pos.y = self.velocity.y * dt
```

### 命名约定

| 类型 | 命名方式 | 示例 |
|------|---------|-|----|
| Component | PascalCase + Component 后缀 | `HealthComponent`、`PositionComponent` |
| System | PascalCase + System 后缀 | `MoveSystem`、`WeatherSystem` |
| Entity | `Entity_<id>` | `Entity_100` |
| 方法 | snake_case | `update()`, `get_components()` |
| 常量 | 大写_SNAKE_CASE_ | `MAX_HEALTH = 100.0` |

---

## 🛠️ ECS 架构开发流程

### 标准开发流程

```
1. 定义 Component (纯数据)
2. 实现 System (纯逻辑)
3. 注册到 World
4. 添加测试覆盖
```

**示例流程**：

#### Step 1：定义 Component

```python
# health_component.py
from core.component import Component

@dataclass
class HealthComponent(Component):
    """健康值组件"""
    health: float = 100.0
    max_health: float = 100.0
    regeneration_rate: float = 0.5  # 每秒恢复
```

**说明**：Component 仅描述"一个实体的一个维度"

#### Step 2：实现 System

```python
# health_system.py
from core.component import Component
from core.system import System

class HealthSystem(System):
    """健康系统处理所有健康值更新"""
    
    @property
    def priority(self) -> int:
        return 10
    
    def update(self, world: World, dt: float):
        """
        每秒调用一次
        
        Args:
            world: World 实例
            dt: 时间步长 (秒)
        """
        for entity_id, health_comp in world.get_components(HealthComponent):
            # 自然恢复
            if health_comp.health < health_comp.max_health:
                health_comp.health = min(
                    health_comp.health + health_comp.regeneration_rate * dt,
                    health_comp.max_health
                )
```

**说明**：System 只处理单一职责，不持有状态

#### Step 3：注册到 World

```python
# world.py
from core.world import World
from health_system import HealthSystem

world = World()

# 注册系统
world.register_system(HealthSystem, priority=10)
```

#### Step 4：添加测试

```python
# test_health_system.py
import unittest
from health_system import HealthSystem

class TestHealthSystem(unittest.TestCase):
    
    def setUp(self):
        self.world = World()
        self.system = HealthSystem()
        
    def test_health_regeneration(self):
        """测试健康值恢复"""
        # 创建测试实体
        entity = self.world.create_entity()
        self.world.add_component(entity, HealthComponent(
            health=50,
            max_health=100,
            regeneration_rate=10
        ))
        
        # 运行更新 (0.1 秒)
        self.system.update(self.world, 0.1)
        
        # 验证
        health_comp = self.world.get_component(entity, HealthComponent)
        self.assertAlmostEqual(health_comp.health, 60, places=0)
```

---

## 📦 添加新系统

### 标准添加步骤

#### Step 1：创建新的 System 文件

```python
# path/to/new_system.py
from core.component import Component
from core.system import System

class NewFeatureSystem(System):
    """你的新功能系统"""
    
    @property
    def priority(self) -> int:
        """控制执行顺序，数值越大越晚执行"""
        return 50
    
    def update(self, world: World, dt: float):
        """系统更新逻辑"""
        # 处理逻辑
        pass
```

**设计原则**：
- ✅ 只处理单一职责
- ✅ 不持有状态数据
- ✅ 依赖 World 提供的索引服务

#### Step 2：注册系统

在 `environment/config/environment_builder.py` 或 `main.py` 中注册:

```python
# config/environment_builder.py
from core.world import World
from new_system import NewFeatureSystem

def build_world():
    world = World()
    world.register_system(NewFeatureSystem, priority=50)
    return world
```

#### Step 3：将 World 添加到所有 System

```python
# 如果需要让所有 System 都能访问 World
class WorldSystem(Stateless):
    def __init__(self, world: World):
        self.world = world
```

---

## 🧩 添加新组件

### 定义新数据存储

#### 示例 Component

```python
# new_component.py
from core.component import Component
from dataclasses import dataclass

@dataclass
class NewCapabilityComponent(Component):
    """新能力组件"""
    level: int = 1
    progress: float = 0.0  # 0-1
    activation_thresholds: dict = None
    
    def activation_check(self, world: World) -> bool:
        """检查是否激活"""
        return self.progress >= self.activation_thresholds.get("lvl", -1)
```

#### Component 添加流程

1. 创建 Component（只描述数据）
2. 在 `core/world.py` 中添加新的组件类到 `World._components`
3. System 中通过 `world.get_components(NewCapabilityComponent)` 遍历所有实例
4. 添加组件到 Entity：`world.add_component(entity, NewCapabilityComponent())`

**设计原则**：
- ✅ Component 描述"一个实体的一个维度"
- ✅ 不持有任何逻辑或方法
- ✅ 使用 `@dataclass` 自动生成 `__init__`

---

## 🔄 扩展现有行为

### 继承扩展 System

```python
# 继承现有 System
class OptimizedMovementSystem(MovementSystem):
    """优化的移动系统"""
    
    def update(self, world: World, dt: float):
        super().update(world, dt)
        
        # 添加额外功能
        for entity_id, pos, vel in world.get_components(
            PositionComponent, VelocityComponent
        ):
            # 额外优化逻辑
            if self._is_optimization_needed(pos, vel):
                vel.vx *= 1.01  # 加速
```

### 扩展 Behavior Pipeline

```python
# human/systems/core/behavior_pipeline.py
class BehaviorPipeline:
    """行为流水线扩展支持"""
    
    def __init__(self, world: World, world_entity: WorldEntity):
        self.world = world
        self.world_entity = world_entity
        # 添加自定义行为阶段
        self.custom_behaviors: list[Callable] = []
    
    def register_custom_behavior(self, behavior: Callable):
        """注册自定义行为阶段"""
        self.custom_behaviors.append(behavior)
```

### 扩展 Decision System

```python
# human/systems/core/decision_system.py
class DecisionSystem:
    """决策系统扩展"""
    
    def __init__(self, world: World, human_component: HumanComponent):
        self.world = world
        self.human_component = human_component
    
    def calculate_intent_weights(self, action_type: ActionType) -> float:
        """
        计算动作紧急度
        
        Args:
            action_type: 动作类型（DRINK, EAT, SLEEP, etc）
        
        Returns:
            float: 紧急度（越高越优先）
        """
        human_component = self.world.get_component(
            self.human_entity,
            HumanComponent
        )
        
        if action_type == ActionType.DRINK:
            # 基础权重 1.0
            # 口渴（thirst < 20）增加紧急度
            if human_component.thirst < 20:
                return 1.0 + (20 - human_component.thirst) / 20
            return 1.0
        
        elif action_type == ActionType.EAT:
            # 基础权重 1.0
            # 饥饿（hunger < 20）增加紧急度
            if human_component.hunger < 20:
                return 1.0 + (20 - human_component.hunger) / 20
            return 1.0
        
        elif action_type == ActionType.SLEEP:
            # 基础权重 1.0
            # 疲劳（fatigue > 80）增加紧急度
            if human_component.fatigue > 80:
                return 1.0 + (human_component.fatigue - 80) / 20
            return 1.0
        
        return 1.0
```

---

## 🧪 测试最佳实践

### Unit Test 示例

```python
# tests/test_human_intent.py
import unittest
import sys
sys.path.append('../../..')

from human.systems.core.intent_system import IntentSystem
from human.components import HumanComponent, PhysiologyNeedsComponent

class TestHumanIntent(unittest.TestCase):
    
    def setUp(self):
        self.world = core.World()
        self.system = IntentSystem(self.world)
        
        # 创建人类实体
        self.entity = self.world.create_entity()
        self.world.add_component(self.entity, HumanComponent(age=30))
        self.world.add_component(self.entity, PhysiologyNeedsComponent(
            thirst=15,  # 口渴
            hunger=10,  # 饥饿
            energy=80,  # 能量
            fatigue=30  # 疲劳
        ))
    
    def test_thirst_priority(self):
        """测试口渴优先级增加"""
        # 运行更新
        self.system.update(self.world, world_entity_type=None)
        
        # 验证意图
        intent = self.system.get_current_intent(self.world, self.entity)
        self.assertEqual(intent.action_type.value, ActionType.DRINK.value)
    
    def test_composite_intent(self):
        """测试复合意图计算"""
        # 设置多个需求
        thirsty_component = PhysiologyNeedsComponent(thirst=15)
        hungry_component = PhysiologyNeedsComponent(hunger=10)
        self.world.add_component(self.entity, thirsty_component)
        self.world.add_component(self.entity, hungry_component)
        
        # 运行更新
        self.system.update(self.world, None)
        
        # 验证复合意图
        intent = self.system.get_current_intent(self.world, self.entity)
        self.assertIsNotNone(intent)
```

### Integration Test 示例

```python
# tests/test_environment.py
import unittest
import sys
sys.path.append('../../..')

from environment.config.environment_builder import EnvironmentBuilder

class TestEnvironmentBuilder(unittest.TestCase):
    
    def test_world_creation(self):
        """测试世界创建"""
        builder = EnvironmentBuilder()
        world = builder.build()
        
        # 验证系统已注册
        for system in world._systems:
            print(f"Registered system: {system}")
    
    def test_environment_sync(self):
        """测试环境同步"""
        world = EnvironmentBuilder().build()
        world_entity = world.create_entity()
        
        # 验证同步计算
        world.systems["EnvironmentSyncSystem"].update(world, world_entity, 1.0)
        self.assertEqual(world_systems['EnvironmentSyncSystem'], World(1))
```

---

## ⚡ 性能检查

### 常见性能问题

#### 问题 1：频繁创建对象

```python
# ❌ 错误：每次 update 都创建新对象
def update(self, world, dt):
    for entity in self.world.entities:
        comp = Component()  # 每次都创建
        ...

# ✅ 正确：使用对象池
self._object_pool = Pool(Component)

def update(self, world, dt):
    for entity in self.world.entities:
        comp = self._object_pool.get()
        try:
            # 处理逻辑
            pass
        finally:
            self._object_pool.put(comp)
```

#### 问题 2：遍历索引过大

```python
# ❌ 错误：遍历所有实体
def update(self, world, dt):
    for entity_id, comp in world.get_components(PositionComponent):
        # 遍历 O(n)
        ...

# ✅ 正确：使用空间索引（O(log n)）
def update(self, world, dt):
    entities = world.spatial_index.query_radius(
        x=self.position_x,
        y=self.position_y,
        r=self.radius
    )
    for entity_id, entity in entities:
        # 遍历 O(log n)
        ...
```

#### 问题 3：未使用缓存

```python
# ❌ 错误：每次都查询同一数据
from time_module import TimeComponent
time = world.get_component(entity, TimeComponent)

# ✅ 正确：缓存时间值
if not hasattr(self, '_cached_time_update'):
    self._cached_time_update = True
```

### 性能分析工具

使用以下工具进行性能分析：

```python
# cProfile
import cProfile
cProfile.run('run_simulation()')

# line_profiler
from line_profiler import LineProfiler
@profile
def update_world():
    # 需要剖析的代码
    pass
```

---

## 🐛 调试技巧

### 添加调试输出

```python
# 在 System 中打印优先级
class DebugSystem(System):
    @property
    def priority(self) -> int:
        return 10
    
    def update(self, world: World, world_entity: Entity):
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Time: {timestamp} | System: {type(self).__name__} | Priority: {self.priority}")
```

### 添加断点

```python
# 使用 breakpoint() 替代 pdb
import pdb
pdb.set_trace()  # 推荐：自动加载本地环境
breakpoint()  # 推荐：Python 3.7+
```

### 添加调试标志

```python
class DebugMode:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def debug(self, msg: str):
        """快速打印调试信息"""
        if debug_mode.verbose:
            print(f"[DEBUG] {msg}")
```

---

## 🧩 贡献流程

### 贡献指南

**步骤**：
1. Fork 项目仓库
2. 创建功能分支 `feature/xxx`
3. 开发新功能
4. 添加测试覆盖
5. 提交 PR
6. 等待审查

**PR 要求**：
- ✅ 添加文档说明
- ✅ 更新 CHANGELOG.md
- ✅ 添加测试覆盖 ≥ 80%
- ✅ 遵循代码风格（PEP 8）
- ✅ 添加迁移指南（如需要）

---

## 🌱 植物/生物学系统开发

### 添加新植物物种

在 `plant/plant_factory.py` 的 `SPECIES_CONFIG` 中添加新预设：

```python
SPECIES_CONFIG = {
    # ... 现有预设
    "my_species": {
        # 光合维度
        "max_photosynthesis_rate": 25.0,   # 最大光合速率 (μmol CO₂/m²/s)
        "light_use_efficiency": 0.6,       # 光照利用效率 (0~1)
        "shade_tolerance": 0.3,            # 耐阴性 (0~1+，越高越耐阴)

        # 温度维度
        "optimal_temp": 25.0,              # 最适光合温度 (°C)
        "cold_tolerance": 5.0,             # 低温耐受阈值 (°C)
        "heat_tolerance": 38.0,            # 高温耐受阈值 (°C)

        # 水分维度
        "water_use_efficiency": 0.4,       # 水分利用效率 (0~1+)

        # 代谢维度
        "metabolism_rate": 0.08,           # 基础呼吸速率
        "growth_partition": 0.6,           # 生长/维持分配比 (0~1)

        # 形态维度
        "leaf_bias": 0.4,                  # 叶分配比 (0~1)
        "root_bias": 0.35,                 # 根分配比 (0~1)
        "stem_bias": 0.25,                 # 茎分配比 (0~1)
        "max_height": 3.0,                 # 最大株高 (m)
        "stem_thickness_factor": 0.02,     # 茎粗因子

        # 繁殖维度
        "seed_production": 40,             # 种子产量倍率
        "dispersal_radius": 5,             # 扩散半径 (网格格数)
    },
}
```

**设计原则**：
- 所有基因提供合理默认值，避免零值导致系统崩溃
- 光合、形态、繁殖三个维度保持内在一致性（如树 → 矮生长分配 + 高茎分配）
- 极端物种（如沙漠仙人掌）的基因配置应反映真实生物学约束

### 使用遗传与变异

#### 从亲本创建子代

```python
from plant.plant_factory import PlantFactory
from biology.components.genome_component import GenomeComponent

# 获取亲本基因组
parent_genome = world.get_component(parent_entity, GenomeComponent)

# 创建子代（自动继承+变异）
child_id = PlantFactory.create_plant_from_genome(
    world, parent_genome, x=35, y=55
)
```

#### 手动操作基因

```python
# 复制基因组
new_genome = parent_genome.copy()

# 触发变异（对每个基因以概率 ±20%）
new_genome.mutate()

# 有性繁殖（预留）
offspring_genome = parent_genome.crossover(another_genome)
```

#### 查询基因

```python
from biology.components.genome_component import GenomeComponent

genome = world.get_component(entity_id, GenomeComponent)
for gene in genome.genes:
    print(f"{gene.name}: strength={gene.strength:.4f}, mutation_rate={gene.mutation_rate}")
```

### 生命周期系统详解

生命周期由 `life_cycle_system.py` 驱动，使用 GDD + 年龄双维度：

#### GDD 计算

```python
# 每个时间步累积
effective_temp = max(0, air_temperature - BASE_TEMPERATURE)  # BASE_TEMPERATURE = 5°C
accumulated_gdd += effective_temp / 24  # 小时折算到天
```

#### 阶段阈值

| 阶段转换 | GDD 阈值 | 额外条件 |
|---------|---------|---------|
| SEED → SPROUT | ≥ 50 + random(-10, 10) | 无 |
| SPROUT → VEGETATIVE | ≥ 150 + random(-20, 20) | 无 |
| VEGETATIVE → MATURE | ≥ 400 + random(-30, 30) | 无 |
| MATURE → SENESCENCE | ≥ 800 或 年龄 > 寿命×0.7 | GDD 优先 |
| SENESCENCE → DEAD | 年龄 > 寿命×1.5 或 biomass ≤ 0 | 触发 DeathSystem |

#### 系统执行顺序（生物学管线）

```
LifeCycleSystem  →  推进 GDD 累积 + 阶段转换
    ↓
GrowthSystem     →  光合产出 (基因×环境因子) → 呼吸消耗 → biomass 净增长
    ↓
MorphologySystem →  biomass → 身高/茎粗/冠幅
    ↓
ReproductionSystem →  MATURE 阶段按种子产量生成子代
    ↓
SenescenceSystem →  SENESCENCE 阶段逐步降低光合效率
    ↓
DeathSystem      →  检测 DEAD 阶段或 biomass ≤ 0 → 移除实体
```

### 生物学 System 优先级建议

| 系统 | 推荐优先级 | 理由 |
|------|-----------|------|
| LifeCycleSystem | 20 | 先推进生命周期，后续系统依赖阶段信息 |
| GrowthSystem | 25 | 光合产出是所有后续过程的基础 |
| MorphologySystem | 30 | 依赖 biomass 数据 |
| ReproductionSystem | 35 | 仅在 MATURE 阶段运行 |
| SenescenceSystem | 40 | 仅在 SENESCENCE 阶段运行 |
| MutationSystem | 45 | 基因变异（可运行于任何阶段） |
| DeathSystem | 50 | 最后检查，移除符合条件的实体 |

### 扩展生物学系统

#### 添加新基因

三步集成新基因：

1. **GenomeComponent** — 在 `genes` 默认列表中添加新 `Gene`
2. **物种预设** — 在 `SPECIES_CONFIG` 中添加该基因的值
3. **目标 System** — 在对应 System 中读取并使用基因

```python
# Step 1: biology/components/genome_component.py
from biology.genetics.gene import Gene

class GenomeComponent(Component):
    genes: List[Gene] = field(default_factory=lambda: [
        Gene("max_photosynthesis_rate", 25.0),
        Gene("my_new_gene", 0.5),  # 新增
        # ... 其他基因
    ])

# Step 3: 在目标 System 中读取
def update(self, world, dt):
    for eid, genome in world.get_components(GenomeComponent):
        my_gene = genome.get_gene("my_new_gene")
        # 使用 gene.strength
```

---

## 🐾 动物模块开发

### 添加新动物物种预设

在 `animal/animal_factory.py` 的 `SPECIES_CONFIG` 中添加：

```python
ANIMAL_SPECIES = {
    "basic": {
        "name": "Basic Animal",
        "max_health": 100.0,
        "speed": 1.0,
        "metabolism": 0.5,
        "strength": 1.0,
        "defense": 1.0,
    },
    "my_animal": {
        "name": "My Custom Animal",
        "max_health": 150.0,
        "speed": 0.8,
        "metabolism": 0.3,
        "strength": 1.8,
        "defense": 1.5,
    },
}
```

### 创建动物实体

```python
from animal.animal_factory import AnimalFactory

# 创建基础型动物
animal_id = AnimalFactory.create_animal(world, "fast", x=50, y=50)
```

---

- [DESIGN_PATTERNS.md](./DESIGN_PATTERNS.md) - 设计模式
- [PROJECT_PRINCIPLES.md](./PROJECT_PRINCIPLES.md) - 设计原则
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 问题排查
- [environment_improvement_report.md](./environment/environment_improvement_report.md) - 环境改进

---

**最后更新**: 2026 年 5 月 28 日  
**维护者**: ECS Core Team  
**贡献**: 欢迎提交 Issue 和 PR！
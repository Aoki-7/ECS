# ECS 世界模拟系统 🌍

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Simulation Step](https://img.shields.io/badge/step-1hr-blue)

> 基于 **Entity-Component-System (ECS)** 架构的复杂世界模拟系统，实现人类↔️环境↔️生物↔️文明四层深度交互。
>
> **核心理念**：底层只有连续物理量的自然演化，所有离散状态（晴/雨/季节/事件）都是物理量的实时视图。

---

## 📋 目录

- [快速开始](#快速开始)
- [项目架构](#项目架构)
- [核心特性](#核心特性)
- [模拟流程](#模拟流程)
- [模块导航](#模块导航)
- [开发者指南](#开发者指南)
- [API 参考](#api-参考)
- [设计原则](#设计原则)
- [性能优化](#性能优化)
- [常见问题](#常见问题)
- [许可证](#许可证)

---

## 🚀 快速开始

### 环境要求

```bash
Python 3.10+
```

### 运行模拟

```bash
python main.py
```

**默认配置**：
- 模拟步数：300 步
- 每步时间：1 小时
- 总时长：约 12.5 天
- 输出：人口统计、资源分布、文明阶段、生物群落状态等信息

### 命令行参数

```bash
python main.py --help

可选参数:
  -s, --steps INT      模拟步数 (默认：300)
  -o, --output str     输出日志文件路径
  -v, --verbose        详细日志模式
  --seed INT           随机种子 (默认：None)
```

---

## 🏗️ 项目架构

### ECS 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      World (世界实例)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Entity (实体)                        │  │
│  │  ┌───────────────────────────────────────────────────┐ │  │
│  │  │          Component (组件 - 纯数据)                  │ │  │
│  │  │  - SpaceComponent  │ Position │ Velocity           │ │  │
│  │  │  - HumanComponent  │ Physiology │ Inventory        │ │  │
│  │  │  - EnvironmentComponent │ Weather │ Climate        │ │  │
│  │  │  - LifeCycleComponent    │ GenomeComponent         │ │  │
│  │  │  - EnergyComponent       │ MorphologyComponent    │ │  │
│  │  └───────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
│                     ↓ System 绑定关系                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  System (系统 - 纯逻辑)                 │  │
│  │  - PhysicalWeatherSystem     (天气物理演化)            │  │
│  │  - LifeCycleSystem           (生命周期推进)            │  │
│  │  - GrowthSystem              (光合/呼吸/环境响应)      │  │
│  │  - SenescenceSystem          (衰老降解)                │  │
│  │  - ReproductionSystem        (繁殖/遗传/变异)          │  │
│  │  - MutationSystem            (基因突变)                │  │
│  │  - MovementSystem            (移动执行)                │  │
│  │  - IntentSystem              (意图管理)                │  │
│  │  - EnvironmentSyncSystem     (环境同步)                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⭐ 核心特性

### 1. 纯物理驱动天气系统 🔬

- **连续物理量演化**：温度、气压、湿度等均为连续物理量，非离散状态
- **实时计算的天文季节**：基于太阳赤纬角和日地距离，无固定季节枚举
- **OU 随机过程气候模型**：长期趋势由 Ornstein-Uhlenbeck 过程驱动
- **统计异常检测**：滑动窗口（720 样本≈30 天）实时检测物理偏离，无预定义事件类型

```
物理演化链路：
太阳位置 → 大气顶辐射 → 连续天气物理量 → 地表光照 → 环境同步
                                              ↓
                                      统计异常检测（无硬编码事件）
```

### 2. 植物全生命周期模拟 🌱

- **五阶段生命周期**：种子 → 发芽 → 营养生长 → 成熟 → 衰老 → 死亡，由 GDD（有效积温）和年龄双维度推进
- **16 维基因体系**：涵盖光合效率、温度耐受、水分利用、代谢速率、形态比例、繁殖策略等维度
- **9 种物种预设**：从阳性先锋种到耐阴、耐旱、水生、肉质植物，各具独特基因配置
- **遗传与变异**：子代通过深度复制继承亲本基因组，每次繁殖以概率引入 ±20% 变异
- **环境交互反馈**：光合速率受光照、温度、水分协同调控，物种性状决定其在各环境下的适应性
- **衰老与凋亡**：成熟后逐步降解光合效率、黄化枯萎，最终进入死亡阶段释放养分

```
植物生命周期链路：
GDD积累 → 阶段推进 → 光合产出 → 形态生长 → 成熟繁殖 → 衰老死亡
                  ↑                        ↓
            环境反馈 (光照/温度/水分)    子代遗传+变异
```

### 3. 动物模块 🐾

- **通用 ECS 架构**：仿照植物模块设计，支持多种动物物种预设（basic / fast / tank）
- **工厂模式创建**：通过 `animal_factory.py` 统一管理实体创建和组件组装
- **预设系统**：当前支持基础型、敏捷型、坚韧型三种动物配置
- **扩展预留**：未来可集成生物学系统中的基因、生长、生命周期等组件

### 4. ECS 架构优势 ⚡

✅ **数据与逻辑分离**：Component 只存储数据，System 只处理逻辑  \
✅ **高内聚低耦合**：每个 System 只处理单一职责  \
✅ **优先级调度**：System 通过 priority 参数控制执行顺序  \
✅ **双向索引**：World 提供 Entity ↔ Component ↔ System 的快速查询

### 5. 模块化管线设计 📦

**环境系统（15 子系统 DAG）**：
```
Layer 1: 外部强迫 → Layer 2: 大气物理 → Layer 3: 辐射传输
    ↓                                                 ↓
Layer 4: 异常检测 + 地表层 → Layer 5: 空间平滑
```

**人类行为流水线**：
```
感知 → 情绪 → 思维 → 目标 → 意图 → 决策 → 规划 → 执行 → 反馈
```

**植物生命周期流水线**：
```
LifeCycle → Growth → Morphology → Senescence → Death
                  ↕
      Mutation ← Reproduction ← Genome
```

### 6. 深度交互系统 🔄

| 交互类型 | 说明 |
|---------|------|
| **人类↔️环境** | 人类受环境影响（温度/湿度影响生理），同时改变环境（资源消耗/废弃） |
| **人类↔️生物** | 采集植物/动物作为食物，受生物生命周期约束 |
| **植物↔️环境** | 光合速率受光照/温度/水分调控，物种适应性决定分布范围 |
| **植物→土壤** | 衰老死亡后释放有机质，影响土壤养分循环 |
| **文明↔️环境** | 文明阶段演化受资源可用性驱动 |

---

## 🎬 模拟流程

### 单步执行顺序（每 1 小时）

```
┌────────────────────────────────────────────────────────────────┐
│ 步骤       系统                          职责                    │
├────────────────────────────────────────────────────────────────┤
│ 0          SpaceSystem                    同步 dirty 位置到索引  │
│ ──────────────────────────────────────────────────────────────│
│ 1          TimeSystem                     推进时间             │
│ ──────────────────────────────────────────────────────────────│
│ 2-8       环境管线 (15 子系统 DAG)          环境物理演化         │
│ ──────────────────────────────────────────────────────────────│
│ 9-16      人类行为流水线                   人类决策与行动       │
│ ──────────────────────────────────────────────────────────────│
│ 17         LifeCycleSystem                GDD → 阶段推进       │
│ 18         GrowthSystem                   光合/呼吸/环境响应    │
│ 19         MorphologySystem              生长形态调整          │
│ 20         ReproductionSystem            繁殖/遗传/变异        │
│ 21         SenescenceSystem              衰老降解              │
│ 22         DeathSystem                   死亡判定              │
│ 23         生理/文明系统                  状态更新              │
│ 24         规则系统                       条件变换              │
│ 25         资源再生                       资源补充              │
└────────────────────────────────────────────────────────────────┘
```

### 人类行为决策流程

```
需求评估 → 意图生成 (紧急度排序) → 任务规划 → 动作调度 → 执行反馈

紧急度示例:
  DRINK: thirst < 20 → 权重 1.3 (口渴) / 1.0 (正常)
  EAT:    hunger < 20 → 权重 1.2 (饥饿) / 1.0 (正常)
  SLEEP:  energy < 40 → 权重 1.3 (疲劳) / 1.0 (正常)
  SOCIALIZE: social < 20 → 权重 0.8 (孤独) / 1.5 (正常)
```

---

## 🗂️ 模块导航

### 核心层 (Core)

| 文件 | 作用 |
|------|------|
| [`core/entity.py`](core/entity.py) | Entity: 自增 ID + 代际管理（防悬挂引用） |
| [`core/component.py`](core/component.py) | Component: dataclass 数据基类 |
| [`core/system.py`](core/system.py) | System: 逻辑基类，优先级继承 |
| [`core/world.py`](core/world.py) | World: Entity/Component/System 双向索引中心 |
| [`core/category.py`](core/category.py) | Category: 分类枚举体系 |

### 环境系统

| 目录 | 说明 |
|------|------|
| `environment/` | 环境系统根目录 |
| `environment/config/environment_builder.py` | 构建 15 子系统 DAG 管线 |
| `environment/physics_weather/systems/physical_weather_system.py` | 核心天气物理演化 |
| `environment/season/season_state.py` | 天文季节计算 |
| `environment/climate/climate_system.py` | OU 过程气候系统 |
| `environment/physics_weather/systems/weather_event_system.py` | 统计异常检测 |

### 人类系统

| 目录 | 说明 |
|------|------|
| `human/components/` | 人类组件层 |
| `human/systems/core/` | 行为核心流水线 |
| `human/systems/cognitive/` | 认知层 (情绪/思维/目标/决策) |
| `human/systems/action/` | 动作执行层 |
| `human/systems/physiological/` | 生理层 |
| `human/systems/social/` | 社交层 |

### 生物学系统

| 目录/文件 | 说明 |
|-----------|------|
| `biology/components/` | **生物通用组件** |
| `biology/components/genome_component.py` | 基因组：16 维基因 + copy/mutate/crossover 方法 |
| `biology/components/life_cycle_component.py` | 生命周期阶段：SEED→SPROUT→VEGETATIVE→MATURE→SENESCENCE→DEAD |
| `biology/components/energy_component.py` | 能量储量组件 |
| `biology/components/morphology_component.py` | 形态表现型组件 |
| `biology/systems/` | **生物通用系统** |
| `biology/systems/life_cycle_system.py` | 生命周期推进：GDD + 年龄双维度 |
| `biology/systems/growth_system.py` | 光合/呼吸/生长：读取 16 维基因响应环境 |
| `biology/systems/morphology_system.py` | 形态生长：身高/茎粗/冠幅因子 |
| `biology/systems/reproduction_system.py` | 繁殖系统：遗传 + 变异 + 空间分布 |
| `biology/systems/senescence_system.py` | 衰老系统：光合效率退化、黄化枯萎 |
| `biology/systems/mutation_system.py` | 基因变异系统：随机漂变 |
| `biology/systems/death_system.py` | 死亡判定系统 |
| `biology/systems/gene_expression_system.py` | 基因表达：基因→表现型映射 |

### 植物模块

| 文件 | 说明 |
|------|------|
| `plant/plant_factory.py` | 植物实体工厂：9 种物种预设 + 基因继承创建 |
| `plant/__init__.py` | 模块入口 |

**9 种物种预设：**

| 预设 | 特点 | 典型环境 |
|------|------|----------|
| `basic` | 通用植物，各项均衡 | 一般陆地 |
| `fast` | 快速生长，早熟多产，短寿命 | 扰动环境 |
| `tree` | 高大长寿，晚熟，少种子 | 稳定森林 |
| `cold_resistant` | 耐低温，高冷耐受 | 高纬度/高海拔 |
| `drought_resistant` | 深根高水分利用效率 | 干旱/半干旱 |
| `succulent` | 肉质储水，超高水效 | 沙漠 |
| `aquatic` | 喜水耐阴，低水效 | 水域/湿地 |
| `shade_tolerant` | 极高耐阴性 | 林下 |
| `pioneer` | 阳性种，高光效低耐阴 | 裸地/灾后 |

**16 维基因体系：**

| 基因 | 类型 | 说明 |
|------|------|------|
| `max_photosynthesis_rate` | 光合 | 最大光合速率上限 |
| `light_use_efficiency` | 光合 | 光照利用效率 |
| `shade_tolerance` | 光合 | 耐阴性，低光补偿 |
| `optimal_temp` | 温度 | 最适光合温度 |
| `cold_tolerance` | 温度 | 低温耐受阈值 |
| `heat_tolerance` | 温度 | 高温耐受阈值 |
| `water_use_efficiency` | 水分 | 水分利用效率 (WUE) |
| `metabolism_rate` | 代谢 | 基础代谢速率 |
| `growth_partition` | 代谢 | 生长/维持分配比 |
| `leaf_bias` | 形态 | 叶生物量分配比 |
| `root_bias` | 形态 | 根生物量分配比 |
| `stem_bias` | 形态 | 茎生物量分配比 |
| `max_height` | 形态 | 最大株高 |
| `stem_thickness_factor` | 形态 | 茎粗因子 |
| `seed_production` | 繁殖 | 单次种子产量倍率 |
| `dispersal_radius` | 繁殖 | 种子扩散半径 |

### 动物模块

| 文件 | 说明 |
|------|------|
| `animal/animal_factory.py` | 动物实体工厂：3 种物种预设 |
| `animal/__init__.py` | 模块入口 |

**3 种物种预设：**

| 预设 | 特点 | 应用场景 |
|------|------|----------|
| `basic` | 基础型，各项均衡 | 通用动物模型 |
| `fast` | 高敏捷，高代谢，短寿命 | 小型掠食者/食草动物 |
| `tank` | 高防御，高耐力，慢速 | 大型动物/防御型 |

### 空间系统

| 文件 | 作用 |
|------|------|
| [`space/space_component.py`](space/space_component.py) | 空间数据：x, y, layer, dirty |
| [`space/space_system.py`](space/space_system.py) | 空间索引管理，范围查询 |
| [`space/spatial_index.py`](space/spatial_index.py) | 稀疏网格索引（字典→集合） |

### 时间系统

| 文件 | 作用 |
|------|------|
| [`time_module/time_system.py`](time_module/time_system.py) | 年/日/时推进，时间倍率 |
| [`time_module/time_component.py`](time_module/time_component.py) | 时间数据载体 |

### 资源系统

| 目录 | 说明 |
|------|------|
| `resource/food/` | 食物系统 |
| `resource/water/` | 水源系统 |
| `resource/components/` | 资源通用组件 |

### 文明系统

| 目录 | 说明 |
|------|------|
| `civilization/systems/` | 文明子系统 (阶段检测/建筑/资源采集/技术/贸易) |

### 规则系统

| 文件 | 作用 |
|------|------|
| `rules/transformation_system.py` | 条件变换引擎 |
| `rules/transformation_rule.py` | 规则定义 |
| `rules/rules_config.py` | 预设规则集 |

---

## 👨‍💻 开发者指南

### 添加新系统（三步完成）

#### Step 1: 创建 System 类

```python
from core.system import System
from core.component import Component
from core.world import World

class MyNewSystem(System):
    """我的新系统"""

    @property
    def priority(self) -> int:
        return 10  # 执行优先级

    def update(self, world: World, delta_hours: float):
        """系统更新逻辑"""
        # 获取所有包含 MyComponent 的实体
        entities_with_my_component = world.get_components(MyComponent)

        for entity_id, component in entities_with_my_component:
            # 处理逻辑
            component.some_property += delta_hours
```

#### Step 2: 注册系统

在 `main.py` 中注册:

```python
from my_new_system_module import MyNewSystem

world.register_system(MyNewSystem, priority=10)
```

#### Step 3: 创建新 Component（如需要）

```python
from dataclasses import dataclass
from core.component import Component

@dataclass
class MyDataComponent(Component):
    some_property: float = 0.0
    another_value: int = 0
```

添加到 World 的组件列表中:

```python
world_entity.add_component(MyDataComponent)
```

### 添加新植物物种

```python
from plant.plant_factory import PlantFactory

# 在 plant_factory.py 的 SPECIES_CONFIG 中添加新预设
SPECIES_CONFIG = {
    "my_species": {
        "max_photosynthesis_rate": 25.0,
        "optimal_temp": 28.0,
        "cold_tolerance": 5.0,
        "heat_tolerance": 38.0,
        "water_use_efficiency": 0.6,
        # ... 其他 12 个基因参数
    }
}

# 使用
plant_id = PlantFactory.create_plant(world, "my_species", x=50, y=50)
```

### 添加新动物物种

```python
from animal.animal_factory import AnimalFactory

# 在 animal_factory.py 的 SPECIES_CONFIG 中添加新预设
animal_id = AnimalFactory.create_animal(world, "basic", x=50, y=50)
```

### 扩展决策系统

在 `human/systems/core/decision_system.py` 中添加新权重:

```python
def calculate_intent_weights(human_component, physiology_needs_component):
    base_weights = {
        ActionType.EAT: {
            "hunger_dependent": 1.2 if humanity.hunger < 20 else 1.0,
            "normal": 1.0
        },
        # ... 其他动作
    }
    return calculate_composite_weights(base_weights, human_component)
```

---

## 📚 API 参考

### World 核心 API

#### 实体管理

```python
# 创建实体
entity = world.create_entity()
print(f"Entity ID: {entity.id}")

# 查询实体
entity = world.query_entity(entity_id)

# 删除实体
world.remove_entity(entity)
```

#### 组件管理

```python
# 添加组件
from core.component import MyComponent
world.add_component(entity, MyComponent(value=10))

# 获取组件
components = world.get_components(MyComponent)
for eid, comp in components:
    print(f"Entity {eid}: {comp.value}")

# 移除组件
world.remove_component(entity, MyComponent)
```

#### 系统管理

```python
# 获取系统实例
system = world.get_system(MySystem)

# 注册系统
world.register_system(MySystem(priority=10))
```

### 环境系统 API

#### 物理天气

```python
from environment.physics_weather.components import PhysicalWeatherComponent

# 获取物理天气
weather = world.get_world_component(PhysicalWeatherComponent)
print(f"温度：{weather.temperature:.1f}°C")
print(f"相对湿度：{weather.relative_humidity:.1f}%")
print(f"云量：{weather.cloud_cover:.1f}")
print(f"风速：{weather.wind_speed:.1f} km/h")
```

#### 空间查询

```python
from space.space_system import SpaceSystem

space_system = world.get_system(SpaceSystem)
# 查询半径 r 范围内的实体 ID
entities_in_radius = space_system.query_radius(x=50, y=50, r=10)
print(f"范围内实体数：{len(entities_in_radius)}")
```

#### 时间查询

```python
from time_module.time_component import TimeComponent

time = world.get_world_component(TimeComponent)
print(f"当前时间：第 {time.day_of_year} 天, {time.hour} 时")
```

### 人类系统 API

#### 人类组件

```python
from human.components import HumanComponent, PhysiologyNeedsComponent

# 获取人类实体
humans = world.get_components(HumanComponent)
for eid, human in humans:
    print(f"年龄：{human.age} 性别：{human.gender}")
    print(f"饥饿：{human.hunger:.1f} 口渴：{human.thirst:.1f}")
    print(f"能量：{human.energy:.1f} 疲劳：{human.fatigue:.1f}")
```

### 植物系统 API

#### 创建植物

```python
from plant.plant_factory import PlantFactory

# 创建快速生长植物
plant_id = PlantFactory.create_plant(world, "fast", x=30, y=50)

# 从亲本基因创建子代（遗传+变异）
from biology.components.genome_component import GenomeComponent
parent_genome = world.get_component(parent_entity, GenomeComponent)
child_id = PlantFactory.create_plant_from_genome(world, parent_genome, x=35, y=55)
```

#### 查询植物生命周期

```python
from biology.components.life_cycle_component import LifeCycleComponent

for eid, lc in world.get_components(LifeCycleComponent):
    print(f"实体 {eid}: 阶段={lc.stage.name}, GDD={lc.accumulated_gdd:.1f}, 年龄={lc.age_hours:.0f}h")
```

#### 查询基因组

```python
from biology.components.genome_component import GenomeComponent

for eid, genome in world.get_components(GenomeComponent):
    for gene in genome.genes:
        print(f"  {gene.name}: {gene.strength:.4f}")
```

---

## 🎯 设计原则

### 1. 数据与逻辑分离

- **Component**：只存储数据，不持有任何逻辑
- **System**：只处理逻辑，不存储状态数据
- **Entity**：作为数据与逻辑的绑定载体

### 2. 单一职责原则

- 每个 System 只处理单一职责
- 每个 Component 只描述单一维度

### 3. 优先使用双向索引

```python
# ❌ 低效：遍历实体找组件
for entity in world.all_entities:
    component = entity.get_component(MyComponent)

# ✅ 高效：World 提供快速查询
components = world.get_components(MyComponent)
```

### 4. 避免状态爆炸

- 使用连续物理量而非离散状态
- 使用实时视图而非硬编码状态机
- 使用统计检测而非固定阈值

### 5. 模块化管线

- ECS 架构天然支持模块化
- 通过 priority 控制执行顺序
- 通过 world_entity 实现全局共享数据同步

### 6. 生物学模拟：连续演化 + 遗传变异

- 生命周期通过连续物理量（GDD）驱动，非硬编码阶段切换
- 基因型决定表现型，表现型与环境交互决定适应度
- 遗传传递 + 随机变异 = 群体演化
- 衰老退化是渐进的连续过程，非瞬间状态

---

## 🚀 性能优化

### 1. 空间索引优化

```python
# SpaceSystem 自动维护稀疏网格索引
# 查询使用 O(log n) 而非 O(n)
entities = space_system.query_radius(x, y, r)
```

### 2. 批次操作

```python
# ✅ 推荐：批量添加组件
entities = world.get_components(SpaceComponent)
for e_id, _ in entities:
    world.add_component(e_id, MyComponent())

# ❌ 避免：逐个添加（可能触发多次内存分配）
for e_id, _ in entities:
    world.add_component(e_id, MyComponent())
```

### 3. 优先查询 World 索引

```python
# World 维护了 Entity→Component→System 的索引
# 优先使用 get_components/get_system 而非手动遍历
```

### 4. 避免在 update 中创建对象

```python
# ❌ 每次 update 都创建新对象
def update(self, world, dt):
    new_entity = world.create_entity()
    ...

# ✅ 预分配对象池
world_entity_object = None

def update(self, world, dt):
    global world_entity_object
    if world_entity_object is None:
        world_entity_object = MyComponent()
    ...
```

---

## ❓ 常见问题

### Q1: 为什么天气是连续的而非离散的？

**A**: 连续物理量能更好地模拟真实世界演化，离散状态会丢失中间态信息。例如温度从 20°C 降到 0°C 的过程中，系统记录了完整的下降轨迹，而非直接跳到雪天。

### Q2: 植物生命周期怎么工作的？

**A**: 采用"有效积温(GDD) + 年龄"双维度推进。GDD 模拟真实植物对温度的累积响应（每天气温度日积温），年龄作为兜底保证即使在极端低温下也能推进。种子需累积足够 GDD 才能发芽，成熟后自动进入繁殖期，衰老期光合效率逐步下降。

### Q3: 遗传和变异是怎么实现的？

**A**: 子代通过 `genome.copy()` 深度复制亲本 16 维基因数组，然后对每个基因以 `mutation_rate` 概率触发变异，变异幅度为原始值的 ±20%。这意味着子代继承亲本的整体策略，但每次繁殖都会引入微小的随机漂变，多代积累后产生基因型多样性。

### Q4: 如何添加新的事件类型？

**A**: 目前使用统计异常检测替代硬编码事件。如需特定事件，可通过调整物理阈值触发：

```python
# 在 environment/config/weather_thresholds.py 中调整
PRECIPITATION_HIGH_THRESHOLD = 5.0  # mm/h
```

### Q5: 如何重置世界状态？

**A**: 创建新的 World 实例:

```python
from core.world import World

world = World()
world.create_all_systems()
world_entity = world.create_entity()
# ... 初始化世界
```

### Q6: 人类为什么会重复执行同一动作？

**A**: 这是设计行为——人类有行为模式。如需修复：

```python
# 在 BrainComponent 中添加行为历史
class BrainComponent:
    def __init__(self):
        self.thought_history: List[str] = []
        self.action_history: List[tuple[ActionType, datetime]] = []
```

### Q7: 如何调试系统顺序？

**A**: 在 System 中打印优先级：

```python
class DebugSystem(System):
    @property
    def priority(self) -> int:
        return 10

    def update(self, world, dt):
        print(f"[{type(self).__name__}] Priority={self.priority} | Timestamp={world.time.hour}")
```

---

## 📄 许可证

本项目采用 **MIT License**。

```
MIT License

Copyright (c) 2026 ECS World Simulation Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 📖 相关文档

- [**architecture.md**](./architecture.md) - 完整架构说明
- [**DEVELOPER_GUIDE.md**](./DEVELOPER_GUIDE.md) - 详细开发指南
- [**DESIGN_PATTERNS.md**](./DESIGN_PATTERNS.md) - 设计模式文档
- [**TROUBLESHOOTING.md**](./TROUBLESHOOTING.md) - 问题排查指南
- [**DESIGN_SUMMARY.md**](./DESIGN_SUMMARY.md) - 设计总结报告
- [**PROJECT_PRINCIPLES.md**](./PROJECT_PRINCIPLES.md) - 设计原则
- [**environment_improvement_report.md**](./environment/environment_improvement_report.md) - 环境模块改进报告

---

**最后更新**: 2026 年 5 月 28 日

**开发团队**: ECS World Simulation Team

**贡献**: 欢迎提交 Issue 和 PR！

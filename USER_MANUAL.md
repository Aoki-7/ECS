# ECS 世界模拟系统 — 使用说明

> **版本**: v3.0  
> **适用对象**: 开发者、模拟设计师、研究人员  
> **最后更新**: 2026-06-08

---

## 目录

1. [快速开始](#一快速开始)
2. [核心概念](#二核心概念)
3. [创建世界](#三创建世界)
4. [实体操作](#四实体操作)
5. [组件系统](#五组件系统)
6. [系统调度](#六系统调度)
7. [事件总线](#七事件总线)
8. [统一记忆层](#八统一记忆层)
9. [存档读档](#九存档读档)
10. [可视化](#十可视化)
11. [性能优化](#十一性能优化)
12. [常见问题](#十二常见问题)

---

## 一、快速开始

### 1.1 环境要求

- Python 3.10+
- 无外部依赖（纯标准库）

### 1.2 最小示例

```python
from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent

# 1. 创建世界
world = World()

# 2. 创建实体
entity = world.create_entity()

# 3. 添加组件
world.add_component(entity, SpaceComponent(x=10, y=20))

# 4. 运行一帧
world.update(dt=1.0)

print(f"世界有 {len(world.entities)} 个实体")
```

### 1.3 运行测试

```bash
cd D:\个人助手\workspace\ECS
python -m pytest -x --tb=short
```

---

## 二、核心概念

### 2.1 ECS 架构

| 概念 | 说明 | 类比 |
|------|------|------|
| **Entity** | 唯一标识符（ID） | 身份证号 |
| **Component** | 纯数据，无逻辑 | 属性标签 |
| **System** | 逻辑处理，操作组件 | 处理器 |
| **World** | 统一管理器 | 数据库 |

### 2.2 数据流

```
创建实体 → 挂载组件 → 系统查询 → 更新状态 → 销毁实体
    ↑_________________________________________________↓
```

### 2.3 记忆层模型

```
物理层（Entity） → 客观记忆（Concept） → 主观记忆（MemoryInstance）
     可消亡              永久保留              个性化、可扭曲
```

---

## 三、创建世界

### 3.1 基础创建

```python
from core.world import World

world = World()
```

### 3.2 配置世界实体

```python
from core.entity import Entity
from environment.environment_component import EnvironmentComponent

# 创建世界实体
world_entity = Entity.create()
world.set_world_entity(world_entity)

# 添加环境组件
world_entity.add_component(EnvironmentComponent())
```

### 3.3 主循环

```python
import time

# 模拟 100 帧
for tick in range(100):
    world.update(dt=1.0)
    time.sleep(0.1)  # 控制速度
```

---

## 四、实体操作

### 4.1 创建实体

```python
# 基础创建
entity = world.create_entity()

# 创建时自动触发事件
# → EventBus.publish("entity_created", {"entity_id": entity.id})
```

### 4.2 查询实体

```python
# 通过 ID 查询
entity = world.query_entity(42)

# 检查存在性
if world.has_entity(entity):
    print("实体有效")
```

### 4.3 销毁实体

```python
# 销毁实体（自动清理组件）
world.remove_entity(entity)

# 自动触发事件
# → EventBus.publish("entity_destroyed", {"entity_id": entity.id})
```

### 4.4 调试打印

```python
# 打印单个实体
world.debug_print_entity(entity, verbose=True)

# 打印所有实体
world.debug_print_all_entities()
```

---

## 五、组件系统

### 5.1 添加组件

```python
from space.space_component import SpaceComponent
from animal.components.animal_component import AnimalComponent

# 添加单个组件
world.add_component(entity, SpaceComponent(x=0, y=0))
world.add_component(entity, AnimalComponent(species="wolf", diet="carnivore"))
```

### 5.2 获取组件

```python
# 获取单个组件
space = world.get_component(entity, SpaceComponent)
if space:
    print(f"位置: ({space.x}, {space.y})")

# 批量查询（推荐）
for entity, (animal, space) in world.get_components(
    AnimalComponent, SpaceComponent
):
    print(f"动物 {entity.id} 在 ({space.x}, {space.y})")
```

### 5.3 移除组件

```python
world.remove_component(entity, SpaceComponent)
```

### 5.4 自定义组件

```python
from dataclasses import dataclass
from core.component import Component

@dataclass(slots=True)
class HealthComponent(Component):
    max_hp: float = 100.0
    current_hp: float = 100.0
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def take_damage(self, damage: float) -> None:
        self.current_hp = max(0, self.current_hp - damage)
```

---

## 六、系统调度

### 6.1 添加系统

```python
from core.system import System

class MySystem(System):
    priority = 10        # 优先级（越高越先执行）
    tick_interval = 5    # 每 5 帧执行一次
    
    def update(self, world, dt: float = 1.0) -> None:
        for entity, space in world.get_components(SpaceComponent):
            # 处理逻辑
            pass

world.add_system(MySystem())
```

### 6.2 系统优先级

```python
# 系统按优先级自动排序
# 负数 = 高优先级（先执行）
# 正数 = 低优先级（后执行）

class InputSystem(System):
    priority = -100   # 最先执行

class RenderSystem(System):
    priority = 100    # 最后执行
```

### 6.3 禁用系统

```python
system = world.get_system(MySystem)
if system:
    system.enabled = False  # 禁用
```

---

## 七、事件总线

### 7.1 订阅事件

```python
from core.event_bus import EventBus

bus = EventBus.get_instance()

def on_entity_created(event):
    print(f"实体 {event.payload['entity_id']} 已创建")

# 订阅
bus.subscribe("entity_created", on_entity_created)

# 带优先级订阅
bus.subscribe("entity_created", on_entity_created, priority=10)

# 一次性订阅
bus.subscribe("entity_created", on_entity_created, once=True)

# 条件订阅
bus.subscribe(
    "entity_created",
    on_entity_created,
    filter_fn=lambda e: e.payload.get("type") == "human"
)
```

### 7.2 发布事件

```python
# 手动发布事件
bus.publish(
    "custom_event",
    {"key": "value"},
    source="my_system",
    priority=5
)
```

### 7.3 取消订阅

```python
bus.unsubscribe("entity_created", on_entity_created)
```

### 7.4 查看历史

```python
# 获取最近 100 个事件
history = bus.get_history(limit=100)

# 获取特定类型事件
entity_events = bus.get_history("entity_created", limit=50)
```

---

## 八、统一记忆层

### 8.1 基本概念

| 概念 | 说明 |
|------|------|
| **Concept** | 客观记忆（实体消亡后仍存在） |
| **MemoryInstance** | 主观记忆（某主体对概念的记忆） |
| **ContactRecord** | 接触记录（主体与实体的交互） |
| **SensoryDescription** | 结构化感官描述（7 字段） |

### 8.2 注册实体到记忆层

```python
from memory_layer import MemoryLayer, SensoryDescription

ml = MemoryLayer.get_instance()

# 注册实体
concept = ml.register_entity(
    entity_id=42,
    entity_type="stone",
    description=SensoryDescription(
        shape="圆形",
        color="灰色",
        texture="光滑",
        size="中等",
    ),
)
```

### 8.3 记录接触

```python
from memory_layer import SubjectType

ml.record_contact(
    subject_id=1,              # 观察者 ID
    subject_type=SubjectType.ANIMAL,
    entity_id=42,              # 被观察实体 ID
    contact_type="visual",     # 接触类型
    intensity=0.8,             # 强度 0~1
    attention_level=0.9,       # 注意力 0~1
    context="在河边发现",
)
```

### 8.4 回忆记忆

```python
# 主体回忆某概念
memory = ml.recall_memory(subject_id=1, concept_id="entity_42_stone")

if memory:
    print(f"确信度: {memory.confidence}")
    print(f"感官印象: {memory.sensory_impression.to_text()}")
```

### 8.5 叙述传播

```python
# 主体 A 向主体 B 叙述记忆
new_memory = ml.narrate_memory(
    from_subject=1,
    to_subject=2,
    to_subject_type=SubjectType.ANIMAL,
    concept_id="entity_42_stone",
)

# 新记忆的确信度更低，可能有扭曲
if new_memory:
    print(f"新确信度: {new_memory.confidence}")  # < 原确信度
```

### 8.6 创建抽象概念

```python
# 创建无实体来源的概念（神话、传说等）
ml.create_abstract_concept(
    name="龙",
    description=SensoryDescription(
        shape="蛇形",
        color="金色",
        size="巨大",
    ),
    concept_type="myth",
)
```

### 8.7 遗忘机制

```python
# 应用遗忘（自然衰减）
forgotten_count = ml.apply_forgetting(
    subject_id=1,      # 可选：指定主体
    decay_rate=0.01,   # 衰减率
)
print(f"遗忘了 {forgotten_count} 个记忆")
```

### 8.8 统计信息

```python
stats = ml.get_stats()
print(f"概念数: {stats['concept_count']}")
print(f"活跃概念: {stats['active_concepts']}")
print(f"记忆数: {stats['memory_count']}")
```

---

## 九、存档读档

### 9.1 统一存档系统

```python
from save_load.unified_save_system import UnifiedSaveSystem

save_system = UnifiedSaveSystem(save_dir="saves")

# 手动存档
save_system.save(world, "slot1")

# 自动存档（每 100 tick）
save_system.update(world, dt=1.0)
```

### 9.2 读档

```python
# 加载存档
success = save_system.load(world, "slot1")
if success:
    print("加载成功")
```

### 9.3 存档管理

```python
# 列出存档
saves = save_system.list_saves()
for save in saves:
    print(f"{save['name']} - {save['save_time']}")

# 删除存档
save_system.delete_save("old_save")
```

### 9.4 存档格式

```json
{
  "version": "2.3",
  "world": { ... },
  "memory_layer": { ... },
  "meta": {
    "save_time": "2026-06-08T12:00:00",
    "tick_count": 1000,
    "entity_count": 500
  }
}
```

---

## 十、可视化

### 10.1 生成可视化报告

```python
from presentation.visualization.world_visualizer import WorldVisualizer

visualizer = WorldVisualizer(world)

# 生成完整报告
report = visualizer.generate_full_report()
```

### 10.2 导出 HTML

```python
# 导出交互式 HTML
filepath = visualizer.export_html("world_visualization.html")
print(f"可视化已导出: {filepath}")
```

### 10.3 单独可视化类型

```python
# 实体分布热力图
heatmap = visualizer.generate_entity_heatmap()

# 系统性能监控
perf = visualizer.generate_system_performance()

# 实体关系网络
network = visualizer.generate_entity_network()

# 记忆网络
memory_net = visualizer.generate_memory_network()

# 事件时间轴
timeline = visualizer.generate_event_timeline(limit=100)
```

---

## 十一、性能优化

### 11.1 使用空间索引

```python
from core.spatial_index import SpatialIndex

# 创建索引
index = SpatialIndex(cell_size=50.0)

# 添加实体
for entity, space in world.get_components(SpaceComponent):
    index.add_entity(entity.id, space.x, space.y)

# 快速查询（比暴力查询快 10x+）
nearby = index.query_radius(100, 100, 50)
```

### 11.2 查询缓存

`World.get_components()` 自动缓存同一 tick 的查询结果，无需手动优化。

### 11.3 系统分频

```python
class SlowSystem(System):
    tick_interval = 10  # 每 10 帧执行一次，减少 CPU 占用
```

### 11.4 组件 slots

```python
@dataclass(slots=True)  # 使用 __slots__ 减少内存占用
class MyComponent(Component):
    value: float = 0.0
```

---

## 十二、常见问题

### Q1: 实体创建后 ID 是多少？

```python
entity = world.create_entity()
print(entity.id)  # 从 0 开始递增
```

### Q2: 如何检查组件是否存在？

```python
comp = world.get_component(entity, SpaceComponent)
if comp is not None:
    # 组件存在
    pass
```

### Q3: 系统执行顺序怎么控制？

```python
# 通过 priority 控制
# 负数 = 先执行，正数 = 后执行
class EarlySystem(System):
    priority = -100

class LateSystem(System):
    priority = 100
```

### Q4: 记忆层数据会无限增长吗？

```python
# 记忆有容量上限和遗忘机制
ml.default_max_memories_per_subject = 100  # 每个主体最多 100 条记忆
ml.apply_forgetting(decay_rate=0.01)       # 定期遗忘
```

### Q5: 如何调试事件？

```python
bus = EventBus.get_instance()

# 查看统计
stats = bus.get_stats()
print(f"发布: {stats['published']}, 投递: {stats['delivered']}")

# 查看历史
history = bus.get_history(limit=10)
for event in history:
    print(f"[{event.timestamp}] {event.event_type}")
```

### Q6: 存档兼容性？

```python
# 存档包含版本号
save_system = UnifiedSaveSystem()
save_system.SAVE_VERSION = "2.3"  # 当前版本

# 加载时检查版本
success = save_system.load(world, "slot1")
# 版本不匹配时会发出警告
```

### Q7: 如何扩展新模块？

```python
# 1. 创建组件
@dataclass(slots=True)
class MyComponent(Component):
    value: float = 0.0

# 2. 创建系统
class MySystem(System):
    priority = 0
    tick_interval = 1
    
    def update(self, world, dt: float = 1.0) -> None:
        for entity, comp in world.get_components(MyComponent):
            comp.value += 1

# 3. 注册到世界
world.add_system(MySystem())
```

---

## 附录

### A. 完整示例：简单生态系统

```python
from core.world import World
from space.space_component import SpaceComponent
from animal.components.animal_component import AnimalComponent
from animal.systems.animal_perception_system import AnimalPerceptionSystem

# 创建世界
world = World()

# 添加系统
world.add_system(AnimalPerceptionSystem())

# 创建动物
wolf = world.create_entity()
world.add_component(wolf, AnimalComponent(species="wolf", diet="carnivore"))
world.add_component(wolf, SpaceComponent(x=0, y=0))

# 创建猎物
rabbit = world.create_entity()
world.add_component(rabbit, AnimalComponent(species="rabbit", diet="herbivore"))
world.add_component(rabbit, SpaceComponent(x=10, y=10))

# 运行模拟
for tick in range(100):
    world.update(dt=1.0)
    print(f"Tick {tick}: {len(world.entities)} 实体")
```

### B. 事件类型参考

| 事件类型 | 触发时机 | 载荷 |
|----------|----------|------|
| `entity_created` | 实体创建时 | `{"entity_id": int}` |
| `entity_destroyed` | 实体销毁时 | `{"entity_id": int, "reason": str}` |
| `component_added` | 组件添加时 | `{"entity_id": int, "component_type": str}` |
| `system_error` | 系统异常时 | `{"system": str, "error": str}` |

### C. 联系与支持

- **项目路径**: `D:\个人助手\workspace\ECS`
- **测试命令**: `python -m pytest -x --tb=short`
- **架构文档**: `ARCHITECTURE.md`
- **发布报告**: `reports/v3.0_release_report.md`

---

> **ECS World Simulation System v3.0**  
> *构建你自己的世界*

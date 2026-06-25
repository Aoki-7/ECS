# Core 模块 — ECS 核心架构

## 概述

`core/` 是 ECS（Entity-Component-System）架构的核心实现层，为整个生态系统模拟提供底层框架支撑。所有上层模块（生物、环境、文明等）均依赖此层。

**版本**: v4.0

---

## 目录结构

```
core/
├── __init__.py              # 包导出与公共接口
├── entity.py                # Entity: 不可变实体标识 (id + generation)
├── component.py             # Component: 纯数据组件基类
├── system.py                # System: 业务逻辑系统基类
├── world.py                 # World: 协调者模式，整合所有管理器
├── entity_manager.py        # EntityManager: 实体生命周期管理
├── archetype_store.py       # ArchetypeStore: Archetype-based 列式组件存储
├── system_scheduler.py      # SystemScheduler: 依赖图解析 + 拓扑排序
├── world_event_bus.py       # WorldEventBus: per-World 事件总线
├── component_serializer.py  # ComponentSerializer: 统一序列化框架
├── query_api.py             # QueryAPI: 声明式查询接口
├── event_bus.py             # EventBus: 全局事件总线（legacy 兼容）
├── spatial_index.py         # SpatialIndex: 均匀网格空间索引
├── performance_monitor.py   # PerformanceMonitor: 性能监控
├── entity_pool.py           # EntityPool: 实体对象池
├── constants.py             # 全局常量
├── cleanup_utils.py         # 大对象清理工具
├── sqrt_cache.py            # 平方根缓存（空间查询优化）
├── components/              # 核心组件
│   └── world_config_component.py
└── systems/                 # 核心系统
    └── world_config_system.py
```

---

## 核心概念

### 1. Entity（实体）

轻量级不可变标识符，由 `id` + `generation` 组成，防止悬挂引用。

```python
from core import Entity

entity = Entity.create()  # 创建实体
print(entity.id)          # 实体 ID
print(entity.generation)  # 代数（用于 ID 回收验证）
```

**不可变性**: Entity 的属性（`id`, `generation`, `metadata`）一旦设置不可重新赋值，但 `metadata`（字典）内部可修改。

### 2. Component（组件）

纯数据类，零业务逻辑。使用 `@dataclass(slots=True)` 实现内存优化。

```python
from core import Component

class HealthComponent(Component):
    max_hp: float = 100.0
    current_hp: float = 100.0
```

### 3. System（系统）

业务逻辑载体，通过重写 `_update()` 方法实现具体逻辑。

```python
from core import System, World

class HealthSystem(System):
    def _update(self, world: World, dt: float = 1.0) -> None:
        # 遍历所有有 HealthComponent 的实体
        for entity, (health,) in world.get_components(HealthComponent):
            if health.current_hp <= 0:
                world.remove_entity(entity)
```

**关键特性**:
- `enabled` 属性控制启用/禁用（基类自动检查）
- `priority` 控制执行顺序（数字越小越先执行）
- `tick_interval` 控制执行频率（1=每帧，2=隔1帧）
- `dependencies_after/before` 声明式依赖（v4.0）

### 4. World（世界）

协调者模式，整合所有管理器，提供统一 API。

```python
from core import World

world = World()

# 实体管理
entity = world.create_entity()
world.remove_entity(entity)

# 组件管理
world.add_component(entity, HealthComponent())
health = world.get_component(entity, HealthComponent)

# 查询
for entity, (health, pos) in world.get_components(HealthComponent, PositionComponent):
    ...

# 系统管理
world.add_system(HealthSystem())
world.update(dt=1.0)  # 执行所有系统
```

---

## v4.0 架构升级

### 新增管理器

| 管理器 | 职责 | 取代的旧实现 |
|--------|------|-------------|
| **EntityManager** | 实体 ID 分配、回收、生命周期 | World 直接管理实体 |
| **ArchetypeStore** | Archetype-based 列式组件存储 | World 直接存储组件字典 |
| **SystemScheduler** | 依赖图解析 + 拓扑排序 | World 直接调度系统 |
| **WorldEventBus** | per-World 事件隔离 | 全局 EventBus |
| **ComponentSerializer** | 统一序列化 + 版本迁移 | 分散的 to_dict/from_dict |

### Archetype 存储

参考 Bevy/Unity DOTS 设计，按组件类型组合分组存储：

- **Archetype**: 组件类型的唯一组合，如 `(Health, Position)`
- **列式存储**: 同类型组件在内存中连续排列，提升缓存友好性
- **自动迁移**: 添加/移除组件时实体自动在 Archetype 间迁移

```python
from core import ArchetypeStore

store = ArchetypeStore()
store.add_component(entity, HealthComponent())
store.add_component(entity, PositionComponent())

# 实体现在位于 Archetype(HealthComponent, PositionComponent)
# 查询直接遍历匹配的 Archetype，无需集合交集
```

---

## 事件系统

### WorldEventBus（推荐）

每个 World 拥有独立的事件总线，避免多 World 事件串扰。

```python
world = World()

# 订阅事件
world.subscribe("entity_created", lambda event: print(f"Created: {event.payload}"))

# 发布事件
world.publish("custom_event", {"data": 123})

# 获取历史
history = world.event_bus.get_history("entity_created")
```

### EventBus（Legacy）

全局单例事件总线，向后兼容。

```python
from core import EventBus

bus = EventBus.get_instance()
bus.subscribe("event_type", handler)
bus.publish("event_type", {"key": "value"})
```

---

## 查询 API

### 基础查询

```python
# 查询单个组件
for entity, (health,) in world.get_components(HealthComponent):
    ...

# 查询多个组件
for entity, (health, pos) in world.get_components(HealthComponent, PositionComponent):
    ...
```

### 声明式查询（v3.7+）

```python
# 注入查询方法后
world.query(HealthComponent, PositionComponent)

# 获取第一个结果
result = world.query_one(HealthComponent)
if result:
    entity, health = result
```

---

## 性能优化

### 1. EntityPool（对象池）

```python
from core import EntityPool

pool = EntityPool.get_instance()
pool.enable()

# 实体创建/销毁自动使用池
entity = Entity.create(pool=pool)
Entity.destroy(entity)  # 自动回收到池中
```

### 2. SqrtCache（距离计算缓存）

```python
from core.sqrt_cache import cached_sqrt, cached_distance

# 缓存常用平方根和距离计算
dist = cached_distance(dx, dy)
```

### 3. 查询缓存

ArchetypeStore 自动缓存查询结果，组件变更时自动失效。

---

## 序列化

### 组件序列化

```python
from core import ComponentSerializer, register_component

@register_component
class MyComponent(Component):
    value: int = 0

# 自动注册后可直接序列化
serialized = ComponentSerializer.serialize(component)
component = ComponentSerializer.deserialize(serialized)
```

### 版本迁移

ComponentSerializer 支持从旧版本数据迁移（当前支持 3.9 → 4.0）。

---

## 设计原则

1. **无硬编码**: 行为由数据 + 规则驱动，无特殊案例
2. **主客观分离**: Component 存储客观状态，System 应用主观解释
3. **信息损失**: 距离、时间、介质会降解信息
4. **组件纯数据**: v4.0 所有业务逻辑在 System 中，Component 仅含数据
5. **向后兼容**: World 保持 v3.9 API，内部委托给新管理器

---

## 依赖关系

```
core/
    ├── entity.py          ← 无依赖（最基础）
    ├── component.py       ← 无依赖
    ├── system.py          ← world.py (TYPE_CHECKING)
    ├── world.py           ← entity, component, entity_manager, archetype_store, system_scheduler, world_event_bus
    ├── entity_manager.py  ← entity
    ├── archetype_store.py ← entity, component
    ├── system_scheduler.py ← system
    ├── world_event_bus.py ← 无依赖
    ├── component_serializer.py ← component
    ├── query_api.py       ← world, entity, component
    └── ...
```

---

## 测试

核心层测试位于项目根目录的 `tests/` 目录中。运行测试：

```bash
pytest tests/ -v
```

---

## 版本历史

| 版本 | 变更 |
|------|------|
| v3.9 | 基础 ECS 实现，World 直接管理所有数据 |
| v4.0 | 架构重构：EntityManager + ArchetypeStore + SystemScheduler + WorldEventBus |

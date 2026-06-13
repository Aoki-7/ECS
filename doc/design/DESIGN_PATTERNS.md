# 设计模式文档

> ECS 架构中的核心设计模式及最佳实践。

---

## 目录

- [工厂模式](#工厂模式)
- [观察者模式](#观察者模式)
- [策略模式](#策略模式)
- [单例模式](#单例模式)
- [外观模式](#外观模式)
- [装饰器模式](#装饰器模式)

---

## 工厂模式

### 植物工厂

```python
class PlantFactory:
    SPECIES_CONFIG = {
        "basic": {"max_photosynthesis_rate": 25.0, ...},
        "tree": {"max_photosynthesis_rate": 18.0, "max_height": 15.0, ...},
    }

    @staticmethod
    def create_plant(world: World, species: str = "basic", x=50, y=50):
        entity = world.create_entity()
        config = PlantFactory.SPECIES_CONFIG.get(species)
        world.add_component(entity, SpaceComponent(x, y))
        world.add_component(entity, GenomeComponent(genes=[...]))
        world.add_component(entity, LifeCycleComponent())
        return entity.id

    @staticmethod
    def create_plant_from_genome(world, parent_genome, x, y):
        child_genome = parent_genome.copy()
        child_genome.mutate()
        # ... 创建子代
```

### 动物工厂

```python
class AnimalFactory:
    SPECIES_CONFIG = {
        "basic": {"max_health": 100, "speed": 1.0},
        "fast": {"max_health": 70, "speed": 2.0},
    }

    @staticmethod
    def create_animal(world, species="basic", x=50, y=50):
        entity = world.create_entity()
        # ... 挂载组件
        return entity.id
```

---

## 观察者模式

### 事件总线（v3.0）

```python
from core.event_bus import EventBus

bus = EventBus.get_instance()

# 订阅
def on_entity_created(event):
    print(f"实体 {event.payload['entity_id']} 已创建")

bus.subscribe("entity_created", on_entity_created)

# 发布
bus.publish("entity_created", {"entity_id": 42})

# 一次性订阅
bus.subscribe("entity_destroyed", handler, once=True)

# 条件订阅
bus.subscribe("entity_created", handler,
    filter_fn=lambda e: e.payload.get("type") == "human")
```

---

## 策略模式

### 决策策略

```python
from abc import ABC, abstractmethod

class IStrategy(ABC):
    @abstractmethod
    def execute(self, world, human_id) -> ActionType:
        pass

class PhysiologicalNeedStrategy(IStrategy):
    def execute(self, world, human_id):
        needs = world.get_component(human_id, PhysiologyNeedsComponent)
        if needs.thirst > 80:
            return ActionType.DRINK
        if needs.hunger > 80:
            return ActionType.EAT
        return ActionType.EXPLORE
```

---

## 单例模式

### EventBus 单例

```python
class EventBus:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### MemoryLayer 单例

```python
class MemoryLayer:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

---

## 外观模式

### World 外观接口

```python
class World:
    """简化 API"""

    def create_entity(self) -> Entity:
        """创建实体"""
        pass

    def get_components(self, *types) -> Iterator:
        """批量查询"""
        pass

    def get_memory_layer(self):
        """获取记忆层"""
        from memory_layer import MemoryLayer
        return MemoryLayer.get_instance()

    def get_event_bus(self):
        """获取事件总线"""
        from core.event_bus import EventBus
        return EventBus.get_instance()
```

---

## 装饰器模式

### System 装饰器

```python
from functools import wraps
from core.system import System

def throttled_update(throttle_duration: float = 5.0):
    def decorator(system_class):
        class NewSystem(system_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._throttle_duration = throttle_duration
                self._last_update_time = 0

            def update(self, world, dt):
                now = world.get_time().total_hours
                if now - self._last_update_time < self._throttle_duration:
                    return
                self._last_update_time = now
                super().update(world, dt)
        return NewSystem
    return decorator

@throttled_update(throttle_duration=5.0)
class SlowSystem(System):
    pass
```

---

## ECS 架构模式

### 数据与逻辑分离

```python
# Component: 纯数据
@dataclass(slots=True)
class PositionComponent(Component):
    x: float = 0.0
    y: float = 0.0

# System: 纯逻辑
class MovementSystem(System):
    def update(self, world, dt):
        for entity, pos, vel in world.get_components(
            PositionComponent, VelocityComponent
        ):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt
```

### 组合优于继承

```python
# 通过组件组合定义实体，而非继承
entity = world.create_entity()
world.add_component(entity, PositionComponent(x=10, y=20))
world.add_component(entity, VelocityComponent(vx=1, vy=0))
world.add_component(entity, HealthComponent(hp=100))
# 同一实体可拥有任意组件组合
```

---

## 避免过度设计

**核心原则**: 保持简单——每个模式都应解决实际问题的复杂度，而非引入新的复杂性。

| 场景 | 推荐模式 |
|------|---------|
| 实体创建/模板化 | 工厂模式 |
| 事件监听/解耦 | 观察者模式（EventBus） |
| 策略选择 | 策略模式 |
| 全局服务访问 | 单例模式 |
| 简化复杂接口 | 外观模式 |
| 动态增强功能 | 装饰器模式 |

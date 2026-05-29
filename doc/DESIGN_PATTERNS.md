# 设计模式文档

> 面向开发者：ECS 架构中的核心设计模式及其最佳实践。

---

## 📚 目录

- [创建者模式 (Creator Pattern)](#创建者模式)
- [观察者模式 (Observer Pattern)](#观察者模式)
- [命令模式 (Command Pattern)](#命令模式)
- [状态模式 (State Pattern)](#状态模式)
- [工厂模式 (Factory Pattern)](#工厂模式)
- [单例模式 (Singleton Pattern)](#单例模式)
- [策略模式 (Strategy Pattern)](#策略模式)
- [适配器模式 (Adapter Pattern)](#适配器模式)
- [装饰器模式 (Decorator Pattern)](#装饰器模式)
- [外观模式 (Facade Pattern)](#外观模式)
- [桥接模式 (Bridge Pattern)](#桥接模式)
- [组合模式 (Composite Pattern)](#组合模式)
- [责任链模式 (Chain of Responsibility)](#责任链模式)
- [备忘录模式 (Memento Pattern)](#备忘录模式)
- [迭代器模式 (Iterator Pattern)](#迭代器模式)
- [中介者模式 (Mediator Pattern)](#中介者模式)
- [解释器模式 (Interpreter Pattern)](#解释器模式)
- [代理模式 (Proxy Pattern)](#代理模式)
- [模板方法模式 (Template Method)](#模板方法模式)
- [职责链模式 (Chain of Responsibility)](#职责链模式)

---

## 🏗️ 创建者模式

### 1.1 人类工厂模式

```python
from dataclasses import dataclass
from typing import List, Dict
from core.component import Component

@dataclass
class HumanEntity:
    """人类实体模板"""
    @staticmethod
    def create_components(world: 'World', x: int = 50, y: int = 50) -> int:
        """
        创建人类实体及其所有组件
        
        Args:
            world: World 实例
            x, y: 实体位置
            
        Returns:
            Entity ID
        """
        entity = world.create_entity()
        
        # 基础组件
        from human.components.basic import (
            HumanComponent, AgeComponent, GenderComponent,
            BodyComponent, IdentityComponent, SpaceComponent
        )
        from human.entities import HumanEntityTemplate
        
        human = HumanEntityTemplate.create_components(world, entity.id, x, y)
        world.add_component(entity, SpaceComponent(x, y))
        
        return entity.id

# 使用示例
human_id = HumanEntity.create_components(world, x=50, y=50)
```

---

### 1.2 资源工厂模式

```python
from dataclasses import dataclass
from resource.food.factory import FoodFactory
from resource.water.factory import WaterFactory

class ResourceFactoryManager:
    """资源工厂管理器"""
    
    @staticmethod
    def create_food(food_type: str, amount: int = 100, x: int = 50, y: int = 50, world: 'World' = None) -> int:
        """创建食物实体"""
        factory = FoodFactory()
        return factory.create_food(food_type, amount, x, y, world)
    
    @staticmethod
    def create_water(amount: int = 100, x: int = 50, y: int = 50, world: 'World' = None) -> int:
        """创建水源实体"""
        factory = WaterFactory()
        return factory.create_water(amount, x, y, world)

# 使用示例
food_id = ResourceFactoryManager.create_food("bread", 100, 50, 50, world)
water_id = ResourceFactoryManager.create_water(100, 50, 50, world)
```

---

## 🔍 观察者模式

### 2.1 Event System

```python
from dataclasses import dataclass, field
from typing import List, Callable, Type, Tuple
from core.component import Component

class WorldEvent:
    """世界事件"""
    
    @dataclass
    class EventPayload:
        """事件数据载荷"""
        @dataclass
        class EntityDiedPayload(EventPayload):
            """实体死亡事件"""
            entity_id: int
            died_component: Type[Component]
            timestamp: float
            
        @dataclass
        class EntitySpawnedPayload(EventPayload):
            """实体出生事件"""
            entity_id: int
            components: Tuple[Type, ...]
        
        @dataclass
        class ResourceRegeneratedPayload(EventPayload):
            """资源再生事件"""
            resource_type: str
            new_amount: int
            location: Tuple[int, int]
        
        def __init__(self, entity_id: int, component: Type[Component], action: str):
            self.entity_id = entity_id
            self.component = component
            self.action = action
    
    @dataclass
    class Event:
        """事件标记"""
        timestamp: float
        payload: EventPayload
    
    def on(self, event_class: Type) -> Event:
        """注册事件"""
        return event_class.create(self)


class WorldEventEngine:
    """世界事件引擎"""
    
    def __init__(self):
        self._handlers: dict[Type[Component], List[Callable]] = {}
    
    def subscribe(self, component_type: Type[Component], handler: Callable) -> None:
        """订阅组件事件"""
        if component_type not in self._handlers:
            self._handlers[component_type] = []
        self._handlers[component_type].append(handler)
    
    def unsubscribe(self, component_type: Type[Component], handler: Callable) -> None:
        """取消订阅"""
        if component_type in self._handlers:
            self._handlers[component_type].remove(handler)
    
    def trigger(self, world: 'World', entity_id: int, component: Type[Component], action: str) -> None:
        """触发事件"""
        payload = WorldEvent.EventPayload(entity_id, component, action)
        timestamp = world.time.hour
        component_event = Event(timestamp, payload)
        
        for handler in self._handlers.get(component, []):
            handler(component_event)


class HealthChangeListener:
    """健康监听器"""
    def __init__(self, threshold: float = 10.0):
        self.threshold = threshold
    
    def on_death(self, event: WorldEvent.Event):
        """实体死亡回调"""
        print(f"Entity {event.payload.entity_id} died!")


class ResourceRegenerationListener:
    """资源再生监听器"""
    def on_regeneration(self, event: WorldEvent.Event):
        """资源再生回调"""
        print(f"Resource {event.payload.resource_type} regenerating...")
```

---

## 👣 命令模式

### 3.1 人类动作命令

```python
from abc import ABC, abstractmethod
from typing import List, Tuple
from core.component import Component
from core.category import ActionType

class ICommand:
    """命令接口"""
    
    @abstractmethod
    def execute(self, world: 'World') -> None:
        """执行命令"""
        pass
    
    @abstractmethod
    def undo(self, world: 'World') -> None:
        """撤销命令"""
        pass

class ActionCommand(ICommand):
    """动作命令"""
    
    def __init__(self, action_type: ActionType, world: 'World', target_entity: int):
        self._action_type = action_type
        self._world = world
        self._target_entity = target_entity
        self._target_action = ActionType.QUEUE
    
    def execute(self, world: 'World') -> None:
        """执行动作"""
        action_system = world.get_system(self._action_type.value)
        action_system.queue_action(self._target_entity, self._action_type)
    
    def undo(self, world: 'World') -> None:
        """撤销动作"""
        action_system = world.get_system(self._action_type.value)
        action_system.clear_action_queue(self._target_entity)


class HumanActionCommandFactory:
    """人类动作命令工厂"""
    
    @staticmethod
    def create_eat_command(world: 'World', target: Tuple[int, int] | None = None) -> ICommand:
        """创建进食命令"""
        return ActionCommand(ActionType.EAT, world, None)
    
    @staticmethod
    def create_drink_command(world: 'World', target: Tuple[int, int] | None = None) -> ICommand:
        """创建饮水命令"""
        return ActionCommand(ActionType.DRINK, world, None)
```

---

## 🔄 状态模式

### 4.1 人类生命周期状态

```python
from enum import Enum
from dataclasses import dataclass

class ReproductiveState(Enum):
    """生殖状态"""
    NO_MATURITY           = "immature"
    MATURING
    REPRODUCTIVE
    PREGNANT
    PREGNANCE_ENDING
    PREGNANT
    MOURNING
    IN_CARE
    NOT_REPRODUCTIVE


@dataclass
class ReproductiveComponent(Component):
    """生殖状态组件"""
    state: ReproductiveState = ReproductiveState.NO_MATURITY
    maturity_date: float = 0.0
    birth_date: float = 0.0
    birth_time: float = 0.0
    days_since_birth: float = 0.0
    current_state_change: ReproductiveState = ReproductiveState.NO_MATURITY
    pregnancy_progress: float = 0.0
    pregnancy_start_time: float = 0.0
    pregnancy_end_time: float = 0.0
    birth_progress: float = 0.0
    birth_start_time: float = 0.0
    birth_end_time: float = 0.0
    mourning_progress: float = 0.0
    mourning_start_time: float = 0.0
    mourning_end_time: float = 0.0
    in_care_progress: float = 0.0
    in_care_start_time: float = 0.0
    in_care_end_time: float = 0.0
    reproduction_progress: float = 0.0
    reproduction_start_time: float = 0.0
    reproduction_end_time: float = 0.0
```

---

## 🏭 工厂模式

### 5.1 组件工厂

```python
from dataclasses import dataclass
from core.component import Component
from typing import Dict, Type

class ComponentFactory:
    """组件工厂"""
    
    @staticmethod
    def create_component(component_type: Type[Component], **kwargs) -> Component:
        """创建新组件实例"""
        return component_type(**kwargs)
    
    @staticmethod
    def create_all_human_components(world: 'World', **kwargs) -> Dict[str, Component]:
        """创建所有人类组件"""
        return {
            "human_component": world.create_component(HumanComponent, **kwargs),
            "age_component": world.create_component(AgeComponent, **kwargs),
            "gender_component": world.create_component(GenderComponent, **kwargs),
            "body_component": world.create_component(BodyComponent, **kwargs),
            "identity_component": world.create_component(IdentityComponent, **kwargs),
            "space_component": world.create_component(SpaceComponent, **kwargs),
            # ... 其他组件
        }


class EntityFactory:
    """实体工厂"""
    
    @staticmethod
    def create_human_entity(world: 'World', position: Tuple[int, int]) -> int:
        """创建人类实体"""
        from human.entities import HumanEntityTemplate
        from human.components.basic import (
            HumanComponent, AgeComponent, GenderComponent,
            BodyComponent, IdentityComponent, SpaceComponent
        )
        
        entity_id = world.create_entity()
        human = HumanEntityTemplate.create_components(world, entity_id, position[0], position[1])
        world.add_component(entity_id, SpaceComponent(position[0], position[1]))
        
        return entity_id

# 使用示例
human_entity = EntityFactory.create_human_entity(world, (50, 50))
food_entity = ComponentFactory.create_component(FoodComponent, amount=100, x=30, y=30)
```

### 5.3 植物工厂模式

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from core.world import World
from core.component import Component
from biology.components.genome_component import GenomeComponent, Gene
from biology.components.life_cycle_component import LifeCycleComponent
from biology.components.energy_component import EnergyComponent
from biology.components.morphology_component import MorphologyComponent
from space.space_component import SpaceComponent

class PlantFactory:
    """植物实体工厂"""

    # 物种基因配置（9 种预设）
    SPECIES_CONFIG = {
        "basic": {
            "max_photosynthesis_rate": 25.0,
            "optimal_temp": 25.0,
            "cold_tolerance": 5.0,
            "heat_tolerance": 35.0,
            "water_use_efficiency": 0.5,
            "metabolism_rate": 0.08,
            "seed_production": 40,
            "dispersal_radius": 5,
            # ... 共 16 维基因参数
        },
        "fast": {"max_photosynthesis_rate": 35.0, "seed_production": 80, ...},
        "tree": {"max_photosynthesis_rate": 18.0, "max_height": 15.0, ...},
        # cold_resistant, drought_resistant, succulent,
        # aquatic, shade_tolerant, pioneer
    }

    @staticmethod
    def create_plant(world: World, species: str = "basic",
                     x: int = 50, y: int = 50) -> int:
        """
        创建植物实体及其所有组件

        Args:
            world: World 实例
            species: 物种预设名称
            x, y: 实体位置

        Returns:
            Entity ID
        """
        entity = world.create_entity()
        config = PlantFactory.SPECIES_CONFIG.get(species,
                            PlantFactory.SPECIES_CONFIG["basic"])

        # 基础组件
        world.add_component(entity, SpaceComponent(x, y))

        # 基因组（16 维基因）
        genes = [Gene(name, config[name]) for name in GenomeComponent.GENE_NAMES]
        world.add_component(entity, GenomeComponent(genes=genes))

        # 生命周期（从种子开始）
        world.add_component(entity, LifeCycleComponent(base_temp=5.0))
        world.add_component(entity, EnergyComponent(energy=10.0))
        world.add_component(entity, MorphologyComponent())

        return entity.id

    @staticmethod
    def create_plant_from_genome(world: World, parent_genome: GenomeComponent,
                                 x: int = 50, y: int = 50) -> int:
        """
        从亲本基因创建子代（遗传+变异）

        Args:
            world: World 实例
            parent_genome: 亲本基因组
            x, y: 子代位置

        Returns:
            Entity ID
        """
        child_genome = parent_genome.copy()
        child_genome.mutate()

        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x, y))
        world.add_component(entity, child_genome)
        world.add_component(entity, LifeCycleComponent(base_temp=5.0))
        world.add_component(entity, EnergyComponent(energy=5.0))
        world.add_component(entity, MorphologyComponent())

        return entity.id

# 使用示例
basic_plant = PlantFactory.create_plant(world, "basic", x=30, y=30)
fast_plant = PlantFactory.create_plant(world, "fast", x=50, y=50)
tree_plant = PlantFactory.create_plant(world, "tree", x=70, y=70)

# 遗传繁殖
parent_genome = world.get_component(parent_id, GenomeComponent)
child_id = PlantFactory.create_plant_from_genome(world, parent_genome, x=35, y=35)
```

### 5.4 动物工厂模式

```python
class AnimalFactory:
    """动物实体工厂（3 种预设）"""

    SPECIES_CONFIG = {
        "basic": {"max_health": 100, "speed": 1.0, "metabolism": 0.5, ...},
        "fast":  {"max_health": 70,  "speed": 2.0, "metabolism": 0.8, ...},
        "tank":  {"max_health": 200, "speed": 0.5, "metabolism": 0.3, ...},
    }

    @staticmethod
    def create_animal(world: World, species: str = "basic",
                      x: int = 50, y: int = 50) -> int:
        entity = world.create_entity()
        config = AnimalFactory.SPECIES_CONFIG.get(species)

        world.add_component(entity, SpaceComponent(x, y))
        # ... 添加各组件

        return entity.id

# 使用示例
animal_id = AnimalFactory.create_animal(world, "fast", x=50, y=50)
```

---

## 🏛️ 单例模式

### 6.1 World 单例

```python
from core.world import World
from core.component import Component

# 6.2 组件单例
class SingletonComponent(Component):
    """单例组件"""
    _instance: 'SingletonComponent' = None
    
    def __new__(cls, *args, **kwargs) -> 'SingletonComponent':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # 初始化逻辑
```

---

## 💻 策略模式

### 7.1 决策策略

```python
from abc import ABC, abstractmethod

class IStrategy(ABC):
    """策略接口"""
    
    @abstractmethod
    def execute(self, world: 'World', human: int) -> ActionType:
        """执行策略"""
        pass


class PhysiologicalNeedStrategy(IStrategy):
    """生理需求策略"""
    
    def execute(self, world: 'World', human: int) -> ActionType:
        """根据生理需求决定行动"""
        need_system = world.get_system(PhysiologyNeedsSystem)
        hunger, thirst, energy, fatigue = need_system.get_current_needs(human)
        
        if thirst > 20:
            return ActionType.DRINK
        
        if hunger > 20:
            return ActionType.EAT
        
        if energy < 40:
            return ActionType.SLEEP
        
        return ActionType.EXPLORE


class SocialNeedStrategy(IStrategy):
    """社交需求策略"""
    
    def execute(self, world: 'World', human: int) -> ActionType:
        """根据社交需求决定行动"""
        social = world.get_component(SocialComponent, world=world).social
        
        if social < 20:
            return ActionType.SOCIALIZE
        
        return ActionType.EXPLORE
```

---

## 🔌 适配器模式

### 8.1 组件适配器

```python
from dataclasses import dataclass
from core.component import Component

class OldComponent(Component):
    """旧组件（不继承 Component 基类）"""
    def __init__(self, value: float):
        self.value = value


class OldComponentAdapter(Component):
    """旧组件适配器"""
    def __init__(self, old_component: OldComponent):
        self._old_component = old_component
        self.value = old_component.value
    
    @property
    def old_value(self) -> float:
        return self._old_component.value
    
    @old_value.setter
    def old_value(self, value: float) -> None:
        self._old_component.value = value
```

---

## 🎨 装饰器模式

### 9.1 System 装饰器

```python
from functools import wraps
from core.system import System

def cached_update(caching=True, max_size=100):
    """@cached_update: 缓存系统更新结果"""
    def decorator(system_class: type) -> type:
        @wraps(system_class)
        def new_update(world: 'World', delta_hours: float):
            result = system_class.update(world, delta_hours)
            if caching and hasattr(system_class, '_cache'):
                system_class._cache = getattr(system_class, '_cache', {})
                system_class._cache.setdefault(delta_hours, result)
            return result
        @wraps(system_class)
        class NewSystem(system_class):
            update = staticmethod(new_update)
        return NewSystem
    return decorator

def limit_update_rate(limit_per_second: float = 1.0):
    """@limit_update_rate: 限制系统更新频率"""
    def decorator(system_class: type) -> type:
        @wraps(system_class)
        class NewSystem(system_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._last_update_time = 0
                self._update_threshold = 1.0 / limit_per_second
                self._update_count = 0
            
            def update(self, world: 'World', delta_hours: float):
                now = world.time.hour
                if now - self._last_update_time < self._update_threshold:
                    return
                self._last_update_time = now
                self._update_count += 1
                super().update(world, delta_hours)
        return NewSystem
    return decorator

def throttled_update(throttle_duration: float = 5.0):
    """@throttled_update: 节流系统更新"""
    def decorator(system_class: type) -> type:
        @wraps(system_class)
        class NewSystem(system_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._throttle_duration = throttle_duration
                self._last_update_time = 0
            
            def update(self, world: 'World', delta_hours: float):
                now = world.time.hour
                if now - self._last_update_time < self._throttle_duration:
                    return
                self._last_update_time = now
                super().update(world, delta_hours)
        return NewSystem
    return decorator


# 使用示例
@cached_update(caching=True)
class CachedHealthSystem(System):
    """带缓存的健康系统"""
    def update(self, world, dt):
        # 更新逻辑
        pass

@throttled_update(throttle_duration=5.0)
class ThrottledProductionSystem(System):
    """限流的生产系统"""
    def update(self, world, dt):
        # 更新逻辑
        pass
```

---

## 🖥️ 外观模式

### 10.1 世界简化接口

```python
class WorldFacade:
    """世界外观接口"""
    
    def __init__(self, world: 'World'):
        self._world = world
    
    # 简化的 API
    def add_human(self, position: Tuple[int, int], **kwargs) -> int:
        """添加人类——简化 API"""
        return self._world.create_entity()
    
    def add_food(self, position: Tuple[int, int], food_type: str = "bread", amount: int = 100) -> int:
        """添加食物——简化 API"""
        return self._world.create_entity()
    
    def add_water(self, position: Tuple[int, int], amount: int = 100) -> int:
        """添加水源——简化 API"""
        return self._world.create_entity()
    
    def get_population_count(self) -> int:
        """获取人口数量"""
        return len(self._world.entities_with_component[HumanComponent])
    
    def get_hunger_level(self) -> int:
        """获取世界总饥饿水平"""
        total = 0
        for eid, comp in self._world.get_components(HumanComponent):
            if hasattr(comp, 'hunger'):
                total += comp.hunger
        return total
```

---

## 🌉 桥接模式

### 11.1 组件桥接

```python
class BridgeableComponent(Component):
    """可桥接组件"""
    def bridge(self, system: System) -> None:
        """桥接到系统"""
        pass


class BridgeSystem(System):
    """桥接系统"""
    def __init__(self, world: 'World', factory: ComponentFactory):
        self._factory = factory
        self._bridge_component(
            world.create_entity(),
            factory.create_component(BridgeableComponent)
        )
```

---

## 📦 组合模式

### 12.1 实体树形结构

```python
@dataclass
class Entity:
    """树形实体"""
    _id: int
    _generation: int
    _components: set
    _children: List['Entity'] = field(default_factory=list)
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def generation(self) -> int:
        return self._generation
    
    def add_component(self, component: Component) -> None:
        self._components.add(type(component))
    
    def remove_component(self, component_type: type) -> None:
        self._components.discard(component_type)
    
    def add_child(self, child: 'Entity') -> None:
        self._children.append(child)
    
    @property
    def children(self) -> List['Entity']:
        return self._children
    
    @property
    def root(self) -> 'Entity':
        return self
    
    def traverse(self) -> None:
        """遍历所有子节点"""
        for child in self._children:
            child.traverse()


class EntityTree(Component):
    """树形实体组件"""
    @property
    def entity_tree(self) -> Entity:
        return self._entity_tree
```

---

## 🧩 访问模式

### 13.1 组件访问器

```python
class WorldComponentAccessor:
    """世界组件访问器"""
    
    def __init__(self, world: 'World'):
        self._world = world
    
    def get_component(
        self,
        component_type: Type[Component],
        world: 'World',
        entity_id: Optional[int] = None
    ) -> Component:
        """获取组件实例"""
        world_component = world.get_world_component(component_type)
        return world_component
    
    def get_components(
        self,
        *component_types: Type[Component]
    ) -> Dict[Type[Component], Component]:
        """获取所有组件实例"""
        return {
            component_type: world.get_world_component(component_type)
            for component_type in component_types
        }
```

---

## 🔑 代理模式

### 14.1 虚拟组件代理

```python
class VirtualComponentProxy:
    """虚拟组件代理"""
    
    def __init__(self, world: 'World', virtual_id: int) -> None:
        self._world = world
        self._virtual_id = virtual_id
        self._target_component = None
    
    def get_target_component(self) -> Component:
        """获取实际组件"""
        if self._target_component is None:
            entities_with_component = self._world.get_components(HumanComponent)
            
            for entity_id, comp in entities_with_component:
                if entity_id is None:
                    self._target_component = self._world.get_world_component(
                        HumanComponent
                    )
                    break
        
        return self._target_component
    
    @property
    def target_component(self) -> Component:
        return self.get_target_component()
```

---

## 📝 模板方法模式

### 15.1 System 模板方法

```python
from abc import ABC, abstractmethod

class SystemTemplate(ABC):
    """系统模板"""
    
    def __init__(self, world: 'World'):
        self._world = world
        self._priority = 0
    
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def update(self, world: 'World', delta_hours: float) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def validate(self, world: 'World') -> bool:
        raise NotImplementedError


class HealthSystem(SystemTemplate):
    """健康系统实现"""
    
    @property
    def name(self) -> str:
        return "HealthSystem"
    
    def update(self, world, dt):
        # 健康系统逻辑
        pass
    
    def __str__(self) -> str:
        return "HealthSystem"
```

---

## 🧵 职责链模式

### 16.1 动作执行链

```python
class ActionChain:
    """动作执行链"""
    
    def __init__(self):
        self._chains: List[Callable[[type], type]] = []
    
    def add(
        self,
        component_type: Type[Component],
        system_factory: Callable[[type], type],
        name: str = None
    ) -> None:
        self._chains.append((component_type, system_factory, name))
    
    def execute(self, world: 'World', component: Type[Component]) -> None:
        for component_type, factory, _ in self._chains:
            if issubclass(component, component_type):
                system_class = factory(component_type)
                system_instance = system_class(world=world)
                system_instance.update(world, world.time.hour)
        
            if len(self._chains) > 1:
                self.execute(world, component)
```

---

## 📁 备忘录模式

### 17.1 系统状态快照

```python
class Snapshot:
    """状态快照"""
    def __init__(self, world: 'World'):
        self._components: Dict[Type[Component], Component] = {}
        self._entity_states: Dict[int, Dict[Type[Component], Component]] = {}
    
    def record(self, world: 'World', world: 'World') -> None:
        for component in world._components:
            self._components[component.__class__] = component
        
        for entity_id, entity in world._entities.items():
            entity_states = {}
            for component in entity._components:
                entity_states[component.__class__] = world.get_world_component(component.__class__)[entity_id]
            self._entity_states[entity_id] = entity_states
    
    def restore(self) -> World:
        # 恢复逻辑
        return world


class WorldStateMachine:
    """世界状态机"""
    
    def __init__(self, world: 'World'):
        self._state = None
        self._state_history: List[Snapshot] = []
    
    def set(self, state: Snapshot, world: World) -> None:
        self._state = state
        self._state_history.append(Snapshot(world))
    
    def restore(self) -> None:
        self._state = self._state_history.pop()
```

---

## 🔁 迭代器模式

### 18.1 系统迭代器

```python
class SystemIterator:
    """系统迭代器"""
    
    def __init__(self, systems: List[System]):
        self._systems = systems
        self._index = 0
    
    def next(self) -> System:
        if self._index < len(self._systems):
            system = self._systems[self._index]
            self._index += 1
            return system
        return None
```

---

## ☮️ 中介者模式

### 19.1 世界中介者

```python
class WorldMediator:
    """世界中介者"""
    
    @staticmethod
    def interact(sender: Component, event) -> None:
        pass
```

---

## 🧠 解释器模式

### 20.1 规则解释器

```python
class RuleInterpreter:
    """规则解释器"""
    
    def interpret(self, world: 'World', rule) -> None:
        pass
```

---

## 🎯 外观模式

### 21.1 系统管理接口

```python
class SystemManager:
    """系统管理接口"""
    
    @staticmethod
    def register_system(system: System) -> None:
        pass

    @staticmethod
    def get_system(system_class: Type[System]) -> System:
        pass
```

---

## 🗂️ 职责链模式

### (重复) 责任链模式

### (重复) 代理模式

### (重复) 备忘录模式

### (重复) 迭代器模式

### (重复) 中介者模式

### (重复) 解释器模式

### (重复) 外观模式

---

## 🎓 总结与建议

### 何时使用这些模式？

| 场景 | 推荐模式 |
|------|---------|
| 实体初始化/模板化创建 | 创建者模式 |
| World/Entity 单例需求 | 单例模式 |
| 生命周期状态管理 | 状态模式 |
| 动作指令执行 | 命令模式 |
| 世界全局服务 | 外观模式 |
| 组件系统解耦 | 桥接模式 |
| Observer 事件监听 | 观察者模式 |
| 策略选择系统 | 策略模式 |

### ECS 架构特有的设计模式

除了以上经典设计模式，ECS 本身也是一种架构模式：

- **Entity-Component-System (ECS)**: 数据与逻辑分离模式
- **Observer Pattern Variant**: 通过 World 索引实现单向观察者
- **Factory Pattern for Components**: 组件工厂模式

### 避免过度设计

**核心原则**: 保持简单——每个模式都应解决实际问题的复杂度，而非引入新的复杂性。

---

**版本**: v2.2  
**最后更新**: 2026 年 5 月 28 日  
**贡献者**: ECS Community
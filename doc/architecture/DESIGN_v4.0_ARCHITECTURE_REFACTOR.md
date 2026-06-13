# ECS v4.0 架构重构设计文档

> 版本: v4.0-alpha  
> 日期: 2026-06-12  
> 状态: 设计阶段（待主人确认后执行）  

---

## 一、重构背景与目标

### 1.1 当前架构问题（v3.9）

| 优先级 | 问题 | 影响 |
|--------|------|------|
| P0 | World 类职责过重（~500行，上帝对象） | 违反单一职责，难以维护 |
| P0 | 组件查询性能瓶颈（集合交集计算） | 高频查询场景性能差 |
| P1 | Component 纯数据化不彻底 | 与核心设计原则冲突 |
| P1 | System 优先级管理脆弱（魔法数字） | 新增系统易冲突 |
| P1 | 测试覆盖不均衡（human/plant薄弱） | 重构风险高 |
| P2 | 事件总线全局单例 | 多World隔离困难 |
| P2 | 序列化不统一 | 存档/网络传输风险 |
| P2 | 文档与代码不同步 | 维护成本高 |

### 1.2 重构目标

1. **架构纯度**：World 拆分为专职管理器，Component 彻底纯数据化
2. **性能提升**：引入 Archetype 存储，查询性能提升 5-10x
3. **可维护性**：System 依赖图自动排序，测试覆盖均衡
4. **可扩展性**：支持多 World 隔离，统一序列化框架

---

## 二、核心架构重构（P0）

### 2.1 World 拆分：从上帝对象到协调者

#### 2.1.1 当前问题

```python
# v3.9: World 承担了所有职责
class World:
    def __init__(self):
        self.entities: dict[int, Entity] = {}           # Entity CRUD
        self.components = defaultdict(dict)              # Component 存储
        self._component_entities: dict = defaultdict(set) # 反向索引
        self.systems = []                                # System 调度
        self._query_cache: dict = {}                     # 查询缓存
        self._world_entity: Entity | None = None         # 世界实体
    
    # Entity 管理（~80行）
    def create_entity(self) -> Entity: ...
    def remove_entity(self, entity: Entity): ...
    
    # Component 管理（~100行）
    def add_component(self, entity, component): ...
    def get_component(self, entity, component_type): ...
    def get_components(self, *component_types): ...
    
    # System 调度（~60行）
    def add_system(self, system): ...
    def update(self, dt): ...
    
    # SpaceSystem 耦合（~40行）
    def _register_component_to_space(self, ...): ...
    
    # 事件/记忆层（~40行）
    def _notify_memory_layer(self, ...): ...
```

#### 2.1.2 目标架构

```python
# v4.0: World 变为协调者，职责委托给专职管理器
class World:
    """World 协调者 — 只负责生命周期管理和跨模块协调"""
    
    def __init__(self):
        self._entity_manager = EntityManager()
        self._component_store = ArchetypeStore()  # 替代 defaultdict
        self._system_scheduler = SystemScheduler()
        self._event_bus = EventBus()  # 非单例，每 World 独立
        self._world_entity: Entity | None = None
        self.tick_count = 0
    
    # === 委托方法（保持向后兼容）===
    def create_entity(self) -> Entity:
        return self._entity_manager.create()
    
    def add_component(self, entity, component):
        self._component_store.add(entity, component)
        self._event_bus.publish("component_added", {...})
    
    def get_components(self, *types):
        return self._component_store.query(*types)
    
    def add_system(self, system):
        self._system_scheduler.add(system)
    
    def update(self, dt):
        self.tick_count += 1
        self._system_scheduler.update(self, dt)
```

#### 2.1.3 新增核心类

| 类名 | 职责 | 文件 |
|------|------|------|
| `EntityManager` | Entity ID 分配、回收、生命周期 | `core/entity_manager.py` |
| `ArchetypeStore` | Archetype-based 组件存储 | `core/archetype_store.py` |
| `SystemScheduler` | System 依赖解析、排序、调度 | `core/system_scheduler.py` |
| `WorldEventBus` | 每 World 独立的事件总线 | `core/world_event_bus.py` |

---

### 2.2 Archetype 存储：查询性能革命

#### 2.2.1 当前性能瓶颈

```python
# v3.9: 每次查询都计算集合交集
def get_components(self, *component_types):
    sets = [self._component_entities[ct] for ct in component_types]
    common = set.intersection(*sets) if sets else set()
    for eid in common:
        yield self.entities[eid], [self.components[ct][eid] for ct in component_types]

# 问题：
# 1. O(n) 集合交集计算
# 2. 缓存粒度太粗（任何变更清空全部缓存）
# 3. 内存局部性差（组件分散存储）
```

#### 2.2.2 Archetype 设计（参考 Bevy/Unity DOTS）

```python
# v4.0: Archetype-based 存储
class Archetype:
    """
    Archetype = 组件类型的唯一组合
    
    例如：
    - Archetype(HealthComponent, PositionComponent) 
    - Archetype(HealthComponent, PositionComponent, VelocityComponent)
    
    每个 Archetype 内部用列式存储：
    - entities: List[Entity]      # 行：实体列表
    - columns: Dict[Type, List]   # 列：组件数组
    """
    
    def __init__(self, component_types: Tuple[Type[Component], ...]):
        self.id = _hash_types(component_types)
        self.component_types = component_types
        self.entities: List[Entity] = []
        self.columns: Dict[Type, List[Component]] = {
            t: [] for t in component_types
        }
        self.entity_index: Dict[int, int] = {}  # entity_id -> row_index

class ArchetypeStore:
    """
    管理所有 Archetype，处理实体组件变更
    """
    
    def __init__(self):
        self._archetypes: Dict[int, Archetype] = {}  # archetype_id -> Archetype
        self._entity_archetype: Dict[int, int] = {}   # entity_id -> archetype_id
        self._query_cache: Dict[Tuple, ArchetypeQuery] = {}
    
    def add_component(self, entity: Entity, component: Component):
        """添加组件 = 实体从一个 Archetype 迁移到另一个"""
        old_arch_id = self._entity_archetype.get(entity.id)
        
        # 计算新 Archetype 类型签名
        new_types = self._get_new_types(old_arch_id, type(component))
        new_arch_id = _hash_types(new_types)
        
        # 创建或获取新 Archetype
        if new_arch_id not in self._archetypes:
            self._archetypes[new_arch_id] = Archetype(new_types)
        
        # 迁移实体数据
        self._migrate_entity(entity, old_arch_id, new_arch_id, component)
    
    def query(self, *component_types) -> Iterator[Tuple[Entity, ...]]:
        """查询 = 遍历匹配的 Archetype，无需集合交集"""
        cache_key = component_types
        if cache_key in self._query_cache:
            yield from self._query_cache[cache_key]
            return
        
        result = []
        for archetype in self._archetypes.values():
            if _is_subset(component_types, archetype.component_types):
                # 直接遍历连续内存，缓存友好
                for i, entity in enumerate(archetype.entities):
                    comps = [archetype.columns[t][i] for t in component_types]
                    item = (entity, *comps)
                    result.append(item)
                    yield item
        
        self._query_cache[cache_key] = result
```

#### 2.2.3 性能对比

| 场景 | v3.9 (集合交集) | v4.0 (Archetype) | 提升 |
|------|----------------|------------------|------|
| 10k实体，单组件查询 | O(n) | O(n) | 2-3x（内存局部性） |
| 10k实体，3组件交集 | O(n) + 集合运算 | O(n) 直接遍历 | 5-10x |
| 组件变更后查询 | 全缓存清空 | 仅受影响 Archetype 失效 | 查询命中率↑ |
| 遍历连续内存 | 随机访问 | 顺序访问 | CPU缓存友好 |

---

### 2.3 System 依赖图：替代魔法数字

#### 2.3.1 当前问题

```python
# v3.9: 魔法数字优先级
class SystemPriority:
    SPACE = 0
    TIME = 5
    ENVIRONMENT = 20
    HUMAN_COGNITIVE = 30
    # ... 新增系统时容易冲突

class MySystem(System):
    priority = 31  # 为什么31？因为30被占了？
```

#### 2.3.2 依赖图设计

```python
# v4.0: 声明式依赖
class System:
    # 声明"我必须在哪些系统之后运行"
    dependencies_after: List[Type[System]] = []
    
    # 声明"我必须在哪些系统之前运行"
    dependencies_before: List[Type[System]] = []
    
    # 可选：兼容旧优先级（用于同依赖层级内排序）
    priority: int = 0

# 示例
class MovementSystem(System):
    """移动系统 — 必须在碰撞检测之前"""
    dependencies_before = [CollisionSystem]

class CollisionSystem(System):
    """碰撞检测 — 必须在移动之后，行为之前"""
    dependencies_after = [MovementSystem]
    dependencies_before = [DecisionSystem]

class DecisionSystem(System):
    """决策系统 — 必须在碰撞检测之后"""
    dependencies_after = [CollisionSystem]

class SystemScheduler:
    """自动解析依赖图，拓扑排序"""
    
    def __init__(self):
        self._systems: List[System] = []
        self._sorted: List[System] = []
        self._dirty = True
    
    def add(self, system: System):
        self._systems.append(system)
        self._dirty = True
    
    def _sort(self):
        """拓扑排序 + 优先级排序"""
        # 1. 构建依赖图
        graph = {}
        for s in self._systems:
            graph[type(s)] = {
                'after': set(s.dependencies_after),
                'before': set(s.dependencies_before),
                'priority': s.priority,
                'instance': s
            }
        
        # 2. 拓扑排序（Kahn算法）
        sorted_types = self._topological_sort(graph)
        
        # 3. 同层级内按 priority 排序
        self._sorted = [...]
    
    def update(self, world, dt):
        if self._dirty:
            self._sort()
        
        for system in self._sorted:
            if system.enabled and world.tick_count % system.tick_interval == 0:
                system.update(world, dt)
```

#### 2.3.3 依赖验证

```python
def validate_dependencies(systems: List[System]) -> List[str]:
    """验证依赖图无环、无冲突"""
    errors = []
    
    # 检查循环依赖
    if _has_cycle(systems):
        errors.append("检测到循环依赖")
    
    # 检查未声明的隐式依赖
    for s in systems:
        for after in s.dependencies_after:
            if after not in systems:
                errors.append(f"{type(s).__name__} 依赖未注册的 {after.__name__}")
    
    return errors
```

---

## 三、Component 纯数据化（P1）

### 3.1 迁移策略

#### 3.1.1 需要迁移的 Component（含业务逻辑）

| Component | 方法数量 | 目标 System | 优先级 |
|-----------|----------|-------------|--------|
| `MemoryComponent` | 5+ | `MemoryManagementSystem` | P0 |
| `WorldConfigComponent` | 2 | `WorldConfigSystem` | P0 |
| `CircadianComponent` | 2 | `CircadianSystem` | P1 |
| `ActionComponent` | 1 | `ActionSystem` | P1 |
| `SearchComponent` | 0 | 已纯数据 | ✅ |
| `HealthStatusComponent` | 0 | 已纯数据 | ✅ |
| `LifeCycleComponent` | 0 | 已纯数据 | ✅ |

#### 3.1.2 迁移示例：MemoryComponent

```python
# v3.9: 含业务逻辑
@dataclass(slots=True)
class MemoryComponent(Component):
    events: list = field(default_factory=list)
    places: dict = field(default_factory=dict)
    people: dict = field(default_factory=dict)
    
    def add_event(self, time, event_type, description, impact=0.0, location=None):
        self.events.append({...})
        if len(self.events) > 100:
            self.events.pop(0)
    
    def get_recent_events(self, n=5, event_type=None):
        ...
    
    def get_event_sentiment(self, event_type, current_time=None, hours=48):
        ...
    
    def record_place(self, pos, place_type, time, sentiment=0.5):
        ...
    
    def find_best_place_by_type(self, place_type, current_pos):
        ...

# v4.0: 纯数据
@dataclass(slots=True)
class MemoryComponent(Component):
    """记忆组件 — 纯数据"""
    events: list = field(default_factory=list)      # [(time, type, desc, impact, loc)]
    places: dict = field(default_factory=dict)      # {(x,y): {type, last_visit, sentiment, visits}}
    people: dict = field(default_factory=dict)      # {entity_id: {name, relationship, last_interaction, trust}}
    recent_successes: dict = field(default_factory=lambda: {...})
    
    # 仅保留数据约束（非业务逻辑）
    MAX_EVENTS: ClassVar[int] = 100

# 新增：MemoryManagementSystem
class MemoryManagementSystem(System):
    """记忆管理系统 — 处理所有记忆业务逻辑"""
    tick_interval = 10
    
    def update(self, world, dt):
        for entity, (memory,) in world.get_components(MemoryComponent):
            self._decay_events(memory, dt)
            self._limit_history(memory)
    
    def _decay_events(self, memory: MemoryComponent, dt: float):
        """事件情感衰减"""
        for event in memory.events:
            event['impact'] *= 0.99  # 每帧衰减1%
    
    def _limit_history(self, memory: MemoryComponent):
        """限制历史记录长度"""
        if len(memory.events) > MemoryComponent.MAX_EVENTS:
            memory.events = memory.events[-MemoryComponent.MAX_EVENTS:]
    
    # 静态工具方法（供其他 System 调用）
    @staticmethod
    def add_event(memory: MemoryComponent, time, event_type, description, 
                  impact=0.0, location=None):
        memory.events.append({...})
    
    @staticmethod
    def get_recent_events(memory: MemoryComponent, n=5, event_type=None):
        ...
    
    @staticmethod
    def record_place(memory: MemoryComponent, pos, place_type, time, sentiment=0.5):
        ...
```

#### 3.1.3 迁移检查清单

```python
# 用于检测 Component 是否含业务逻辑
def check_component_purity(component_class) -> List[str]:
    """检查 Component 是否纯数据"""
    issues = []
    
    for name, method in inspect.getmembers(component_class, predicate=inspect.isfunction):
        if name in ('__init__', 'to_dict', 'from_dict', '__post_init__'):
            continue
        if not name.startswith('_'):
            issues.append(f"{component_class.__name__}.{name} 是公共方法，应迁移到 System")
    
    return issues
```

---

### 3.2 统一序列化框架

#### 3.2.1 当前问题

```python
# 方式1: dataclass + asdict()
class Component:
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, d): return cls(**d)

# 方式2: 手动实现
class CircadianComponent(Component):
    def to_dict(self): 
        return {"phase": self.phase, "period": self.period, ...}
    @classmethod
    def from_dict(cls, data):
        return cls(phase=data.get("phase", 0.0), ...)

# 方式3: 无序列化
class HumanComponent(Component):
    pass  # 空组件，但存档时可能丢失
```

#### 3.2.2 统一序列化设计

```python
# v4.0: 统一序列化框架
from typing import Protocol

class Serializable(Protocol):
    """序列化协议"""
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "Serializable": ...

class ComponentSerializer:
    """组件序列化器 — 自动处理所有 Component 类型"""
    
    _registry: Dict[str, Type[Component]] = {}
    
    @classmethod
    def register(cls, component_type: Type[Component]):
        """注册组件类型"""
        cls._registry[component_type.__name__] = component_type
    
    @classmethod
    def serialize(cls, component: Component) -> dict:
        """序列化组件"""
        return {
            "__type__": type(component).__name__,
            "data": component.to_dict()
        }
    
    @classmethod
    def deserialize(cls, data: dict) -> Component:
        """反序列化组件"""
        type_name = data["__type__"]
        component_type = cls._registry.get(type_name)
        if component_type is None:
            raise ValueError(f"未注册的组件类型: {type_name}")
        return component_type.from_dict(data["data"])

# 自动注册装饰器
@dataclass(slots=True)
@register_component  # 自动注册到 ComponentSerializer
class HealthComponent(Component):
    hp: float = 100.0
    max_hp: float = 100.0
    
    def to_dict(self): 
        return {"hp": self.hp, "max_hp": self.max_hp}
    
    @classmethod
    def from_dict(cls, d):
        return cls(hp=d.get("hp", 100.0), max_hp=d.get("max_hp", 100.0))
```

---

## 四、事件总线重构（P2）

### 4.1 多 World 隔离

#### 4.1.1 当前问题

```python
# v3.9: 全局单例
class EventBus:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance

# 问题：
# 1. 测试时需要 reset_instance()
# 2. 多 World 场景下事件混淆
# 3. 无法按 World 隔离事件
```

#### 4.1.2 目标设计

```python
# v4.0: 每 World 独立的事件总线
class WorldEventBus:
    """World 级别事件总线 — 非单例"""
    
    def __init__(self, world_id: str = "default"):
        self.world_id = world_id
        self._subscriptions: Dict[str, List[EventSubscription]] = {}
        self._history: deque = deque(maxlen=1000)
        self._stats = {"published": 0, "delivered": 0}
    
    def subscribe(self, event_type, handler, priority=0, once=False):
        ...
    
    def publish(self, event_type, payload, source="unknown", timestamp=0):
        ...
    
    def get_history(self, event_type=None):
        ...

class World:
    def __init__(self, world_id: str = "default"):
        self._event_bus = WorldEventBus(world_id)
    
    def get_event_bus(self) -> WorldEventBus:
        return self._event_bus

# 全局事件总线（用于跨 World 通信）
class GlobalEventBus:
    """全局事件总线 — 用于 World 间通信"""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalEventBus()
        return cls._instance
```

---

## 五、测试策略

### 5.1 测试覆盖目标

| 模块 | 当前测试数 | 目标测试数 | 缺口 |
|------|-----------|-----------|------|
| core | 13文件 | 20文件 | +7 |
| memory_layer | 53 | 60 | +7 |
| animal | 25 | 40 | +15 |
| human | 5 | 50 | **+45** |
| plant | 6 | 30 | **+24** |
| environment | 若干 | 40 | +20 |

### 5.2 新增测试类型

```python
# 1. ArchetypeStore 测试
class TestArchetypeStore:
    def test_entity_migration(self):
        """实体添加组件时正确迁移 Archetype"""
        store = ArchetypeStore()
        entity = Entity.create()
        
        store.add(entity, HealthComponent(hp=100))
        assert store.get_archetype_id(entity) == _hash_types((HealthComponent,))
        
        store.add(entity, PositionComponent(x=10, y=20))
        assert store.get_archetype_id(entity) == _hash_types((HealthComponent, PositionComponent))
    
    def test_query_performance(self):
        """查询性能基准"""
        store = ArchetypeStore()
        for i in range(10000):
            e = Entity.create()
            store.add(e, HealthComponent(hp=i))
            store.add(e, PositionComponent(x=i, y=i))
        
        start = time.time()
        results = list(store.query(HealthComponent, PositionComponent))
        elapsed = time.time() - start
        
        assert len(results) == 10000
        assert elapsed < 0.01  # 10ms 内完成

# 2. System 依赖图测试
class TestSystemScheduler:
    def test_topological_sort(self):
        """依赖图正确排序"""
        scheduler = SystemScheduler()
        scheduler.add(MovementSystem())
        scheduler.add(CollisionSystem())
        scheduler.add(DecisionSystem())
        
        sorted_systems = scheduler._sort()
        
        # Movement 必须在 Collision 之前
        movement_idx = next(i for i, s in enumerate(sorted_systems) if isinstance(s, MovementSystem))
        collision_idx = next(i for i, s in enumerate(sorted_systems) if isinstance(s, CollisionSystem))
        assert movement_idx < collision_idx
    
    def test_circular_dependency_detection(self):
        """循环依赖检测"""
        scheduler = SystemScheduler()
        
        class A(System):
            dependencies_after = [B]
        class B(System):
            dependencies_after = [A]
        
        scheduler.add(A())
        scheduler.add(B())
        
        with pytest.raises(CircularDependencyError):
            scheduler._sort()

# 3. Component 纯度测试
class TestComponentPurity:
    def test_no_business_logic_in_components(self):
        """所有 Component 都是纯数据"""
        from core.component_registry import get_all_components
        
        for comp_class in get_all_components():
            issues = check_component_purity(comp_class)
            assert not issues, f"{comp_class.__name__} 含业务逻辑: {issues}"
```

---

## 六、实施计划

### 6.1 Phase 1: 核心重构（P0）— 预计 2-3 天

| 步骤 | 任务 | 文件 | 测试 |
|------|------|------|------|
| 1.1 | 创建 EntityManager | `core/entity_manager.py` | `core/tests/test_entity_manager.py` |
| 1.2 | 创建 ArchetypeStore | `core/archetype_store.py` | `core/tests/test_archetype_store.py` |
| 1.3 | 创建 SystemScheduler | `core/system_scheduler.py` | `core/tests/test_system_scheduler.py` |
| 1.4 | 重构 World 为协调者 | `core/world.py` | 更新 `test_world.py` |
| 1.5 | 集成测试 | — | 全量回归测试 |

### 6.2 Phase 2: 纯数据化 + 依赖图（P1）— 预计 3-4 天

| 步骤 | 任务 | 文件 | 测试 |
|------|------|------|------|
| 2.1 | 迁移 MemoryComponent | `human/components/cognitive/memory_component.py` | `human/tests/test_memory_system.py` |
| 2.2 | 迁移 WorldConfigComponent | `core/components/world_config_component.py` | `core/tests/test_world_config_system.py` |
| 2.3 | 迁移 CircadianComponent | `biology/components/circadian_component.py` | `biology/tests/test_circadian_system.py` |
| 2.4 | 迁移 ActionComponent | `human/components/action/action_component.py` | `human/tests/test_action_system.py` |
| 2.5 | 为所有 System 添加依赖声明 | 各 `systems/*.py` | `core/tests/test_dependencies.py` |
| 2.6 | 补充 human/plant 测试 | — | +45 / +24 个测试 |

### 6.3 Phase 3: 事件总线 + 序列化（P2）— 预计 2-3 天

| 步骤 | 任务 | 文件 | 测试 |
|------|------|------|------|
| 3.1 | 创建 WorldEventBus | `core/world_event_bus.py` | `core/tests/test_world_event_bus.py` |
| 3.2 | 创建 ComponentSerializer | `core/component_serializer.py` | `core/tests/test_serializer.py` |
| 3.3 | 为所有 Component 添加 @register_component | 各 `components/*.py` | `core/tests/test_registry.py` |
| 3.4 | 更新存档系统 | `save_load/*.py` | `save_load/tests/test_save_load.py` |
| 3.5 | 更新文档 | `architecture/ARCHITECTURE.md`, `../ROADMAP.md` | — |

### 6.4 风险与回滚策略

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Archetype 迁移引入性能回退 | 中 | 高 | 保留 v3.9 存储作为 fallback |
| System 依赖图解析失败 | 低 | 高 | 保留 priority 作为 fallback |
| 测试覆盖率不足 | 中 | 中 | 每 Phase 结束强制全量测试 |
| 循环依赖 | 低 | 高 | 依赖图验证 + 运行时检测 |

---

## 七、向后兼容性

### 7.1 API 兼容层

```python
# v4.0 World 保持 v3.9 API 兼容
class World:
    # 旧 API（兼容层）
    def create_entity(self) -> Entity:
        return self._entity_manager.create()
    
    def get_components(self, *types):
        return self._component_store.query(*types)
    
    # 新 API（推荐使用）
    def query(self, *types):
        return self._component_store.query(*types)
    
    @property
    def archetypes(self):
        return self._component_store.archetypes
```

### 7.2 存档兼容

```python
class SaveLoadMigrator:
    """存档迁移器 — v3.9 -> v4.0"""
    
    @staticmethod
    def migrate_v39_to_v40(data: dict) -> dict:
        """迁移 v3.9 存档到 v4.0"""
        # 1. 转换组件存储格式
        # v3.9: {component_type: {entity_id: component_data}}
        # v4.0: {archetype_id: {entities: [...], columns: {...}}}
        
        # 2. 重建 Archetype 结构
        entities = data.get('entities', {})
        components = data.get('components', {})
        
        migrated = {
            'version': '4.0',
            'entities': entities,
            'archetypes': _rebuild_archetypes(entities, components)
        }
        
        return migrated
```

---

## 八、验收标准

### 8.1 功能验收

- [ ] 所有 542+ 现有测试通过
- [ ] 新增 100+ 测试通过
- [ ] 存档/读档功能正常
- [ ] SimulationLoop 正常运行

### 8.2 性能验收

- [ ] 10k 实体创建 < 3s（v3.9: < 5s）
- [ ] 组件查询 1000 次 < 0.5s（v3.9: < 1s）
- [ ] 100 帧更新 < 3s（v3.9: < 5s）

### 8.3 架构验收

- [ ] World 类 < 200 行（v3.9: ~500行）
- [ ] 所有 Component 纯数据化（check_component_purity 通过）
- [ ] System 依赖图无环
- [ ] 每 World 独立事件总线

---

## 九、附录

### 9.1 参考架构

- **Bevy ECS**: Archetype-based 存储、System 依赖图
- **Unity DOTS**: Archetype Chunk、Burst Compiler
- **Entt**: Sparse Set 存储、Group 查询

### 9.2 术语表

| 术语 | 定义 |
|------|------|
| Archetype | 组件类型的唯一组合，如 (Health, Position) |
| Chunk | Archetype 内部的连续内存块 |
| Sparse Set | 稀疏集合，用于 Entity -> Component 映射 |
| 拓扑排序 | 有向无环图的线性排序 |

---

> **下一步**: 主人确认设计文档后，按 Phase 1 → Phase 2 → Phase 3 顺序执行。每个 Phase 完成后汇报进度并运行全量测试。

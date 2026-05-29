# 问题排查指南 (Troubleshooting Guide)

> 面向开发者：常见问题、错误处理与问题排查指南。

---

## 📚 目录

- [常见错误 (Common Errors)](#常见错误)
- [性能问题 (Performance Issues)](#性能问题)
- [调试技巧 (Debugging Tips)](#调试技巧)
- [日志配置 (Log Configuration)](#日志配置)
- [版本兼容性 (Version Compatibility)](#版本兼容性)
- [内存泄漏 (Memory Leaks)](#内存泄漏)
- [环境配置 (Environment Configuration)](#环境配置)

---

## ❌ 常见错误

### 错误 1：System 未注册

**现象**：系统不执行或报错 `AttributeError`

**错误示例**：

```python
class MySystem(System):
    def update(self, world, dt):
        print("Running!")

# ❌ 忘记注册
# MySystem 不会被执行

# ✅ 正确做法
world.register_system(MySystem, priority=10)
```

**排查方法**：

```python
# 在 World 初始化后检查已注册的 System
print("Registered systems:", list(world._systems.keys()))
```

---

### 错误 2：System 未依赖 Component

**现象**：System 遍历不报错，但处理不到任何实体

**错误示例**：

```python
class MySystem(System):
    def update(self, world, dt):
        # ❌ 只依赖 PositionComponent，但它不依赖 VelocityComponent
        for eid, pos in world.get_components(PositionComponent):
            # 只有带 PositionComponent 的实体会被处理
            pass
```

**排查方法**：

```python
# 检查哪些实体有 PositionComponent
from space.space_component import SpaceComponent

print("Entities with position:", len(world.get_components(SpaceComponent)))
```

---

### 错误 3：Component 类型不匹配

**现象**：无法更新或处理

**错误示例**：

```python
@dataclass
class HealthComponent(Component):
    health: int = 0

class HealthSystem(System):
    def update(self, world, dt):
        # ❌ 获取到了 HealthComponent 的不同实例
        for eid, health_component in world.get_components(HealthComponent):
            if health_component.health < 0:
                health_component.health = 0
```

**正确做法**：

```python
class HealthSystem(System):
    def update(self, world, dt):
        # ✅ 确保遍历正确的 Component 类型
        for eid, health_component in world.get_components(HealthComponent):
            # 处理逻辑
            pass
```

---

### 错误 4：Entity 生命周期管理失效

**现象**：悬挂引用、内存泄漏

**错误示例**：

```python
# ❌ Entity 被删除但 Component 未清理
world.remove_entity(entity)
# 但实体 still has components!

# ✅ 正确做法
def cleanup_entity_components(world, entity):
    for comp_type in entity._components:
        world.remove_component(entity, comp_type)
    world.remove_entity(entity)
```

**排查方法**：

```python
def check_hanging_entities(world):
    """检查悬挂实体（无引用但依然存在）"""
    hanging = []
    for entity_id, entity in world._entities.items():
        # 检查实体是否被其他系统依赖
        if hasattr(entity, 'referenced_by'):
            handlers = entity.referenced_by
            if len(handlers) == 0:
                hanging.append((entity_id, list(entity._components.keys())))
    return hanging
```

---

### 错误 5：双向索引不一致

**现象**：`world.get_components()` 返回结果与手动遍历不一致

**错误示例**：

```python
# ❌ 手动添加组件但忘记更新索引
def manual_add_component(world, entity_id, component):
    entity = world.query_entity(entity_id)
    entity._components[type(component)] = component
    # 忘记更新 world._components
```

**正确做法**：

```python
def manual_add_component(world, entity_id, component):
    entity = world.query_entity(entity_id)
    entity._components[type(component)] = component
    world._components[type(component)][entity_id] = component
    # ✅ 更新双向索引
```

---

### 错误 6：优先级冲突

**现象**：期望的行为未按预期发生

**错误示例**：

```python
class SystemA(System):
    def update(self, world, dt):
        pass

class SystemB(System):
    def update(self, world, dt):
        pass

world.register_system(SystemA, priority=10)
world.register_system(SystemB, priority=10)  # 相同优先级！
```

**正确做法**：

```python
world.register_system(SystemA, priority=10)
world.register_system(SystemB, priority=5)  # 不同优先级
```

---

## ⚡ 性能问题

### 问题 1：频繁创建对象

**现象**：内存占用高、GC 压力大

**错误示例**：

```python
class MySystem(System):
    def update(self, world, dt):
        # ❌ 每次 update 都创建新对象
        for i in range(100):
            new_component = MyComponent()
            pass
```

**正确做法**：

```python
class MyClass(System):
    def __init__(self, world):
        self._object_pool = Pool(MyComponent)  # 对象池
        ...
    
    def update(self, world, dt):
        # ✅ 复用以避免频繁 GC
        component = self._object_pool.get()
        try:
            # 处理逻辑
            pass
        finally:
            self._object_pool.put(component)
```

---

### 问题 2：遍历索引过大

**现象**：`get_components()` 遍历过多实体

**错误示例**：

```python
class SlowSystem(System):
    def update(self, world, dt):
        # ❌ 遍历所有实体，即使只需要一小部分
        for eid, component in world.get_components(PositionComponent):
            # 处理逻辑
            pass
```

**正确做法**：

```python
class OptimizedSlowSystem(System):
    def update(self, world, dt):
        # ✅ 使用空间索引（就近遍历）
        entities = world.spatial_index.query_region(
            x=50, y=50, radius=10, layer=0
        )
        for eid, entity in entities:
            pass
```

---

### 问题 3：缓存未使用

**现象**：频繁查询同一数据

**错误示例**：

```python
class UncachedSystem(System):
    def update(self, world, dt):
        # ❌ 每次都查询同一 World 对象
        for eid, component in world.get_components(HealthComponent):
            pass
```

**正确做法**：

```python
class CachedSystem(System):
    def __init__(self, world):
        self._cached_components = {}
    
    def update(self, world, dt):
        # ✅ 首次缓存，后续复用
        if world not in self._cached_components:
            self._cached_components[world] = {
                "components": world.get_components(HealthComponent),
            }
        for eid, component in self._cached_components[world]["components"]:
            pass
```

---

## 🐛 调试技巧

### 技巧 1：添加 Debug System（最后执行）

```python
class DebugSystem(System):
    @property
    def priority(self) -> int:
        return 100  # 最后执行，仅用于调试
    
    def update(self, world, dt):
        print(f"[Debug] Step: {dt} | Entities: {len(world.all_entities)}")
        
        for eid, comp in world.get_components(HealthComponent):
            print(f"  #{eid}: health={comp.health}")
        
        print("Systems registered:")
        for sys_type, sys in world._systems.items():
            print(f"  System: {sys_type.__name__} (priority={sys.priority})")
```

---

### 技巧 2：性能剖析

```python
# 运行模拟
cProfile.run('main.run_simulation(300)')

# 分析
p = pstats.Stat('cprofile.out')
p.sort_stats('cumulative').print_stats(20)
```

---

### 技巧 3：内存泄漏检测

```python
import tracemalloc

tracemalloc.start()
main.run_simulation(300)
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current} | Peak: {peak}")
tracemalloc.stop()
```

---

### 技巧 4：断点调试

```python
# 在系统中添加断点
def update(self, world, dt):
    if world.time.hour == 12 * 6:  # 第 72 小时
        breakpoint()  # Python 3.7+
        # 或在 VSCode 中：# 打断点 -> # 启用
```

---

### 技巧 5：日志系统

```python
import logging

logger = logging.getLogger(__name__)

def update(self, world, dt):
    logger.debug(f"Updating {type(self).__name__} at hour {world.time.hour}")
    if world.time.hour % 24 == 0:
        logger.info(f"Day {world.time.day_of_year} started")
```

---

## 📝 日志配置

### 生产环境配置

```python
# 日志级别：DEBUG=0, INFO=1, WARNING=2, ERROR=3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
```

**使用示例**：

```python
logger = logging.getLogger(__name__)

def update(self, world, dt):
    logger.debug("Debug message")  # 仅 DEBUG 级别
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

---

## 🔀 版本兼容性

### Python 版本

| Feature | Python 3.8+ | Python 3.9+ | Python 3.10+ |
|---------|------------|------------|-------------|
| `@dataclass` | ✅ | ✅ | ✅ |
| `dict.setdefault` | ✅ | ✅ | ✅ |
| `@field` (dataclass) | ✅ | - | - |
| `from __future__ import annotations` | ✅ | ✅ | ✅ |

**推荐版本**：Python 3.9+（支持所有特性且性能优）

---

## 🧾 内存泄漏

### 原因 1：未引用的组件对象

**排查**：

```python
import gc

# 运行 GC
gc.collect()

# 强制收集
gc.collect()

# 检查存活对象
gc.get_objects(limit=100)
```

**解决**：

```python
class Component(object):
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        cls._instances = cls._instances if hasattr(cls, '_instances') else set()
        instance = _instances.add(obj)
        return obj

    def __del__(self):
        if self in self._instances:
            self._instances.remove(obj)
```

---

### 原因 2：弱引用失效

**排查**：

```python
# 检查弱引用
weak.ref.weakened_key = []

# 检查是否有循环引用
try:
    gc.collect()
except Exception:
    pass
```

---

### 原因 3：未清理的对象池

**排查**：

```python
import os

# 检查临时文件
os.listdir("/tmp")
```

---

## ⚙️ 环境配置

### 本地开发环境

```bash
# 虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 虚拟路径
python main.py
python full_simulation.py
python weather_test.py

# 代码统计
python calculate_code_nums.py
```

---

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
```

---

### CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: python -m pydocstyle
```

---

## 🌱 植物/生物学系统常见问题

### 问题 8：植物不生长或不推进生命周期

**现象**：植物实体创建后，`LifeCycleComponent.stage` 始终为 `SEED`。

**排查方法**：

```python
# 检查 LifeCycleSystem 是否已注册
from biology.systems.life_cycle_system import LifeCycleSystem
if world.get_system(LifeCycleSystem) is None:
    print("❌ LifeCycleSystem 未注册！")

# 检查 GDD 累积
from biology.components.life_cycle_component import LifeCycleComponent
for eid, lc in world.get_components(LifeCycleComponent):
    print(f"#{eid}: GDD={lc.accumulated_gdd:.2f}, age={lc.age_hours:.0f}h, stage={lc.stage}")

# 检查环境是否有温度数据
from environment.environment_component import EnvironmentComponent
env = world.get_world_component(EnvironmentComponent)
if env and hasattr(env, 'air_temperature'):
    print(f"环境温度：{env.air_temperature:.1f}°C")
else:
    print("❌ 环境温度数据缺失！")
```

**常见原因**：
- LifeCycleSystem 未注册到 World
- `EnvironmentComponent.air_temperature` 缺失或为零（GDD 无法累积）
- `SpaceComponent` 缺失（生命周期系统不需要，但植物工厂要求）
- GDD 阈值配置过高导致长期无法突破

### 问题 9：遗传变异未生效

**现象**：子代基因与亲本完全相同，没有变异。

**排查方法**：

```python
from biology.components.genome_component import GenomeComponent

parent_genome = world.get_component(parent_id, GenomeComponent)
child_genome = world.get_component(child_id, GenomeComponent)

# 对比基因值
for pg, cg in zip(parent_genome.genes, child_genome.genes):
    diff = abs(pg.strength - cg.strength)
    if diff > 0.001:
        print(f"✅ {pg.name}: {pg.strength:.4f} → {cg.strength:.4f} (Δ={diff:.4f})")
    else:
        print(f"  {pg.name}: 无变化")

# 检查变异率
import random
for gene in child_genome.genes:
    print(f"{gene.name}: mutation_rate={gene.mutation_rate}")
    if gene.mutation_rate <= 0:
        print("  ⚠️ 变异率为零！")
```

**常见原因**：
- `PlantFactory.create_plant_from_genome()` 未调用 `genome.mutate()`
- 变异率默认为 0（检查 `Gene` 构造函数中 `mutation_rate` 参数）
- 使用 `create_plant()` 而非 `create_plant_from_genome()`（后者才会触发变异）

### 问题 10：植物过早死亡

**现象**：植物在发芽或生长初期就进入 DEAD 阶段。

**排查方法**：

```python
from biology.components.life_cycle_component import LifeCycleComponent, LifeStage

for eid, lc in world.get_components(LifeCycleComponent):
    if lc.stage == LifeStage.DEAD:
        print(f"#{eid}: 死亡时 GDD={lc.accumulated_gdd:.2f}, age={lc.age_hours:.0f}h")

        # 检查能量是否耗竭
        from biology.components.energy_component import EnergyComponent
        energy = world.get_component(eid, EnergyComponent)
        if energy:
            print(f"  能量: {energy.energy:.2f}")
```

**常见原因**：
- 环境温度极低导致呼吸消耗 > 光合产出
- `metabolism_rate` 基因值过高，呼吸消耗过快
- `death_system.py` 中 biomass 阈值过低或过高
- 光照为 0（夜间或极度阴蔽）且能量储备不足

### 问题 11：繁殖系统未产生子代

**现象**：植物处于 MATURE 阶段但无子代生成。

**排查方法**：

```python
from biology.systems.reproduction_system import ReproductionSystem

repro_system = world.get_system(ReproductionSystem)
if repro_system is None:
    print("❌ ReproductionSystem 未注册！")

# 检查植物是否处于 MATURE 阶段
for eid, lc in world.get_components(LifeCycleComponent):
    if lc.stage == LifeStage.MATURE:
        print(f"#{eid}: 已成熟，等待繁殖")

# 检查种子和扩散参数
genome = world.get_component(eid, GenomeComponent)
if genome:
    seed_gene = genome.get_gene("seed_production")
    disp_gene = genome.get_gene("dispersal_radius")
    print(f"  种子产量={seed_gene.strength:.1f}, 扩散半径={disp_gene.strength:.0f}")
```

**常见原因**：
- `SpaceComponent` 缺失（繁殖系统依赖空间定位来放置子代）
- `seed_production` 或 `dispersal_radius` 基因值为 0
- ReproductionSystem 优先级过低，在死亡系统之后执行

### 问题 12：衰老系统不生效

**现象**：植物进入 SENESCENCE 阶段后光合效率无变化。

```python
from biology.systems.senescence_system import SenescenceSystem

sen_system = world.get_system(SenescenceSystem)
if sen_system is None:
    print("❌ SenescenceSystem 未注册！")

from biology.components.growth_component import GrowthComponent
for eid, gc in world.get_components(GrowthComponent):
    lc = world.get_component(eid, LifeCycleComponent)
    if lc and lc.stage == LifeStage.SENESCENCE:
        print(f"#{eid}: 衰老中，光合效率={gc.photosynthesis_efficiency:.3f}")
```

---

## 📋 问题排查清单 (Checklist)

**快速查阅**：

- [ ] 1. 系统已注册
- [ ] 2. 双向索引一致
- [ ] 3. 优先级正确
- [ ] 4. 内存泄漏检测
- [ ] 5. 性能问题排查
- [ ] 6. 日志配置正确
- [ ] 7. 版本兼容性检查
- [ ] 8. 实体生命周期管理
- [ ] 9. 缓存使用
- [ ] 10. 对象池管理

---

## 🛠️ 工具推荐

### 性能分析工具

| 工具 | 用途 | 示例 |
|------|------|------|
| cProfile | 性能剖析 | `cProfile.run()` |
| Memory Profiler | 内存分析 | `memory_profiler` |
| tracemalloc | GC 追踪 | `tracemalloc.start()` |
| line_profiler | 代码行分析 | `@profile` 装饰器 |

### 调试工具

| 工具 | 用途 | 示例 |
|------|------|------|
| VSCode | 代码编辑 | `Ctrl+F` 快速查找 |
| pdb | 断点调试 | `breakpoint()` |
| IPython | 交互式调试 | `db()` |
| flake8 | 代码检查 | `flake8.pycode()` |

---

**版本**：v2.2  
**最后更新**：2026 年 5 月 28 日  
**维护者**：ECS Core Team  
**联系**：github@example.com
# 问题排查指南

> 常见问题、错误处理与调试技巧。

---

## 常见错误

### System 未注册

```python
# ❌ 忘记注册
class MySystem(System):
    def update(self, world, dt):
        print("Running!")

# ✅ 正确做法
world.add_system(MySystem())
```

### Component 类型不匹配

```python
# ✅ 确保遍历正确的 Component 类型
for entity, health in world.get_components(HealthComponent):
    if health.current_hp <= 0:
        world.remove_entity(entity)
```

### Entity 生命周期管理

```python
# ✅ 正确删除实体（World 自动清理组件）
world.remove_entity(entity)

# ✅ 删除前检查存在性
if world.has_entity(entity):
    world.remove_entity(entity)
```

---

## 性能问题

### 频繁创建对象

```python
# ❌ 每次 update 都创建新对象
def update(self, world, dt):
    for i in range(100):
        new_component = MyComponent()  # 每次都创建

# ✅ 使用对象池或复用
class MySystem(System):
    def __init__(self):
        self._pool = []
```

### 遍历索引过大

```python
# ❌ 遍历所有实体
for entity, pos in world.get_components(PositionComponent):
    pass

# ✅ 使用空间索引
index = world.get_spatial_index()
nearby = index.query_radius(x, y, radius)
```

---

## 调试技巧

### 添加调试输出

```python
class DebugSystem(System):
    priority = 100  # 最后执行

    def update(self, world, dt):
        print(f"[Debug] Entities: {len(world.entities)}")
        for eid, comp in world.get_components(HealthComponent):
            print(f"  #{eid}: health={comp.health}")
```

### 性能剖析

```python
import cProfile
cProfile.run('run_simulation()')
```

### 内存泄漏检测

```python
import tracemalloc
tracemalloc.start()
main.run_simulation(300)
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current} | Peak: {peak}")
tracemalloc.stop()
```

### 断点调试

```python
def update(self, world, dt):
    if world.get_time().hour == 72:
        breakpoint()  # Python 3.7+
```

---

## 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Info message")
logger.debug("Debug message")
```

---

## 植物/生物学系统常见问题

### 植物不生长

```python
# 检查 LifeCycleSystem 是否已注册
if world.get_system(LifeCycleSystem) is None:
    print("❌ LifeCycleSystem 未注册！")

# 检查 GDD 累积
for eid, lc in world.get_components(LifeCycleComponent):
    print(f"#{eid}: GDD={lc.accumulated_gdd:.2f}, stage={lc.stage}")

# 检查环境温度
env = world.get_environment()
print(f"环境温度：{env.air_temperature:.1f}°C")
```

### 遗传变异未生效

```python
parent = world.get_component(parent_id, GenomeComponent)
child = world.get_component(child_id, GenomeComponent)

for pg, cg in zip(parent.genes, child.genes):
    diff = abs(pg.strength - cg.strength)
    if diff > 0.001:
        print(f"✅ {pg.name}: {pg.strength:.4f} → {cg.strength:.4f}")
```

---

## 问题排查清单

- [ ] 系统已注册到 World
- [ ] 双向索引一致
- [ ] 优先级正确
- [ ] 内存泄漏检测
- [ ] 性能问题排查
- [ ] 日志配置正确
- [ ] 实体生命周期管理

---

## 工具推荐

| 工具 | 用途 |
|------|------|
| cProfile | 性能剖析 |
| tracemalloc | GC 追踪 |
| pdb / breakpoint() | 断点调试 |
| logging | 日志记录 |

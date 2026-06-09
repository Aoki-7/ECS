# ECS 世界模拟系统 — 架构总览

> 版本: v3.0 (2026-06-08)
> 文件数: 496 个 Python 文件
> 测试数: 260 个（全部通过）

---

## 目录结构

```
ECS/
├── core/                    # 核心框架（零外部依赖）
│   ├── entity.py, component.py, system.py, world.py
│   ├── event_bus.py, spatial_index.py
│   └── tests/               # 30+ 测试
├── application/             # 应用层
│   ├── simulation_loop.py, world_builder.py
├── config/                  # 系统优先级表
├── space/                   # 空间索引与坐标
├── time_module/             # 时间推进
├── environment/             # 环境系统（15 系统 DAG 管线）
├── biology/                 # 基因/生长/生命周期/竞争/物种形成
├── animal/                  # 动物模块（27 文件，10 系统，25 测试）
├── human/                   # 人类模块（~30 文件，5 测试）
├── plant/                   # 植物模块（~15 文件，6 测试）
├── memory_layer/            # 统一记忆层（15 文件，53 测试）
├── save_load/               # 统一存档（5 文件，8 测试）
├── presentation/            # 可视化工具（2 文件，9 测试）
└── doc/                     # 设计文档
```

---

## 核心设计原则

### 1. 分层架构

```
┌─────────────────────────────────────────┐
│  presentation / application              │
├─────────────────────────────────────────┤
│  animal / human / plant / civilization   │
├─────────────────────────────────────────┤
│  memory_layer / space / environment      │
├─────────────────────────────────────────┤
│  core (entity / component / system /     │
│       world / event_bus / spatial_index) │
└─────────────────────────────────────────┘
```

### 2. ECS 核心模式

| 概念 | 实现 |
|------|------|
| Entity | 不可变 ID，仅作为标识 |
| Component | `@dataclass(slots=True)` 纯数据 |
| System | `update(world, dt)` 逻辑处理 |
| World | 统一管理器，双向索引 |
| EventBus | 全局单例，解耦事件通信 |
| SpatialIndex | 均匀网格，O(1)~O(k) 查询 |

### 3. 系统执行模型

```python
for system in sorted_systems:
    if system.enabled and tick % system.tick_interval == 0:
        system.update(world, dt * tick_interval)
```

---

## 统一记忆层（Memory Layer）

### 设计哲学

独立于 ECS 的元层服务，实现"物理层 → 客观记忆 → 主观记忆"的三层模型。

```
Entity（石头E42） → Concept（"石头E42"） → MemoryInstance（生物A的记忆）
   （可消亡）          （实体消亡后仍存在）    （个性化、可能扭曲）
```

### 核心特性

| 特性 | 实现 |
|------|------|
| 独立于实体 | 实体销毁后 Concept 标记 `is_active=False` |
| 主客观分离 | `Concept`（客观事实） vs `MemoryInstance`（主观观点） |
| 记忆传播 = 重新生成 | `narrate_memory()` 基于描述 + 认知框架重新生成 |
| 结构化感官 | `SensoryDescription`（形状/颜色/质地/大小/气味/声音/温度） |
| 认知框架 | `CognitiveFramework`（注意力/解释/威胁/重构滤镜） |
| 记忆扭曲 | `MemoryDistortionEngine`（传话游戏效应） |
| 持久化 | `MemoryPersistence`（JSON 存档/读档/自动保存） |

---

## 性能优化（v3.0）

### 空间索引（SpatialIndex）

```python
from core.spatial_index import SpatialIndex

index = SpatialIndex(cell_size=50.0)
index.add_entity(entity_id, x, y)
nearby = index.query_radius(x, y, radius)  # O(1) ~ O(k)
```

**基准**：10,000 实体创建 < 5s，空间索引 vs 暴力查询 **5x+ 加速**

---

## 模块状态

| 模块 | 文件数 | 测试数 | 状态 |
|------|--------|--------|------|
| core | 9 | 30+ | ✅ 稳定 |
| animal | 27 | 25 | ✅ 重构完成 |
| memory_layer | 15 | 53 | ✅ 完成 |
| human | ~30 | 5 | ✅ 已集成 |
| plant | ~15 | 6 | ✅ 已增强 |
| save_load | 5 | 8 | ✅ 已统一 |
| presentation | 2 | 9 | ✅ 已完成 |
| environment | ~20 | 若干 | ⚠️ 需关注 |

---

## 技术债务

| 债务 | 优先级 | 状态 |
|------|--------|------|
| `memory/` 旧系统 | 中 | ✅ 已清理 |
| `except:pass` | 高 | ✅ 已清理 |
| `dt` 类型注解 | 中 | ✅ 已清理 |
| 各模块 README | 低 | ⚠️ 待补充 |
| API 文档自动生成 | 低 | ⚠️ 待实现 |

---

## 版本历史

| 版本 | 日期 | 主要特性 |
|------|------|----------|
| v1.0 | 2026-05 | ECS 核心框架 |
| v1.5 | 2026-05 | 生物模块 |
| v2.0 | 2026-06-08 | Animal 重构 + 记忆层骨架 |
| v2.1 | 2026-06-08 | 架构文档 + 清理 |
| v2.2 | 2026-06-08 | Human 集成 + Plant 增强 |
| v2.3 | 2026-06-08 | 存档统一 + 旧系统迁移 |
| v3.0-alpha | 2026-06-08 | 事件总线 |
| v3.0-beta | 2026-06-08 | 可视化工具 |
| **v3.0** | **2026-06-08** | **性能优化 + 正式发布** |

---

## 快速开始

```python
from core.world import World
from core.event_bus import EventBus
from memory_layer import MemoryLayer, SensoryDescription, SubjectType

world = World()
entity = world.create_entity()

memory_layer = world.get_memory_layer()
event_bus = world.get_event_bus()

concept = memory_layer.register_entity(
    entity_id=entity.id,
    entity_type="stone",
    description=SensoryDescription(shape="圆形", color="灰色"),
)

memory_layer.record_contact(
    subject_id=1,
    subject_type=SubjectType.ANIMAL,
    entity_id=entity.id,
    contact_type="visual",
    intensity=0.8,
)

world.update(dt=1.0)
```

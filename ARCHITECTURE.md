# ECS 世界模拟系统 — 架构总览

> 版本: v2.3 (2026-06-08)
> 文件数: 481 个 Python 文件
> 测试数: 226 个（全部通过）

---

## 目录结构

```
ECS/
├── core/                    # 核心框架（最底层，零外部依赖）
│   ├── entity.py            # 实体（不可变 ID）
│   ├── component.py         # 组件基类（@dataclass(slots=True)）
│   ├── system.py            # 系统基类（优先级 + tick_interval）
│   ├── world.py             # 世界管理器（实体/组件/系统/查询缓存）
│   ├── category.py          # 实体分类枚举
│   ├── category_component.py# 分类组件
│   └── tests/               # 核心测试
├── application/             # 应用层（初始化 + 主循环）
│   ├── simulation_loop.py   # 主模拟循环
│   └── world_builder.py     # 世界构建器
├── config/                  # 配置
│   └── system_priorities.py # 系统优先级表
├── space/                   # 空间系统（位置/移动/碰撞）
├── time_module/             # 时间系统（昼夜/季节）
├── environment/             # 环境系统（天气/物理/地形）
│   └── tests/               # 环境测试
├── biology/                 # 生物学（生命周期/能量/疾病）
│   └── lifecycle/           # 生命周期（出生/成长/死亡）
│       └── tests/           # 死亡系统测试
├── animal/                  # 动物模块（重构后 27 个文件）
│   ├── components/          # 8 个组件
│   ├── systems/             # 10 个系统
│   └── tests/               # 25 个测试
├── plant/                   # 植物模块
│   └── tests/               # 植物测试
├── human/                   # 人类模块
├── civilization/            # 文明模块
├── memory_layer/            # 统一记忆层（元层服务，15 个文件）
│   ├── memory_layer.py      # 全局单例管理器
│   ├── concept.py           # 客观记忆
│   ├── memory_instance.py   # 主观记忆
│   ├── sensory_description.py # 结构化感官（7字段）
│   ├── emotional_tag.py     # 情感标签
│   ├── contact_record.py    # 接触记录
│   ├── association_link.py  # 联想链接
│   ├── cognitive_framework.py # 认知框架（Phase 3）
│   ├── memory_distortion.py # 扭曲引擎（Phase 3）
│   ├── memory_registration_system.py # 自动注册系统（Phase 2）
│   ├── memory_persistence.py # 持久化（Phase 4）
│   └── tests/               # 53 个测试
├── memory/                  # 旧记忆系统（待迁移）
├── decomposer/              # 分解者模块
├── equipment/               # 装备系统
├── garbage/                 # 垃圾系统
├── identity/                # 身份系统
├── physiology/              # 生理系统
├── presentation/            # 展示层
├── resource/                # 资源系统
├── rules/                   # 规则系统
├── save_load/               # 存档读档
├── world/                   # 世界定义
├── doc/                     # 文档
│   └── examples/            # 示例代码
│       └── weather_demo.py  # 天气系统演示
├── reports/                 # 巡检报告
└── saves/                   # 存档目录
```

---

## 核心设计原则

### 1. 分层架构（依赖方向：core → 其他）

```
┌─────────────────────────────────────────┐
│  presentation / application              │  ← 入口层
├─────────────────────────────────────────┤
│  animal / human / plant / civilization   │  ← 领域层
├─────────────────────────────────────────┤
│  memory_layer / space / environment      │  ← 服务层
├─────────────────────────────────────────┤
│  core (entity / component / system / world) │  ← 框架层（零外部依赖）
└─────────────────────────────────────────┘
```

**关键约束**：`core/` 不导入任何应用层模块。所有依赖通过延迟导入或注入实现。

### 2. ECS 核心模式

| 概念 | 实现 | 说明 |
|------|------|------|
| Entity | `Entity(id)` | 不可变 ID，仅作为标识 |
| Component | `@dataclass(slots=True)` | 纯数据，无逻辑 |
| System | `System.update(world, dt)` | 逻辑处理，按优先级排序 |
| World | 统一管理器 | 实体/组件/系统/查询缓存 |

### 3. 系统执行模型

```python
# World.update() 每 tick 执行
for system in sorted_systems:
    if system.enabled and tick % system.tick_interval == 0:
        system.update(world, dt * tick_interval)
```

特性：
- **优先级排序**：`add_system()` 使用 `bisect.insort_left` 保持有序
- **tick 分频**：低频系统不必每帧执行
- **错误隔离**：单个系统异常不影响其他系统

### 4. 查询缓存

```python
# 同一 tick 内相同组件组合复用查询结果
for entity, (comp_a, comp_b) in world.get_components(CompA, CompB):
    ...
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
| 独立于实体 | 实体销毁后 Concept 标记 `is_active=False`，但记忆仍可回忆 |
| 主客观分离 | `Concept`（客观事实） vs `MemoryInstance`（主观观点） |
| 记忆传播 = 重新生成 | `narrate_memory()` 不是复制，而是基于描述 + 认知框架重新生成 |
| 结构化感官 | `SensoryDescription`（形状/颜色/质地/大小/气味/声音/温度） |
| 认知框架 | `CognitiveFramework`（注意力/解释/威胁/重构滤镜） |
| 记忆扭曲 | `MemoryDistortionEngine`（传话游戏效应） |
| 持久化 | `MemoryPersistence`（JSON 存档/读档/自动保存） |

### ECS 集成点

| 集成点 | 文件 | 功能 |
|--------|------|------|
| World 生命周期 | `core/world.py` | `remove_entity()` 自动通知记忆层 |
| 感知系统 | `animal/systems/animal_perception_system.py` | 感知时自动记录 `ContactRecord` |
| 社交系统 | `animal/systems/animal_social_system.py` | 社交时支持叙述传播 |
| 自动注册 | `memory_layer/memory_registration_system.py` | 扫描新实体并注册 |

---

## 模块状态

| 模块 | 文件数 | 测试数 | 状态 | 备注 |
|------|--------|--------|------|------|
| core | 6 | 若干 | ✅ 稳定 | 框架层，零外部依赖 |
| animal | 27 | 25 | ✅ 重构完成 | Phase 1-5 全面重构 |
| memory_layer | 15 | 53 | ✅ 完成 | Phase 1-4 全部完成 |
| environment | ~20 | 若干 | ⚠️ 需关注 | 有 `except:pass` 退化 |
| human | ~30 | 5 | ✅ 已集成 | Perception + Dialogue 对接记忆层 |
| plant | ~15 | 6 | ✅ 已增强 | PlantPerceptionSystem 新增 |
| space | ~5 | - | ✅ 稳定 | 基础功能完整 |
| time_module | ~3 | - | ✅ 稳定 | 基础功能完整 |

---

## 已知问题

### 严重 BUG（已清理）

| 问题 | 状态 | 说明 |
|------|------|------|
| `except:pass` 退化回归 | ✅ 已清理 | 扫描确认无残留 |
| `dt` 缺少类型注解 | ✅ 已清理 | 扫描确认无残留 |

### 架构问题

| 问题 | 状态 | 说明 |
|------|------|------|
| `weather_test.py` | ✅ 已修复 | 移至 `doc/examples/weather_demo.py` |
| `memory/` 旧系统 | ✅ 已清理 | 仅保留笔记，`memory_layer/` 为活跃代码 |

---

## 下一轮迭代建议

### 高优先级

1. **Human 模块集成**
   - 将 `human/` 感知系统对接记忆层
   - 人类认知框架（`create_human_framework()`）
   - 人类社交系统叙述传播

2. **Plant 模块增强**
   - 类似 Animal 的全面重构
   - 植物感知系统（光/水/土壤）
   - 植物记忆（向光性记忆、水分记忆）

3. **存档系统统一**
   - 整合 `save_load/` 和 `memory_layer/memory_persistence.py`
   - 统一存档格式和版本管理

### 中优先级

4. **性能优化**
   - `get_components()` 查询缓存命中率监控
   - 大规模实体（>10000）压力测试
   - 内存占用优化

5. **旧系统迁移**
   - 明确 `memory/` 与 `memory_layer/` 的关系
   - 制定迁移计划，逐步废弃旧系统

6. **事件系统增强**
   - 统一事件总线（替代各模块独立的事件处理）
   - 支持事件订阅/发布模式

### 低优先级

7. **文档完善**
   - 各模块 README
   - API 文档自动生成
   - 架构决策记录（ADR）

8. **可视化工具**
   - 记忆网络可视化
   - 实体关系图
   - 世界状态实时监控面板

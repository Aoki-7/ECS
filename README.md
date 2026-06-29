# ECS 世界模拟系统

> **底层连续物理量驱动世界演化** —— 基于 ECS（Entity-Component-System）架构的多层级世界模拟引擎。
>
> 版本：v4.0　|　Python 文件：723　|　代码：73,831 行　|　测试：612 passed, 1 skipped

---

## 🎯 核心理念

**"连续物理量 + 实时视图 + 主客观分离"**

- 底层只有连续物理量的自然演化（温度、光照、降水、能量、营养）
- 所有离散状态（晴/雨/季节/事件）都是物理量的实时视图
- **信息损失机制**：物理量连续，感知/认知离散——生物只能采样有限信息
- 物理驱动而非硬编码状态机驱动；自然演化优于预设计

```
太阳位置 → 大气顶辐射 → 连续天气物理量 → 地表光照 → 环境同步
                                              ↓
                                      生物光合 → 能量分配 → 形态生长
                                              ↓
                                      生命周期 → 繁殖/衰老/死亡 → 分解 → 土壤养分
                                              ↓
                                      人类感知 → 认知/情绪/决策 → 社会/文明
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 核心引擎：无第三方依赖（纯标准库）
- Web API：`pip install fastapi uvicorn`（可选）

### 运行模式

```bash
# 1. 基础模拟 — 轻量启动，核心系统
python main.py

# 2. 全面模拟 — 全系统注册（164 个系统），完整环境管线
python full_simulation.py

# 3. 纯生态模拟 — 仅植物/动物/分解者
python ecosystem_main.py

# 4. Web API 服务（FastAPI）
python -m uvicorn api.main:app --reload
# 访问 http://127.0.0.1:8000/docs
```

### 运行测试

```bash
# 全量测试（约 20 秒）
python -m pytest -q

# 核心测试（快速）
python -m pytest tests/core/ -q

# 带覆盖率
python -m pytest --cov=core --cov-report=term-missing
```

---

## 🏗️ 架构概览

### ECS 核心（v4.0）

```
┌──────────────────── World ────────────────────┐
│  ┌──────────── Entity ──────────────┐         │
│  │  ┌────────── Component ─────────┐ │         │
│  │  │ (纯数据存储，dataclass slots) │ │         │
│  │  └──────────────────────────────┘ │         │
│  └────────────────────────────────────┘         │
│           ↓ ArchetypeStore（按组件类型组合分桶） │
│  ┌────────────────── System ─────────────────┐ │
│  │   (纯逻辑处理，priority + tick_interval)   │ │
│  └───────────────────────────────────────────┘ │
│           ↓ WorldEventBus（每个 World 独立）    │
└────────────────────────────────────────────────┘
```

| 类型 | 职责 | 关键特性 |
|------|------|----------|
| **Entity** | 标识符 + 代际（防悬挂引用） | `id=42, generation=3` |
| **Component** | 纯数据存储 | `@dataclass(slots=True)` |
| **System** | 纯逻辑处理，按优先级与间隔调度 | `update(world, dt)` |
| **World** | 双向索引中心，支持多组件联合查询 | `get_components(A, B)` |
| **ArchetypeStore** | 按组件类型组合分桶，查询缓存 | 精确失效，62x 性能提升 |
| **WorldEventBus** | 每个世界独立的事件总线 | `subscribe/publish` |
| **SpatialIndex** | 均匀网格空间索引 | `query_radius(x, y, r)` |

### 模块分层

| 层级 | 模块 | 说明 |
|------|------|------|
| **入口层** | `presentation/` `application/` | 可视化 + 主循环 + 系统注册 |
| **API 层** | `api/` | FastAPI Web 服务（实体 CRUD、世界查询） |
| **领域层** | `animal/` `human/` `plant/` `civilization/` `biology/` | 生物行为 + 生命周期 + 文明 |
| **服务层** | `memory_layer/` `space/` `environment/` | 记忆 + 空间 + 环境 |
| **框架层** | `core/` | ECS 引擎（零外部依赖） |
| **持久层** | `save_load/` | JSON 序列化 + 增量存档 + SQLite |

---

## 📂 目录结构

```
ECS/
├── core/                          # ECS 核心引擎
│   ├── world.py                   # 世界中心，兼容 v3.9 API
│   ├── archetype_store.py         # 查询缓存与分桶
│   ├── system_scheduler.py        # 系统调度（优先级 + 间隔）
│   ├── entity_manager.py          # 实体生命周期管理
│   └── systems/                   # 核心系统（配置等）
├── api/                           # FastAPI Web 服务
│   ├── main.py
│   ├── routers/entity.py
│   └── routers/world.py
├── application/                   # 应用层（模拟循环 + 系统注册）
│   ├── system_registry.py         # 自动扫描注册 164 个系统
│   └── full_simulation.py
├── space/                         # 空间系统（碰撞/网格/索引）
├── time_module/                   # 时间系统（昼夜/季节/历法）
├── environment/                   # 环境系统（大气/天气/季节/气候/土壤/地形）
├── biology/                       # 生物学（遗传/生命周期/生态学/种群）
│   ├── lifecycle/                 # 生命周期子系统（生长/出生/衰老/繁殖）
│   └── systems/                   # 兼容层转发（已迁移至 lifecycle）
├── plant/                         # 植物层
├── animal/                        # 动物层（10 系统生态模拟）
├── human/                         # 人类层（生理/认知/社交/行为/经济/战斗）
├── civilization/                  # 文明层（社会/技术/文化/政治）
├── memory_layer/                  # 统一记忆层（元层服务）
├── save_load/                     # 统一存档系统（JSON + SQLite）
├── presentation/                  # 可视化工具
├── doc/                           # 项目文档
│   ├── architecture/              # 架构文档
│   ├── design/                    # 设计模式
│   └── troubleshooting/           # 问题排查
├── reports/                       # 各类报告
│   ├── releases/                  # 版本发布报告
│   ├── inspections/               # 巡检报告
│   └── analysis/                  # 分析类报告
└── tests/                         # 测试（612 passed）
```

---

## ⚡ 性能数据

| 指标 | 数值 | 说明 |
|------|------|------|
| 组件查询 | 52,258 /s | `get_components()` 带缓存，62x 提升 |
| 全量测试 | ~20 s | 612 测试用例 |
| 注册系统 | 164 个 | 自动扫描，按优先级调度 |
| 系统调度间隔 | 支持 1~N tick | `tick_interval` 控制 |

---

## 📖 相关文档

| 文档 | 内容 |
|------|------|
| [`doc/architecture/ARCHITECTURE.md`](doc/architecture/ARCHITECTURE.md) | 完整架构文档、模块状态、技术债务 |
| [`doc/USER_MANUAL.md`](doc/USER_MANUAL.md) | 使用说明、API 参考、常见问题 |
| [`doc/ROADMAP.md`](doc/ROADMAP.md) | 里程碑与迭代计划 |
| [`doc/CHANGELOG.md`](doc/CHANGELOG.md) | 版本更新日志 |
| [`doc/architecture/ARCHITECTURE_DIAGRAM.md`](doc/architecture/ARCHITECTURE_DIAGRAM.md) | 模块架构图 |
| [`doc/architecture/ARCHITECTURE_OVERVIEW.md`](doc/architecture/ARCHITECTURE_OVERVIEW.md) | 全架构总览 |
| [`doc/design/DESIGN_PATTERNS.md`](doc/design/DESIGN_PATTERNS.md) | ECS 架构中的设计模式 |
| [`doc/troubleshooting/TROUBLESHOOTING.md`](doc/troubleshooting/TROUBLESHOOTING.md) | 常见问题排查 |

---

## 📝 版本历史（近期）

| 版本 | 日期 | 重点 |
|------|------|------|
| v4.0 | 2026-06 | 重构：Archetype 缓存、自动扫描注册、EventBus 统一、API 兼容层、空壳系统补完 |
| v3.9 | 2026-05 | 迁移：biology 模块重组为 lifecycle 子系统；System 纯工具化 |
| v3.0.1 | 2026-04 | 稳定：增量存档、性能优化、360+ 测试 |
| v3.0 | 2026-03 | 大重构：ECS 核心重写、EventBus、SpatialIndex、MemoryLayer |

---

## 📜 许可证

MIT License

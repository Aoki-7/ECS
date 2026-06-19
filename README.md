# ECS 世界模拟系统

> **底层连续物理量驱动世界演化** —— 基于 ECS（Entity-Component-System）架构的多层级世界模拟引擎。
>
> 版本：v3.0　|　Python 文件：496　|　测试：260（全部通过）

---

## 🎯 核心理念

**"连续物理量 + 实时视图"**

- 底层只有连续物理量的自然演化（温度、光照、降水、能量、营养）
- 所有离散状态（晴/雨/季节/事件）都是物理量的实时视图
- 物理驱动而非硬编码状态机驱动

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
- 无第三方依赖（纯标准库）

### 三种运行模式

```bash
# 1. 基础模拟 — 轻量启动，核心系统
python main.py

# 2. 全面模拟 — 全系统注册，完整环境管线
python full_simulation.py

# 3. 纯生态模拟 — 仅植物/动物/分解者
python ecosystem_main.py
```

### 运行测试

```bash
python -m pytest
```

---

## 🏗️ 架构概览

### ECS 核心

```
┌──────────────────── World ────────────────────┐
│  ┌──────────── Entity ──────────────┐         │
│  │  ┌────────── Component ─────────┐ │         │
│  │  │ (纯数据存储，dataclass)       │ │         │
│  │  └──────────────────────────────┘ │         │
│  └────────────────────────────────────┘         │
│           ↓ 双向索引                            │
│  ┌────────────────── System ─────────────────┐ │
│  │   (纯逻辑处理，priority + tick_interval)   │ │
│  └───────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

| 类型 | 职责 | 关键接口 |
|------|------|----------|
| **Entity** | 标识符 + 代际（防悬挂引用） | `id=42, generation=3` |
| **Component** | 纯数据存储 | `@dataclass(slots=True)` |
| **System** | 纯逻辑处理，按优先级与间隔调度 | `update(world, dt)` |
| **World** | 双向索引中心，支持多组件联合查询 | `get_components(A, B)` |
| **EventBus** | 全局单例事件总线（v3.0） | `subscribe/publish` |
| **SpatialIndex** | 均匀网格空间索引（v3.0） | `query_radius(x, y, r)` |

### 模块分层

| 层级 | 模块 | 说明 |
|------|------|------|
| **入口层** | `presentation/` `application/` | 可视化 + 主循环 |
| **领域层** | `animal/` `human/` `plant/` `civilization/` | 生物行为模拟 |
| **服务层** | `memory_layer/` `space/` `environment/` | 记忆 + 空间 + 环境 |
| **框架层** | `core/` | ECS 引擎（零外部依赖） |

---

## 📂 目录结构

```
ECS/
├── core/                   # ECS 核心引擎
├── application/            # 应用层（模拟循环）
├── space/                  # 空间系统
├── time_module/            # 时间系统
├── environment/            # 环境系统（大气/天气/季节/气候/土壤/地形）
├── biology/                # 生物学（遗传/生长/免疫/生态学/种群）
├── plant/                  # 植物层
├── animal/                 # 动物层（10 系统生态模拟）
├── human/                  # 人类层（生理/认知/社交/行为/经济/战斗）
├── memory_layer/           # 统一记忆层（元层服务）
├── save_load/              # 统一存档系统
├── presentation/           # 可视化工具
├── doc/                    # 项目文档
│   ├── README_WEB.md       # Web 开发套件说明
│   ├── CHANGELOG.md        # 更新日志
│   ├── ROADMAP.md          # 迭代路线图
│   ├── USER_MANUAL.md      # 使用说明
│   ├── architecture/       # 架构文档
│   │   ├── ARCHITECTURE.md
│   │   ├── ARCHITECTURE_DIAGRAM.md
│   │   ├── ARCHITECTURE_OVERVIEW.md
│   │   └── DESIGN_v4.0_ARCHITECTURE_REFACTOR.md
│   ├── design/             # 设计文档
│   │   └── DESIGN_PATTERNS.md
│   └── troubleshooting/    # 问题排查
│       └── TROUBLESHOOTING.md
├── reports/                # 各类报告
│   ├── releases/           # 版本发布报告
│   ├── inspections/        # 巡检报告
│   ├── updates/            # 更新报告
│   ├── simulations/        # 模拟/测试/可视化报告
│   └── analysis/           # 分析类报告
└── README.md               # 本文件
```

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
| [`doc/README_WEB.md`](doc/README_WEB.md) | Web 开发套件说明 |
| [`animal/README.md`](animal/README.md) | Animal 模块文档 |
| [`memory_layer/README.md`](memory_layer/README.md) | 统一记忆层文档 |

---

## 📜 许可证

MIT License

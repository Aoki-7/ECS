# ECS 世界模拟系统

> **底层连续物理量驱动世界演化** —— 一个基于 ECS（Entity-Component-System）架构的多层级世界模拟引擎。
>
> 版本：v2.3　|　Python 文件：481　|　测试：226（全部通过）

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
# 1. 基础模拟 — 轻量启动，核心系统，适合快速调试
python main.py

# 2. 全面模拟 — 全系统注册，完整环境管线 + 资源腐败 + 文明演进
python full_simulation.py

# 3. 纯生态模拟 — 仅植物/动物/分解者，不含人类与文明
python ecosystem_main.py
```

输出示例：
```
[Run] 模拟: 1000 步 × 1.0h
  Step    0/1000 | 实体:120 人口:10 食物:80 水源:80   0.0步/s
  Step  100/1000 | 实体:156 人口:12 食物:72 水源:81  48.5步/s
...
[Done] 实体:203 人口:15 食物:65 水源:78 文明:tribal  52步/s
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
| **Component** | 纯数据存储 | `@dataclass class EnergyComponent` |
| **System** | 纯逻辑处理，按优先级与间隔调度 | `update(world, dt)` |
| **World** | 双向索引中心，支持多组件联合查询 | `get_components(A, B)` |

### 模块分层（当前真实结构）

| 层级 | 模块 | 说明 |
|------|------|------|
| **核心框架** | `core/` | ECS 引擎（Entity/Component/System/World/分类） |
| **配置** | `config/` | 系统优先级表、执行间隔常量 |
| **应用层** | `application/` | 模拟循环编排、世界构建器 |
| **基础设施** | `space/` `time_module/` | 空间索引与坐标、时间推进（年/日/时） |
| **环境** | `environment/` | 大气、天气物理、光照场、季节、气候、土壤、地形、连续体同步 |
| **生物** | `biology/` | 基因表达、生长、形态、营养、免疫、竞争、生命周期、种群动态、物种形成 |
| **植物** | `plant/` | 物种预设、工厂、光合作用、水分吸收、种子扩散、地形适应 |
| **动物** | `animal/` | 物种预设、工厂、感知、需求、社交、领地、迁徙、学习、记忆、捕食、啃食 |
| **人类** | `human/` | 生理、认知（感知→情绪→思维→目标→决策）、社交（配对/部落/领地/忠诚）、生存、行为、经济、战斗 |
| **生理** | `physiology/` | 代谢、水分、体温、疲劳、毒性、健康 |
| **文明** | `civilization/` | 科技树、建筑、贸易、资源采集 |
| **资源** | `resource/` | 食物、水、木材、石头、金属（含腐败/风化/氧化） |
| **规则** | `rules/` | 资源转换、技能提升 |
| **装备** | `equipment/` | 装备工厂、所有权 |
| **身份** | `identity/` | 名称、生物属性、社交身份 |
| **记忆层** | `memory_layer/` | 统一记忆系统（感知记录、关联、情感标签、认知框架、记忆扭曲、持久化） |
| **死亡归档** | `death_archive/` | 死亡事件记录与存档 |
| **分解者** | `decomposer/` | 尸体与有机质分解 |
| **垃圾** | `garbage/` | 垃圾清理 |
| **存档** | `save_load/` | 统一存档/读档（World + MemoryLayer 序列化） |
| **展示** | `presentation/` | 人类观察面板与信息输出 |

---

## 🔄 关键系统管线

### 环境管线（DAG）

```
太阳辐射 → 大气物理 → 天气场 → 季节/气候 → 土壤/地形 → 环境同步 → 资源再生
```

### 生物管线

```
基因表达 → 生态竞争 → 光合/生长 → 形态更新 → 营养代谢 → 生命周期推进
    → 衰老/损伤/突变 → 繁殖/种子扩散 → 免疫/感染 → 死亡判定
```

### 人类管线

```
感知 → 情绪 → 思维 → 目标 → 决策 → 规划 → 动作调度
  → 搜索/移动/采集/进食/社交 → 部落/领地/忠诚 → 文明演进
```

### 生态闭环（纯生态模式）

```
植物（光合作用）→ 食草动物（啃食）→ 食肉动物（捕食）→ 尸体 → 分解者 → 土壤养分 → 植物
```

---

## 📂 目录结构

```
ECS/
├── core/                   # ECS 核心引擎
├── application/            # 应用层（模拟循环）
├── config/                 # 全局配置（优先级/间隔）
├── space/                  # 空间系统
├── time_module/            # 时间系统
├── environment/            # 环境系统（大气/天气/季节/气候/土壤/地形/光照）
├── biology/                # 生物学（遗传/生长/免疫/生态学/种群）
├── plant/                  # 植物层
├── animal/                 # 动物层
├── human/                  # 人类层（生理/认知/社交/行为/经济/战斗）
├── physiology/             # 生理系统
├── civilization/           # 文明系统
├── resource/               # 资源系统（食物/水/木材/石头/金属）
├── rules/                  # 规则系统
├── equipment/              # 装备系统
├── identity/               # 身份系统
├── memory_layer/           # 统一记忆层
├── death_archive/          # 死亡归档
├── decomposer/             # 分解者
├── garbage/                # 垃圾清理
├── save_load/              # 存档系统
├── presentation/           # 展示面板
│
├── main.py                 # 基础模拟入口
├── full_simulation.py      # 全面模拟入口
├── ecosystem_main.py       # 纯生态模拟入口
│
├── doc/                    # 设计文档
│   ├── PROJECT_PRINCIPLES.md
│   ├── DESIGN_PATTERNS.md
│   ├── DESIGN_SUMMARY.md
│   ├── DEVELOPER_GUIDE.md
│   ├── architecture.md
│   └── TROUBLESHOOTING.md
├── reports/                # 巡检与更新报告
├── README.md               # 本文件
├── ARCHITECTURE.md         # 架构总览
├── ROADMAP.md              # 迭代路线图
└── CHANGELOG.md            # 更新日志
```

---

## 📖 相关文档

| 文档 | 内容 |
|------|------|
| [`doc/PROJECT_PRINCIPLES.md`](doc/PROJECT_PRINCIPLES.md) | 设计理念、ECS 架构选择、技术决策 |
| [`doc/DESIGN_PATTERNS.md`](doc/DESIGN_PATTERNS.md) | 工厂、观察者、策略、命令等 20+ 设计模式 |
| [`doc/DESIGN_SUMMARY.md`](doc/DESIGN_SUMMARY.md) | Emitter 风格设计总结、生态模型 |
| [`doc/DEVELOPER_GUIDE.md`](doc/DEVELOPER_GUIDE.md) | 代码风格、添加系统/组件流程、调试技巧 |
| [`doc/architecture.md`](doc/architecture.md) | 完整模块架构、接口说明、数据流 |
| [`doc/TROUBLESHOOTING.md`](doc/TROUBLESHOOTING.md) | 常见问题排查 |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 项目级架构总览与统计 |
| [`ROADMAP.md`](ROADMAP.md) | 里程碑与迭代计划 |
| [`CHANGELOG.md`](CHANGELOG.md) | 版本更新日志 |

---

## 📜 许可证

本项目采用 MIT 许可证。

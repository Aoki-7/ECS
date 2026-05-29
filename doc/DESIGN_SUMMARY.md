# Emitter 设计总结报告

> **Emitter 风格**：简洁、结构化、聚焦核心

---

## 🎯 核心理念

**底层连续，离散为视图**

- **物理世界观**：世界底层只有连续物理量的自然演化
- **离散真相**：所有离散状态（晴/雨/季节/事件）只是物理量的实时视图
- **示例**：`rainfall = 5.2mm/h`（连续量）而非 `status = "rainy"`（离散枚举）

**持续演化**：没有硬编码状态机，所有状态变化都由物理量演化驱动

---

## 🏗️ ECS 架构

```
┌─────────────────── World ────────────────────┐
│  ┌─────────── Entity ────────────┘
│  │  ┌─────────── Component ─────┐
│  │  │ (纯数据存储，dataclass)    │
│  │  └───────────────────────────┘
│  └───────────────────────────────────────────┘
│           ↓ 双向索引
│  ┌─────────────────── System ────────────────┐
│  │   (纯逻辑处理，update 函数)                │
│  └───────────────────────────────────────────┘
└───────────────────────────────────────────────┘
```

### 核心组件

| 类型 | 职责 | 示例 |
|------|------|------|
| **Component** | 纯数据存储 | `@dataclass class HealthComponent` |
| **System** | 纯逻辑处理 | `def update(self, world, dt)` |
| **Entity** | 数据与逻辑绑定 | `id + generation(防悬挂)` |
| **World** | 双向索引中心 | `get_components()` |

---

## 🌱 植物生态系统 — 连续演化的生命

**生命周期流水线**：
```
GDD累积 → 阶段推进 → 光合产出 → 形态生长 → 成熟繁殖 → 衰老凋亡
                 ↑                            ↓
            环境反馈（光/温/水）           子代遗传+变异
```

### 四层生物模型

| 层 | 说明 | 实现 |
|-----|------|------|
| **基因型** | 16 维基因向量（光合/温度/水分/代谢/形态/繁殖） | `GenomeComponent.genes[]` |
| **表现型** | 株高、茎粗、冠幅 | `MorphologyComponent` |
| **生命周期** | SEED→SPROUT→VEGETATIVE→MATURE→SENESCENCE→DEAD | `LifeCycleComponent` |
| **环境响应** | 光合速率 = f(光照, 温度, 水分) | `GrowthSystem` |

### 遗传与变异

```
亲本 16 维基因 → genome.copy() → 子代 16 维基因
                                      ↓
                          每个基因以 mutation_rate 概率变异
                                      ↓
                           gene.strength = original × random(0.8, 1.2)
```

### 9 种物种预设

| 预设 | 策略 | 适生环境 |
|------|------|----------|
| basic | 均衡 | 一般陆地 |
| fast | 快生早熟高产 | 扰动环境 |
| tree | 高大多寿晚熟 | 稳定森林 |
| cold_resistant | 耐寒 | 高寒 |
| drought_resistant | 节水 | 干旱 |
| succulent | 肉质高水效 | 沙漠 |
| aquatic | 喜水耐阴 | 水域 |
| shade_tolerant | 极耐阴 | 林下 |
| pioneer | 阳性高光效 | 裸地/灾后 |

### 动物模块

```
animal/
├── animal_factory.py   # 3 种物种预设 (basic / fast / tank)
└── __init__.py
```

通用 ECS 架构，与植物共享生物学底层组件。

---

## 🔄 环境系统

**15 子系统 DAG 管线**（每步≈1 小时）

```
外部强迫
   ↓
大气物理
   ↓
辐射传输
   ↓       ↓
异常检测 ← 地表层（同步）
   ↓
空间平滑 → 空间连续
```

### 关键子系统

| 子系统 | 职责 | 物理量（连续） |
|--------|------|----------------|
| **光照系统** | 光照传播/阴影 | `lux`, `direction`, `attenuation` |
| **气候系统** | OU 随机过程 | `atmospheric_co2`, `soil_moisture` |
| **物理天气** | 温度/湿度/风 | `temperature`, `relative_humidity` |
| **季节系统** | 天文季节 | `solar_elevation` |
| **地形系统** | 高程/坡度 | `elevation`, `surface_angle` |
| **土壤系统** | 物理演化 | `temperature`, `water_level` |

---

## 🧠 人类行为流水线

```
感知 → 情绪 → 思维 → 目标 → 意图 → 决策 → 规划 → 执行 → 反馈
```

### 紧急度权重

| 动作 | 触发条件 | 权重 |
|------|---------|------|
| **DRINK** | `thirst < 20` | 1.3 (口渴) / 1.0 |
| **EAT** | `hunger < 20` | 1.2 (饥饿) / 1.0 |
| **SLEEP** | `energy < 40` | 1.3 (疲劳) / 1.0 |
| **SOCIALIZE** | `social < 20` | 0.8 (孤独) / 1.5 |

---

## 🚀 性能优化

### 空间查询（O(log n) 而非 O(n)）

```python
# SpaceSystem 维护稀疏网格索引
entities = space_system.query_radius(x=50, y=50, r=10)
```

### 批次操作

```python
# ✅ 推荐：批量添加组件
for e_id, _ in world.get_components(SpaceComponent):
    world.add_component(e_id, MyComponent())

# ❌ 避免：逐个添加（触发多次内存分配）
```

---

## 🛠️ 开发要点

### 添加新系统（三步）

1. **创建 System 类**（继承 System 基类）
2. **注册系统**（优先级控制执行顺序）
3. **创建 Component**（如需要新数据）

### 优先级调度

```python
class MySystem(System):
    @property
    def priority(self) -> int:
        return 10  # 负值=高优先级，正值=低优先级
```

---

## 📋 常见问题

### Q1：为什么天气是连续的？

**A**：真实世界是连续的，离散状态丢失中间态信息。例如温度从 20°C→0°C，系统记录完整轨迹而非直接跳到雪天。

### Q2：事件如何触发？

**A**：统计异常检测（滑动窗口=720 样本≈30 天），无硬编码事件类型。

### Q3：植物生命周期如何推进？

**A**：通过有效积温(GDD)累积驱动，温度高则生长快，低温则停滞。年龄作为兜底机制保证极端条件下也能推进。

### Q4：遗传变异如何工作？

**A**：子代深度复制亲本 16 维基因数组，每个基因以 `mutation_rate` 概率变异 ±20%，多代积累产生群体多样性。

---

## 📄 文档索引

| 文档 | 链接 |
|------|------|
| [README.md](README.md) | 项目概览 |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | 开发指南 |
| [DESIGN_PATTERNS.md](DESIGN_PATTERNS.md) | 设计模式 |
| [PROJECT_PRINCIPLES.md](PROJECT_PRINCIPLES.md) | 设计原则 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 问题排查 |
| [architecture.md](architecture.md) | 架构说明 |
| [environment_improvement_report.md](environment/environment_improvement_report.md) | 环境改进 |

---

**创建时间**: 2026-05-28  
**维护者**: ECS Core Team  
**版本**: v2.2

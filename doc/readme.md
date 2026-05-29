# ECS 世界模拟系统

> **底层连续物理量驱动世界演化** —— 一个基于 ECS（Entity-Component-System）架构的多层级世界模拟引擎。

---

## 🎯 核心理念

**"连续物理量 + 实时视图"**

- 底层只有连续物理量的自然演化（温度、光照、降水、能量）
- 所有离散状态（晴/雨/季节/事件）都是物理量的实时视图
- 物理驱动而非硬编码状态机驱动

```
太阳位置 → 大气顶辐射 → 连续天气物理量 → 地表光照 → 环境同步
                                              ↓
                                      生物光合 → 能量分配 → 形态生长
                                              ↓
                                      生命周期 → 繁殖/衰老/死亡
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 无第三方依赖（纯标准库）

### 运行基础模拟

```bash
python main.py
```

输出示例：
```
[Run] 模拟: 300 步 × 1.0h
  Step    0/300 | 实体:120 人口:10 食物:80 水源:80   0.0步/s
  Step   50/300 | 实体:142 人口:10 食物:65 水源:78  45.2步/s
...
[Done] 实体:156 人口:12 食物:72 水源:81 文明:tribal  52步/s
```

### 运行全面模拟

```bash
python full_simulation.py
```

全面模拟在基础版之上增加了：
- 完整环境管线（天气、季节、气候、大气、光照）
- 资源腐败与再生（食物腐败、木材腐朽、石头风化、金属氧化）
- 植物生命周期与繁殖
- 人类文明演进

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
│  │   (纯逻辑处理，update(world, dt))          │ │
│  └───────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

| 类型 | 职责 | 示例 |
|------|------|------|
| **Entity** | 标识符 + 代际（防悬挂） | `id=42, generation=3` |
| **Component** | 纯数据存储 | `@dataclass class EnergyComponent` |
| **System** | 纯逻辑处理 | `def update(self, world, dt)` |
| **World** | 双向索引中心 | `get_components(A, B)` 联合查询 |

### 模块分层

```
core/           # ECS 引擎核心（Entity, Component, System, World）
space/          # 空间系统（坐标、空间索引、范围查询）
time_module/    # 时间系统（年/日/时推进）
environment/    # 环境系统（15 子系统 DAG 管线：光照→天气→季节→土壤）
biology/        # 生物系统（基因、表型、生长、生命周期、免疫、营养、竞争）
plant/          # 植物工厂（9 种物种预设 + 生命周期模板）
animal/         # 动物工厂（3 种物种预设）
human/          # 人类系统（生理、认知、社交、行为、文明）
resource/       # 资源系统（食物、水、木材、石头、金属）
rules/          # 规则系统（资源转换、腐败、技能提升）
civilization/   # 文明系统（科技树、建筑、贸易）
```

---

## 🌱 生物学系统详解

### 12 步执行管线

```
1. GeneExpressionSystem    # 基因型 → 表型（16维基因表达）
2. CompetitionSystem       # 生态竞争（光照遮阴 + 水分竞争）
3. GrowthSystem            # 光合作用 + 呼吸 + 能量分配
4. MorphologySystem        # 生长池 → 形态更新（高度/叶片/茎粗）
5. NutrientSystem          # N/P/K 吸收与消耗（环境联动）
6. LifeCycleSystem         # 积温累积 + 阶段推进
7. SenescenceSystem        # 衰老退化（黄化、光合衰减）
8. DamageRepairSystem      # 损伤修复（能量消耗）
9. MutationSystem          # 持续环境诱变
10. ReproductionSystem     # 成熟期繁殖（遗传 + 变异 + 散布）
11. ImmuneSystem           # 感染传播与免疫反应
12. DeathSystem            # 死亡判定（最后执行，移除实体）
```

### 四层生物模型

| 层 | 说明 | 组件 |
|-----|------|------|
| **基因型** | 16 维基因向量（光合/温度/水分/代谢/形态/繁殖） | `GenomeComponent` |
| **表型** | 基因表达后的动态性状集合 | `PhenotypeComponent` |
| **表现型** | 株高、茎粗、冠幅、叶片数 | `MorphologyComponent` |
| **生命周期** | SEED → SPROUT → VEGETATIVE → MATURE → SENESCENCE → DEAD | `LifeCycleComponent` |

### 植物物种预设（9 种）

| 预设 | 策略 | 特征 |
|------|------|------|
| `basic` | 均衡型 | 一般陆地适生 |
| `fast` | 速生杂草 | 高光合、短寿命、高繁殖 |
| `tree` | 乔木 | 高大多寿、低繁殖、强遮阴 |
| `cold_resistant` | 耐寒型 | 低温适生、高耐寒系数 |
| `drought_resistant` | 耐旱型 | 深根系、高水分利用效率 |
| `shade_tolerant` | 耐阴型 | 低光高效光合、大叶片 |
| `aquatic` | 水生型 | 水域适生、漂浮叶片 |
| `succulent` | 多肉型 | 极端耐旱、茎干储水 |
| `vine` | 藤本型 | 攀援生长、高叶面积比 |

---

## 🧬 人类系统管线

```
感知(Preception) → 情绪(Emotion) → 思维(Thought) → 目标(Goal)
       ↓
意图(Intent) → 决策(Decision) → 规划(Planning) → 动作调度(Action)
       ↓
搜索/移动/采集/进食/饮水/睡眠/社交 → 部落(Tribe) → 文明(Civilization)
```

---

## 📂 目录结构

```
ECS/
├── core/                       # ECS 核心引擎
│   ├── entity.py               # 实体（id + generation）
│   ├── component.py            # 组件基类
│   ├── system.py               # 系统基类（priority 排序）
│   ├── world.py                # 世界（双向索引中心）
│   └── ...
│
├── biology/                    # 生物模拟层
│   ├── components/             # 生物组件
│   │   ├── genome_component.py
│   │   ├── phenotype_component.py
│   │   ├── energy_component.py
│   │   ├── morphology_component.py
│   │   ├── life_cycle_component.py
│   │   ├── immune_component.py       # 免疫状态
│   │   ├── damage_component.py       # 损伤伤口
│   │   ├── nutrient_component.py     # N/P/K 营养
│   │   └── competition_component.py  # 生态竞争
│   ├── systems/                # 生物系统
│   │   ├── gene_expression_system.py
│   │   ├── growth_system.py
│   │   ├── morphology_system.py
│   │   ├── life_cycle_system.py
│   │   ├── senescence_system.py
│   │   ├── mutation_system.py
│   │   ├── reproduction_system.py
│   │   ├── immune_system.py          # 感染传播 + 免疫反应
│   │   ├── damage_repair_system.py   # 损伤修复
│   │   ├── nutrient_system.py        # 营养代谢
│   │   └── competition_system.py     # 生态竞争
│   ├── genetics/               # 遗传机制
│   │   └── gene.py             # 基因原子（表达/突变/复制）
│   └── traits/                 # 性状
│       └── trait.py            # 数值性状（约束/来源标记）
│
├── plant/                      # 植物层
│   ├── presets.py              # 物种基因预设 + 生命周期预设
│   └── plant_factory.py        # 植物工厂（单创/批量/繁殖）
│
├── animal/                     # 动物层
│   ├── presets.py              # 物种基因预设
│   └── animal_factory.py       # 动物工厂
│
├── human/                      # 人类层（生理/认知/社交/行为）
├── environment/                # 环境层（天气/季节/土壤/光照）
├── space/                      # 空间层（坐标/索引）
├── time_module/                # 时间层
├── resource/                   # 资源层（食物/水/木材/石头/金属）
├── rules/                      # 规则层
├── civilization/               # 文明层
├── equipment/                  # 装备层
├── identity/                   # 身份层
├── physiology/                 # 生理层
├── garbage/                    # 垃圾层
│
├── main.py                     # 基础模拟入口
├── full_simulation.py          # 全面模拟入口
│
├── README.md                   # 本文件
├── PROJECT_PRINCIPLES.md       # 项目设计原则
├── DESIGN_PATTERNS.md          # 设计模式文档
├── DESIGN_SUMMARY.md           # 设计总结报告
├── DEVELOPER_GUIDE.md          # 开发者指南
└── architecture.md             # 项目架构文档
```

---

## 🛠️ 扩展开发

### 添加新组件

```python
# my_module/components/my_component.py
from dataclasses import dataclass
from core.component import Component

@dataclass
class MyComponent(Component):
    value: float = 0.0
```

### 添加新系统

```python
# my_module/systems/my_system.py
from core.system import System
from core.world import World

class MySystem(System):
    def update(self, world: World, dt: float = 1.0):
        for entity, (comp_a, comp_b) in world.get_components(
            ComponentA, ComponentB
        ):
            # 业务逻辑
            pass
```

### 注册到主循环

```python
# main.py
from my_module.systems.my_system import MySystem

self.biology_systems.append(MySystem())
```

详细开发规范请参阅 [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md)。

---

## 📖 相关文档

| 文档 | 内容 |
|------|------|
| [`PROJECT_PRINCIPLES.md`](PROJECT_PRINCIPLES.md) | 设计理念、ECS 架构选择、技术决策 |
| [`DESIGN_PATTERNS.md`](DESIGN_PATTERNS.md) | 工厂模式、观察者模式、策略模式等最佳实践 |
| [`DESIGN_SUMMARY.md`](DESIGN_SUMMARY.md) | Emitter 风格设计总结、植物生态模型 |
| [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) | 代码风格、添加系统/组件流程、调试技巧 |
| [`architecture.md`](architecture.md) | 完整模块架构、接口说明、数据流 |
| [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | 常见问题排查 |

---

## 📜 许可证

本项目采用 MIT 许可证。

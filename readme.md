# ECS 世界模拟系统

基于 **Entity-Component-System (ECS)** 架构的复杂世界模拟，实现人类-环境-文明三层交互。

> 模拟粒度：1 步 = 1 小时 | 默认 300 步 ≈ 12.5 天 | Python 3.10+

---

## 快速开始

```bash
python main.py
```

默认运行 300 步模拟，每步 1 小时，输出人口、食物、文明阶段等统计信息。

---

## 架构概览

三层模拟框架，由 **5 层 DAG 环境管线** 驱动时间演进：

```
外部强迫（太阳/季节/气候）
    → 大气物理（温度/气压/湿度/云量/降水/风速）
    → 辐射传输（TOA → 地表光照）
    → 异常检测 + 地表层（土壤/环境同步）
    → 空间平滑（扩散/平流/水流）
```

完整架构说明见 [**architecture.md**](architecture.md)。

---

## 核心特性

- **纯物理驱动天气** — 连续物理量演化，离散状态仅为实时视图
- **ECS 架构** — 数据与逻辑分离，高内聚低耦合
- **模块化管线** — 环境/人类/生物/规则/文明系统独立演进
- **天文季节** — 太阳赤纬角和日地距离实时计算，无固定季节枚举
- **统计异常检测** — 滑动窗口识别物理偏离，无预定义事件类型

---

## 模块导航

| 模块 | 关键入口 | 说明 |
|------|---------|------|
| **核心层** | [`core/`](core/) | Entity、Component、System、World 基类 |
| **环境系统** | [`environment/config/environment_builder.py`](environment/config/environment_builder.py) | 15 系统管线组装 |
| | [`environment/physics_weather/systems/physical_weather_system.py`](environment/physics_weather/systems/physical_weather_system.py) | 核心天气物理演化 |
| | [`environment/season/season_state.py`](environment/season/season_state.py) | 天文季节计算 |
| | [`environment/climate/climate_system.py`](environment/climate/climate_system.py) | OU 随机过程气候 |
| | [`environment/physics_weather/systems/weather_event_system.py`](environment/physics_weather/systems/weather_event_system.py) | 统计异常检测 |
| **人类系统** | [`human/human_factory.py`](human/human_factory.py) | 人类实体创建 |
| | [`human/systems/physiological/physiology_needs_system.py`](human/systems/physiological/physiology_needs_system.py) | 生理需求更新 |
| | [`human/systems/core/intent_system.py`](human/systems/core/intent_system.py) | 意图决策 |
| **空间系统** | [`space/space_system.py`](space/space_system.py) | 空间索引与范围查询 |
| **时间系统** | [`time_module/time_system.py`](time_module/time_system.py) | 时间推进 |
| **规则系统** | [`rules/transformation_system.py`](rules/transformation_system.py) | 条件变换（如食物腐败） |
| **主入口** | [`main.py`](main.py) | 模拟循环与系统初始化 |

---

## 扩展开发

添加新系统只需三步：

1. 创建系统类继承 [`System`](core/system.py)，实现 `update(world, delta_hours)`
2. 在 [`environment/config/environment_builder.py`](environment/config/environment_builder.py) 或 [`main.py`](main.py) 中注册
3. 如需新组件，继承 [`Component`](core/component.py) 并在 `build()` 中添加到 `world_entity`

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [**architecture.md**](architecture.md) | 完整架构说明、执行流水线、组件依赖图、数据流、当前状态 |
| [**environment/environment_improvement_report.md**](environment/environment_improvement_report.md) | 环境模块改进报告（21 项问题及修复状态） |
| [**memory/2026-05-17.md**](memory/2026-05-17.md) | 开发历史记录 |

---

## 技术栈

- **Python 3.10+** — 现代类型提示与 dataclass
- **ECS 模式** — Entity + Component（纯数据）+ System（纯逻辑）
- **单向 DAG 管线** — 环境子系统按 5 层拓扑顺序执行

## 许可证

MIT

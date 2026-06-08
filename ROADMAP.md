# ECS 世界模拟系统 — 迭代路线图

> 当前版本: v2.1
> 最后更新: 2026-06-08

---

## 已完成的里程碑

### ✅ v1.0 核心框架（2026-05）
- [x] ECS 核心（Entity/Component/System/World）
- [x] 空间系统（SpaceComponent/SpaceSystem）
- [x] 时间系统（昼夜/季节）
- [x] 环境系统（天气/物理）

### ✅ v1.5 生物模块（2026-05）
- [x] 生命周期系统（出生/成长/死亡）
- [x] 能量系统
- [x] 疾病系统
- [x] 基础动物行为（捕食/觅食/繁殖）

### ✅ v2.0 Animal 重构 + 记忆层（2026-06-08）
- [x] Animal 模块全面重构（7→27 文件，3→10 系统）
- [x] 统一记忆层 Phase 1-4 完成
  - [x] Phase 1: 核心骨架（16 核心类）
  - [x] Phase 2: ECS 集成（World 钩子 + Perception/Social 系统）
  - [x] Phase 3: 高级特性（认知框架 + 扭曲引擎 + 传话游戏）
  - [x] Phase 4: 持久化（存档/读档 + 性能基准）
- [x] 207 个测试全部通过

---

## 当前迭代（v2.2 目标）

### 🔨 Human 模块记忆层集成

**目标**: 将人类感知和社交系统对接统一记忆层

**任务清单**:
- [ ] 分析 `human/` 模块现有感知系统
- [ ] 在 `human/systems/` 中添加记忆层记录点
- [ ] 人类社交系统支持叙述传播
- [ ] 人类特有的认知框架（文化/语言影响）
- [ ] 添加 10+ 集成测试

**预期产出**:
- `human/systems/human_perception_system.py` 增强
- `human/systems/human_social_system.py` 增强
- `memory_layer/cognitive_framework.py` 人类框架扩展

---

### 🔨 Plant 模块重构

**目标**: 类似 Animal 的全面重构

**任务清单**:
- [ ] 分析现有 `plant/` 模块
- [ ] 设计 PlantComponent 扩展（光/水/土壤需求）
- [ ] 新增 PlantPerceptionSystem（光感知/水分感知）
- [ ] 新增 PlantGrowthSystem（生长决策）
- [ ] 新增 PlantMemorySystem（向光性/水分记忆）
- [ ] 对接统一记忆层
- [ ] 添加 15+ 测试

**预期产出**:
- `plant/components/` 扩展
- `plant/systems/` 新增 3-5 个系统
- `plant/tests/` 新增测试

---

### 🔨 存档系统统一

**目标**: 整合分散的存档逻辑

**任务清单**:
- [ ] 分析 `save_load/` 现有实现
- [ ] 设计统一存档格式（JSON Schema）
- [ ] 整合 `MemoryPersistence` 到全局存档流程
- [ ] 版本兼容性处理（存档升级机制）
- [ ] 添加 5+ 测试

**预期产出**:
- `save_load/unified_save_system.py`
- 存档格式文档

---

## 未来迭代（v3.0 目标）

### 🌟 事件总线系统

**目标**: 统一各模块的事件处理

**设计**:
```python
class EventBus:
    def subscribe(self, event_type, handler)
    def publish(self, event_type, payload)
    def unsubscribe(self, event_type, handler)
```

**应用场景**:
- 实体创建/销毁事件
- 天气变化事件
- 战斗/死亡事件
- 记忆形成事件

---

### 🌟 可视化工具

**目标**: 实时监控和调试工具

**功能**:
- 记忆网络图（Graphviz/D3.js）
- 实体分布热力图
- 系统性能监控面板
- 时间轴回放

---

### 🌟 大规模性能优化

**目标**: 支持 10,000+ 实体实时模拟

**优化方向**:
- 空间查询优化（四叉树/网格）
- 组件存储优化（SOA 布局）
- 系统并行化（多线程更新）
- 内存池管理

---

## 技术债务追踪

| 债务 | 优先级 | 状态 | 计划解决版本 |
|------|--------|------|-------------|
| `memory/` 旧系统 | 中 | ✅ 已清理 | v2.3 |
| 各模块 README 缺失 | 低 | ⚠️ 待补充 | v3.0 |
| API 文档自动生成 | 低 | ⚠️ 待实现 | v3.0 |
| 类型注解覆盖率 | 中 | ⚠️ 待提升 | v2.2 |

---

## 版本发布计划

| 版本 | 目标日期 | 主要特性 |
|------|----------|----------|
| v2.1 | 2026-06-08 | 架构文档 + 清理 ✅ |
| v2.2 | 2026-06-08 | Human 集成 + Plant 重构 ✅ |
| v2.3 | 2026-06-08 | 存档统一 + 旧系统迁移 ✅ |
| v3.0 | 2026-07-01 | 事件总线 + 可视化 + 性能优化 |

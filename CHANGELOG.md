# 更新日志

## v2.3 (2026-06-08)

### 存档系统统一
- 新增 `save_load/unified_save_system.py`
  - 整合 World 序列化 + MemoryLayer 持久化
  - 统一存档格式：`{version, world, memory_layer, meta}`
  - 支持版本检查、自动存档、存档列表/删除
- 修复 `WorldSerializer.deserialize()` 兼容旧 World 对象
- 新增 `save_load/tests/test_unified_save.py`
  - 8 个测试覆盖保存/加载/列表/删除/版本检查

### 旧系统迁移
- `memory/` 目录确认为笔记存档（非活跃代码）
- 新增 `memory/README.md` 说明迁移状态
- `memory_layer/` 为唯一活跃记忆系统

### 测试
- 总测试数: 226 个（全部通过）
  - save_load: 8 个（新增）

---

## v2.2 (2026-06-08)

### Human 模块记忆层集成
- `human/systems/cognitive/perception_system.py` 增强
  - 感知时自动记录 `ContactRecord` 到统一记忆层
  - 支持人类/资源/异常实体的感知记录
- `human/systems/interaction/dialogue_system.py` 增强
  - 对话时记录社交接触
  - 支持旁观者的叙述传播（记忆重新生成）
- 新增 `human/tests/test_human_memory_integration.py`
  - 5 个测试覆盖感知、对话、认知框架、生命周期

### Plant 模块增强
- 新增 `plant/components/plant_perception_component.py`
  - 光感知、水感知、化学感知、重力感知
- 新增 `plant/systems/plant_perception_system.py`
  - 处理植物感知并记录到统一记忆层
  - 支持向光性/向水性记忆
- 新增 `plant/tests/test_plant_memory_integration.py`
  - 6 个测试覆盖感知组件、记忆集成、系统更新

### 测试
- 总测试数: 218 个（全部通过）
  - memory_layer: 53 个
  - animal: 25 个
  - human: 5 个（新增）
  - plant: 6 个（新增）
  - 其他模块: 129 个

---

## v2.1 (2026-06-08)

### 架构优化
- 新增 `ARCHITECTURE.md` — 完整架构文档
- 新增 `ROADMAP.md` — 迭代路线图
- 新增 `CHANGELOG.md` — 本文件
- 清理根目录临时文件（`weather_test.py` → `doc/examples/weather_demo.py`）
- 扫描确认无 `except:pass` 残留
- 扫描确认无 `dt` 类型注解缺失残留

### 统一记忆层（v1.3.0）
- **Phase 4 完成**: 持久化 + 性能基准测试
  - `memory_persistence.py` — 存档/读档/自动保存
  - `test_phase4.py` — 11 个测试（持久化 + 性能 + 压力）
  - 性能基准：1000 实体 注册 < 2s，10000 接触记录 < 2s
- 更新 `__init__.py` 导出列表
- 更新 `README.md` 版本历史

### 测试
- 207 个测试全部通过

---

## v2.0 (2026-06-08)

### Animal 模块全面重构
- 文件从 7 → 27 个
- 系统从 3 → 10 个
- 新增组件：AnimalNeeds, AnimalSocial, AnimalMemory, AnimalTerritory, AnimalMigration, AnimalReproduction
- 新增系统：AnimalNeedsSystem, AnimalSocialSystem, AnimalMemorySystem, AnimalTerritorySystem, AnimalMigrationSystem, AnimalPerceptionSystem, AnimalLearningSystem
- 25/25 测试通过

### 统一记忆层（v1.0-1.2）
- **Phase 1**: 核心骨架（16 核心类，23 个测试）
- **Phase 2**: ECS 集成（World 钩子 + Perception/Social 系统，6 个集成测试）
- **Phase 3**: 高级特性（认知框架 + 扭曲引擎 + 传话游戏，13 个测试）

---

## v1.5 (2026-05)

### 生物模块
- 生命周期系统（出生/成长/死亡）
- 能量系统
- 疾病传播系统

---

## v1.0 (2026-05)

### 核心框架
- ECS 核心（Entity/Component/System/World）
- 空间系统
- 时间系统
- 环境系统

# 统一记忆层（Memory Layer）

独立于 ECS 的元层服务，管理客观记忆（Concept）和主观记忆（MemoryInstance）。

## 核心设计

### 三层模型

```
物理层（Entity） → 客观记忆（Concept） → 主观记忆（MemoryInstance）
     石头E42    →   "石头E42"概念    →   生物A的记忆 / 生物B的记忆
   （可消亡）      （实体消亡后仍存在）      （个性化、可能扭曲）
```

### 关键特性

1. **独立于实体存在**：石头被破坏了，"石头的概念"仍然存在
2. **主客观分离**：Concept（客观事实） vs MemoryInstance（主观观点）
3. **记忆传播 = 重新生成**：不是复制，而是基于描述 + 接收者认知重新生成
4. **结构化感官描述**：形状/颜色/质地/大小/气味/声音/温度

## 快速开始

```python
from memory_layer import MemoryLayer, SensoryDescription, SubjectType

# 获取单例
ml = MemoryLayer.get_instance()

# 注册实体（自动创建客观概念）
desc = SensoryDescription(shape="圆形", color="灰色", texture="光滑")
concept = ml.register_entity(
    entity_id=42,
    entity_type="stone",
    description=desc,
)

# 记录接触（自动形成主观记忆）
ml.record_contact(
    subject_id=1,
    subject_type=SubjectType.ANIMAL,
    entity_id=42,
    contact_type="visual",
    intensity=0.8,
)

# 回忆记忆
memory = ml.recall_memory(subject_id=1, concept_id="entity_42_stone")
print(memory.sensory_impression.to_text())  # "圆形灰色的光滑"

# 叙述传播（重新生成，非复制）
new_memory = ml.narrate_memory(
    from_subject=1,
    to_subject=2,
    to_subject_type=SubjectType.ANIMAL,
    concept_id="entity_42_stone",
)
```

## ECS 集成

### World 集成

```python
# World 已添加 get_memory_layer() 方法
world = World()
ml = world.get_memory_layer()  # 获取记忆层单例

# 实体销毁时自动通知记忆层
world.remove_entity(entity)  # → 自动调用 ml.entity_destroyed()
```

### PerceptionSystem 集成

```python
# AnimalPerceptionSystem 感知时自动记录 Contact
# 同时更新传统 AnimalMemoryComponent 和统一记忆层
```

### SocialSystem 集成

```python
# AnimalSocialSystem 社交时支持叙述传播
# 通过 _share_memory() 方法实现记忆重新生成
```

## 核心类

| 类 | 职责 |
|----|------|
| `MemoryLayer` | 全局单例管理器 |
| `Concept` | 客观记忆（被记忆的对象） |
| `MemoryInstance` | 主观记忆（某主体对概念的记忆） |
| `SensoryDescription` | 结构化感官描述（7字段） |
| `EmotionalTag` | 情感标签 |
| `ContactRecord` | 接触记录 |
| `AssociationLink` | 联想链接 |
| `MemoryRegistrationSystem` | 自动注册实体到记忆层 |

## 测试

```bash
cd D:\个人助手\workspace\ECS
python -m pytest memory_layer/tests/ -v
```

**状态**: 29/29 通过（含 6 个 ECS 集成测试）

## 版本历史

- v1.0 (2026-06-08): Phase 1 核心骨架完成（23 个测试）
- v1.1 (2026-06-08): Phase 2 ECS 集成完成（+6 个集成测试）
  - World 实体生命周期钩子
  - AnimalPerceptionSystem 记录 Contact
  - AnimalSocialSystem 叙述传播
  - MemoryRegistrationSystem 自动注册
- v1.2 (2026-06-08): Phase 3 高级特性完成（+13 个测试）
  - 认知框架（CognitiveFramework）
  - 记忆扭曲引擎（MemoryDistortionEngine）
  - 传话游戏效应（simulate_telephone_game）
  - 注意力滤镜 / 解释偏差 / 威胁滤镜 / 记忆重构
- v1.3 (2026-06-08): Phase 4 性能优化与持久化完成（+11 个测试）
  - 存档/读档（MemoryPersistence）
  - 自动保存（按 tick 间隔）
  - 性能基准测试（1000 实体 < 2s，10000 接触 < 2s）
  - 压力测试（5000 实体，10000 接触）

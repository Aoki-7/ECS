# 统一记忆层概念设计文档

## 一、需求理解

### 核心洞察
您提出的不是传统 ECS 中的"Component 存储数据"，而是一种**元层（Meta-Layer）**：

```
物理层（Physical Layer）          元层（Meta Layer）
┌─────────────────┐              ┌─────────────────┐
│ 石头实体 E42    │ ──破坏──→    │ 石头概念 C42    │
│ - 位置 (10,20)  │   消失       │ - 抽象定义      │
│ - 硬度 50       │              │ - 多主体记忆    │
│ - 质量 100kg    │              │ - 情感关联      │
└─────────────────┘              └─────────────────┘
         ↑                              ↑
    生物 A 接触                    生物 A 的记忆
    生物 B 接触                    生物 B 的记忆
                                   （不完全相同）
```

### 关键特性

1. **独立于实体存在**：石头被破坏了，"石头的概念"仍然存在
2. **多主体共享**：不同生物对同一概念有不同记忆
3. **不可量化**：不是数值，是模糊的、带情感的、个性化的
4. **跨生死**：死者留下的记忆可以被生者继承
5. **虚构性**：可以是完全虚构的（神话生物、传说）

---

## 二、需求规范化

### 2.1 核心概念定义

| 术语 | 定义 | 示例 |
|------|------|------|
| **概念（Concept）** | 独立于实体的抽象存在 | "石头"这个概念 |
| **记忆实例（MemoryInstance）** | 某主体对某概念的具体记忆 | 生物A记忆中的"那块圆石头" |
| **主体（Subject）** | 拥有记忆能力的存在 | 生物、AI、甚至文明 |
| **记忆层（MemoryLayer）** | 管理所有概念和记忆实例的系统 | 全局单例 |
| **接触记录（Contact）** | 主体与实体的交互历史 | "2026-06-08 生物A踢了石头" |

### 2.2 记忆的非量化特性

```python
# 传统 ECS 组件（量化）
@dataclass
class MemoryComponent:
    food_location: tuple  # (10, 20)
    threat_level: float   # 0.8

# 统一记忆层（非量化）
class ConceptMemory:
    """
    生物A对"石头E42"的记忆：
    - 形象："圆圆的，有点滑，灰色的"
    - 情感："讨厌，因为曾经绊倒过我"
    - 关联："和那条河边的石头很像"
    - 模糊度：高（可能记错了大小）
    """
    pass
```

### 2.3 用例场景

**场景1：实体消亡，记忆留存**
```
时间线：
T0: 石头E42 存在，生物A接触过
T1: 石头E42 被破坏（实体删除）
T2: 生物A仍然记得"那块石头"
T3: 生物A向生物B描述"那块石头"
T4: 生物B形成对"石头E42"的间接记忆
```

**场景2：同一概念，不同记忆**
```
概念："石头E42"
├── 生物A的记忆："圆圆的，讨厌"
├── 生物B的记忆："灰色的，可以用来磨刀"
└── 生物C（从未见过）：从A/B处听说的"一块石头"
```

**场景3：虚构概念**
```
概念："龙"
├── 实体层：不存在
├── 记忆层：
│   ├── 生物A："巨大的，喷火，可怕"
│   ├── 生物B："神圣的，守护者"
│   └── 文明传说："古代英雄屠龙的故事"
```

---

## 三、架构设计草案

### 3.1 层级关系

```
┌─────────────────────────────────────────┐
│           统一记忆层 (MemoryLayer)         │
│  ┌─────────────┐    ┌─────────────┐    │
│  │  概念注册表  │    │  记忆图谱    │    │
│  │  Concept    │◄──►│  Memory     │    │
│  │  Registry   │    │  Graph      │    │
│  └─────────────┘    └─────────────┘    │
│         ▲                    ▲          │
│         │                    │          │
│    实体消亡时            主体访问时      │
│    自动转换              激活记忆       │
└─────────────────────────────────────────┘
              ▲
    ┌─────────┴─────────┐
    │     主体层         │
    │  ┌─────┐ ┌─────┐ │
    │  │生物A│ │生物B│ │
    │  └──┬──┘ └──┬──┘ │
    │     │       │     │
    │  ┌──┴──┐ ┌──┴──┐ │
    │  │记忆A│ │记忆B│ │
    │  └──┬──┘ └──┬──┘ │
    │     └───────┘     │
    │       共享概念      │
    └───────────────────┘
```

### 3.2 核心类设计

```python
# ========== 概念（独立于实体）==========
class Concept:
    """
    抽象概念，独立于物理实体存在
    """
    concept_id: str           # 唯一标识
    name: str                 # 名称
    concept_type: str         # "entity", "abstract", "myth"
    source_entity_id: int | None  # 来源实体（可能已消亡）
    canonical_description: str    # 客观描述（如果有）
    created_at: float         # 概念形成时间
    is_active: bool           # 是否还有实体对应

# ========== 记忆实例（主体对概念的记忆）==========
class MemoryInstance:
    """
    某主体对某概念的具体记忆
    非量化、个性化、可能扭曲
    """
    memory_id: str
    concept_id: str           # 关联的概念
    subject_id: int           # 记忆主体（实体ID）
    
    # === 非量化属性 ===
    sensory_impression: str   # 感官印象："圆圆的，滑滑的"
    emotional_tag: str        # 情感标签："讨厌"/"喜欢"/"恐惧"
    confidence: float         # 确信度 0.0~1.0（"我好像记得..."）
    distortion_level: float   # 扭曲度 0.0~1.0（记忆偏差）
    
    # === 关系属性 ===
    associations: List[str]   # 联想：["河边的石头", "小时候"]
    narrative: str            # 叙事："那天我踢了它，摔倒了"
    
    # === 时间属性 ===
    first_contact: float      # 首次接触时间
    last_recall: float        # 上次回忆时间
    recall_count: int         # 回忆次数（影响清晰度）

# ========== 接触记录（主体与实体的交互）==========
class ContactRecord:
    """
    主体与实体的客观交互记录
    作为记忆形成的基础
    """
    contact_id: str
    subject_id: int
    entity_id: int
    contact_type: str         # "visual", "physical", "auditory", "narrative"
    timestamp: float
    context: str              # 上下文描述
    intensity: float          # 强度 0.0~1.0

# ========== 统一记忆层管理器 ==========
class MemoryLayer:
    """
    全局单例，管理所有概念和记忆
    """
    _concepts: Dict[str, Concept]
    _memories: Dict[str, MemoryInstance]  # key: "subject_id:concept_id"
    _contacts: List[ContactRecord]
    
    # === 核心操作 ===
    def register_entity(self, entity: Entity) -> Concept: ...
    def entity_destroyed(self, entity_id: int) -> None: ...
    def record_contact(self, subject_id: int, entity_id: int, ...) -> None: ...
    def form_memory(self, subject_id: int, concept_id: str) -> MemoryInstance: ...
    def recall_memory(self, subject_id: int, concept_id: str) -> MemoryInstance | None: ...
    def narrate_memory(self, from_subject: int, to_subject: int, concept_id: str) -> None: ...
```

---

## 四、可行性评估

### 4.1 技术可行性：✅ 可行

| 方面 | 评估 | 说明 |
|------|------|------|
| **存储** | ✅ | 概念和记忆实例可以用 Python 对象存储，不依赖 ECS 组件系统 |
| **查询** | ✅ | 按 subject_id + concept_id 索引，O(1) 查询 |
| **序列化** | ✅ | 可以保存到 JSON/数据库，支持存档读档 |
| **性能** | ⚠️ | 记忆数量可能爆炸（N个主体 × M个概念），需要裁剪机制 |

### 4.2 架构可行性：✅ 可行

| 方面 | 评估 | 说明 |
|------|------|------|
| **与 ECS 集成** | ✅ | MemoryLayer 作为全局服务，System 通过 API 访问 |
| **与现有系统兼容** | ✅ | AnimalMemoryComponent 可以引用 MemoryLayer 中的概念 |
| **扩展性** | ✅ | 新实体类型自动注册概念，无需修改记忆层 |

### 4.3 设计挑战：⚠️ 需要权衡

| 挑战 | 严重程度 | 解决方案 |
|------|----------|----------|
| **记忆爆炸** | 🔴 高 | 限制每个主体的记忆数量，遗忘机制 |
| **非量化如何驱动行为** | 🟡 中 | 需要 NLP/语义解析将描述转为行为权重 |
| **多主体记忆同步** | 🟡 中 | 叙述传播时添加扭曲（传话游戏效应） |
| **虚构概念管理** | 🟢 低 | 允许 concept.source_entity_id = None |

### 4.4 实现复杂度：🟡 中等偏高

```
预估工作量：
├── 核心类实现（Concept, MemoryInstance, ContactRecord）    ~2天
├── MemoryLayer 管理器（CRUD + 查询 + 索引）               ~3天
├── 与 ECS 集成（实体生命周期钩子 + System 访问）           ~2天
├── 遗忘与裁剪机制                                        ~2天
├── 叙述传播系统（主体间记忆传递）                         ~3天
├── 存档/读档支持                                         ~1天
└── 测试覆盖                                              ~2天
总计：约 15 个工作日
```

---

## 五、与现有 Animal 模块的关系

### 5.1 当前 AnimalMemoryComponent 的局限

```python
# 当前：量化、物理、短期
@dataclass
class AnimalMemoryComponent:
    memories: List[MemoryEntry]  # x, y, type, value
    # 问题：
    # 1. 只有位置坐标，没有"概念"
    # 2. 实体删除后记忆失效（entity_id 指向不存在实体）
    # 3. 无法表达"那块讨厌的石头"
```

### 5.2 统一记忆层增强

```python
# 增强后：AnimalMemoryComponent 引用统一记忆层
@dataclass
class AnimalMemoryComponent:
    memory_layer_refs: List[str]  # 引用的概念ID列表
    
    def recall(self, memory_layer: MemoryLayer, concept_id: str):
        memory = memory_layer.recall_memory(self._entity_id, concept_id)
        if memory:
            return memory.sensory_impression, memory.emotional_tag
        return None, None
```

---

## 六、推荐实现路径

### Phase 1: 核心骨架（1 周）
- [ ] 实现 Concept + MemoryInstance + ContactRecord
- [ ] 实现 MemoryLayer 基础 CRUD
- [ ] 实体生命周期钩子（创建/销毁时自动注册概念）

### Phase 2: 与 ECS 集成（1 周）
- [ ] 修改 AnimalMemoryComponent 引用记忆层
- [ ] 新增 MemorySystem（管理记忆形成/遗忘/传播）
- [ ] 修改 AnimalPerceptionSystem 记录 ContactRecord

### Phase 3: 高级特性（1 周）
- [ ] 叙述传播（主体间记忆传递）
- [ ] 记忆扭曲（多次传递后失真）
- [ ] 虚构概念创建（神话、传说）

### Phase 4: 优化（1 周）
- [ ] 遗忘机制（基于时间/重要性）
- [ ] 性能优化（索引、缓存）
- [ ] 存档读档

---

## 七、结论

| 维度 | 评估 |
|------|------|
| **技术可行性** | ✅ 可行，无技术障碍 |
| **架构兼容性** | ✅ 与现有 ECS 兼容，作为元层服务 |
| **实现复杂度** | 🟡 中等偏高，约 15 工作日 |
| **价值** | 🔴 极高，为世界模拟增加深度和叙事能力 |
| **推荐** | ✅ **建议实现** |

这个设计将 ECS 世界从"物理模拟"提升到"认知模拟"层面，使实体不再只是物理对象，而是拥有主观世界、可以传承记忆、创造文化的存在。

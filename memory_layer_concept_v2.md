# 统一记忆层概念设计文档 V2

**状态**: 设计冻结，等待开发确认  
**更新日期**: 2026-06-08  
**变更**: 基于主人5点反馈全面重构

---

## 一、主人需求确认（5点）

| # | 需求 | 设计响应 |
|---|------|----------|
| 1 | **结构化描述** | 感官印象拆分为形状/颜色/质地/大小/气味等字段 |
| 2 | **主体限定动物/人类** | Subject 类型枚举限制为 `ANIMAL` / `HUMAN` |
| 3 | **记忆传播 = 重新生成** | `narrate()` 不复制，而是基于描述 + 接收者认知重新生成 |
| 4 | **先存档，确认后开发** | 本文档为冻结版，主人确认后启动 Phase 1 |
| 5 | **主观记忆 + 客观记忆** | 核心架构变更：Concept 承载客观记忆，MemoryInstance 承载主观记忆 |

---

## 二、核心架构变更：主客观记忆分离

### 2.1 三层模型（V2）

```
┌─────────────────────────────────────────────────────────────┐
│                      统一记忆层 (MemoryLayer)                  │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   客观记忆层     │    │          主观记忆层              │ │
│  │  (Objective)    │◄──►│        (Subjective)             │ │
│  │                 │    │                                 │ │
│  │  Concept        │    │  MemoryInstance                 │ │
│  │  ├── 客观描述    │    │  ├── 感官印象（结构化）          │ │
│  │  ├── 物理属性    │    │  ├── 情感标签                    │ │
│  │  ├── 历史记录    │    │  ├── 确信度/扭曲度               │ │
│  │  └── 关联实体    │    │  ├── 联想网络                    │ │
│  │                 │    │  └── 叙事文本                    │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           ▲                          ▲                      │
│           │                          │                      │
│      实体消亡时                   主体访问时                 │
│      客观记忆保留                 激活主观记忆               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 关键洞察

**客观记忆（Concept）** = "被记忆的对象本身"  
- 石头E42的客观属性：圆形、灰色、硬度50、在(10,20)
- 即使所有生物都死了，"石头E42曾存在过"这个客观事实不变
- 类似数据库中的"事实表"

**主观记忆（MemoryInstance）** = "某主体对对象的记忆"  
- 生物A的记忆："圆圆的，滑滑的，讨厌"
- 生物B的记忆："灰色的，可以用来磨刀"
- 类似数据库中的"观点表"，多个观点指向同一个事实

```
Concept: "石头E42"
├── 客观描述: {形状: "圆形", 颜色: "灰色", 硬度: 50, 位置: (10,20)}
├── 来源实体: 42 (已消亡)
└── 主观记忆实例:
    ├── MemoryInstance (subject=A): {形状: "圆形", 情感: "讨厌", 确信度: 0.9}
    ├── MemoryInstance (subject=B): {颜色: "灰色", 情感: "实用", 确信度: 0.7}
    └── MemoryInstance (subject=C, 间接): {形状: "可能是圆形", 确信度: 0.3}
```

---

## 三、核心类设计（V2 结构化版）

### 3.1 结构化感官描述

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto


class SubjectType(Enum):
    """主体类型（当前限定动物/人类）"""
    ANIMAL = auto()
    HUMAN = auto()


class ConceptType(Enum):
    """概念类型"""
    ENTITY = auto()      # 来源于实体
    ABSTRACT = auto()    # 抽象概念（如"爱情"）
    MYTH = auto()        # 神话/虚构（如"龙"）
    EVENT = auto()       # 事件（如"那场洪水"）


@dataclass
class SensoryDescription:
    """
    结构化感官描述
    
    非量化、模糊、可缺失
    例如：生物A可能记得形状但忘了颜色
    """
    shape: Optional[str] = None        # "圆形", "方形", "不规则"
    color: Optional[str] = None        # "灰色", "暗红色"
    texture: Optional[str] = None      # "光滑", "粗糙", "有鳞片"
    size: Optional[str] = None         # "小", "中等", "巨大"（相对描述）
    smell: Optional[str] = None        # "无味", "腥味", "花香"
    sound: Optional[str] = None        # "无声", "低沉", "尖锐"
    temperature: Optional[str] = None  # "冰凉", "温暖", "灼热"
    
    def to_text(self) -> str:
        """转为自然语言描述（用于叙述传播）"""
        parts = []
        if self.shape: parts.append(f"{self.shape}的")
        if self.color: parts.append(f"{self.color}的")
        if self.texture: parts.append(f"{self.texture}")
        if self.size: parts.append(f"{self.size}")
        return "".join(parts) if parts else "某物"


@dataclass
class EmotionalTag:
    """
    情感标签（可组合）
    """
    primary: str = "neutral"           # 主情感: "fear", "joy", "disgust", "trust"...
    intensity: float = 0.5             # 强度 0.0~1.0
    reason: Optional[str] = None       # 原因: "因为曾经绊倒过我"


@dataclass
class AssociationLink:
    """
    联想链接
    """
    target_concept_id: str             # 关联的概念ID
    relation_type: str                 # "similar_to", "opposite_of", "part_of", "caused_by"
    strength: float = 0.5              # 联想强度 0.0~1.0
```

### 3.2 客观记忆：Concept

```python
@dataclass
class Concept:
    """
    客观记忆 = 被记忆的对象本身
    
    独立于任何主体存在，实体消亡后仍然保留
    类似"事实表"中的一条记录
    """
    concept_id: str                    # 唯一标识 (如 "entity_42_stone")
    name: str                          # 名称
    concept_type: ConceptType          # 概念类型
    
    # === 客观描述（结构化）===
    canonical_description: SensoryDescription  # 客观感官属性
    physical_properties: Dict[str, any] = field(default_factory=dict)  # 物理属性
    
    # === 来源追踪 ===
    source_entity_id: Optional[int] = None     # 来源实体（可能已消亡）
    source_entity_type: Optional[str] = None   # 实体类型
    created_at: float = 0.0                    # 概念形成时间
    destroyed_at: Optional[float] = None       # 实体消亡时间（如适用）
    
    # === 状态 ===
    is_active: bool = True                     # 是否还有对应实体存在
    
    # === 关联 ===
    related_concepts: Set[str] = field(default_factory=set)  # 关联概念ID
    
    def mark_destroyed(self, timestamp: float) -> None:
        """标记来源实体已消亡"""
        self.is_active = False
        self.destroyed_at = timestamp
```

### 3.3 主观记忆：MemoryInstance

```python
@dataclass
class MemoryInstance:
    """
    主观记忆 = 某主体对某概念的具体记忆
    
    个性化、可能扭曲、可能遗忘
    类似"观点表"中的一条记录
    """
    memory_id: str                     # 唯一标识
    concept_id: str                    # 关联的客观概念
    subject_id: int                    # 记忆主体（实体ID）
    subject_type: SubjectType          # 主体类型
    
    # === 主观感官印象（结构化，可能缺失/扭曲）===
    sensory_impression: SensoryDescription = field(default_factory=SensoryDescription)
    
    # === 情感 ===
    emotional_tag: EmotionalTag = field(default_factory=EmotionalTag)
    
    # === 记忆质量 ===
    confidence: float = 1.0            # 确信度 0.0~1.0（"我好像记得..."）
    distortion_level: float = 0.0      # 扭曲度 0.0~1.0（与客观描述的偏差）
    clarity: float = 1.0               # 清晰度 0.0~1.0（随时间衰减）
    
    # === 联想网络 ===
    associations: List[AssociationLink] = field(default_factory=list)
    
    # === 叙事 ===
    narrative: Optional[str] = None    # "那天我踢了它，摔倒了"
    
    # === 时间 ===
    first_contact: float = 0.0         # 首次接触时间
    last_recall: float = 0.0           # 上次回忆时间
    recall_count: int = 0              # 回忆次数
    
    # === 来源 ===
    formation_type: str = "direct"     # "direct"直接体验 / "narrative"间接听闻
    source_subject_id: Optional[int] = None  # 若间接听闻，信息来源主体
    
    def decay(self, rate: float = 0.01) -> None:
        """记忆自然衰减"""
        self.clarity = max(0.0, self.clarity - rate)
        self.confidence = max(0.0, self.confidence - rate * 0.5)
    
    def recall(self, timestamp: float) -> None:
        """被回忆一次，更新统计"""
        self.last_recall = timestamp
        self.recall_count += 1
        # 回忆可能增强清晰度（但不超过原始值）
        self.clarity = min(1.0, self.clarity + 0.05)
```

### 3.4 接触记录

```python
@dataclass
class ContactRecord:
    """
    主体与实体的客观交互记录
    
    作为主观记忆形成的基础素材
    """
    contact_id: str
    subject_id: int
    subject_type: SubjectType
    entity_id: int
    concept_id: str                    # 关联的概念
    
    contact_type: str                  # "visual", "physical", "auditory", "olfactory", "narrative"
    timestamp: float
    
    # === 接触详情 ===
    duration: float = 0.0              # 接触持续时间
    intensity: float = 0.5             # 强度 0.0~1.0
    context: Optional[str] = None      # 上下文: "在河边散步时"
    
    # === 主体状态（记录时的状态，影响记忆形成）===
    subject_emotional_state: Optional[str] = None  # "calm", "fearful", "excited"
    subject_attention_level: float = 0.5           # 注意力水平
```

---

## 四、记忆传播：重新生成机制

### 4.1 核心原则

**记忆不可共享，只能重新生成。**

```
生物A的记忆 ──描述──→ 生物B的重新生成
   ↓                        ↓
"圆圆的，讨厌"         "好像听说是圆的，
                       但A说讨厌可能是因为
                       他自己不小心"
   ↓                        ↓
确信度 0.9              确信度 0.4（更低）
扭曲度 0.1              扭曲度 0.6（更高）
formation: direct       formation: narrative
```

### 4.2 传播算法

```python
def narrate_memory(
    from_subject: int,
    to_subject: int,
    concept_id: str,
    memory_layer: MemoryLayer
) -> MemoryInstance:
    """
    叙述传播：基于描述重新生成记忆
    
    不是复制，而是接收者基于：
    1. 叙述者的描述（可能不完整/扭曲）
    2. 接收者自身的认知框架（已有知识、偏见）
    3. 传播过程中的信息损失
    
    重新生成一个全新的 MemoryInstance
    """
    # 1. 获取叙述者的记忆
    narrator_memory = memory_layer.recall_memory(from_subject, concept_id)
    if not narrator_memory:
        return None
    
    # 2. 信息损失：叙述者无法完美表达记忆
    expressed_description = _express_with_loss(
        narrator_memory.sensory_impression,
        narrator_memory.confidence
    )
    
    # 3. 接收者理解：基于自身认知框架重新解释
    receiver_framework = _get_cognitive_framework(to_subject)
    interpreted_description = _interpret_with_framework(
        expressed_description,
        receiver_framework
    )
    
    # 4. 生成新记忆（重新生成，不是复制）
    new_memory = MemoryInstance(
        memory_id=generate_id(),
        concept_id=concept_id,
        subject_id=to_subject,
        subject_type=memory_layer.get_subject_type(to_subject),
        sensory_impression=interpreted_description,
        emotional_tag=_transfer_emotion_with_distortion(
            narrator_memory.emotional_tag,
            loss_factor=0.3
        ),
        confidence=narrator_memory.confidence * 0.5,  # 间接记忆确信度更低
        distortion_level=min(1.0, narrator_memory.distortion_level + 0.3),
        clarity=0.6,  # 新记忆初始清晰度中等
        formation_type="narrative",
        source_subject_id=from_subject,
        narrative=f"从{from_subject}处听说: {narrator_memory.narrative}"
    )
    
    return new_memory


def _express_with_loss(description: SensoryDescription, confidence: float) -> SensoryDescription:
    """叙述表达时的信息损失"""
    # 确信度越低，丢失的信息越多
    loss_probability = 1.0 - confidence
    
    result = SensoryDescription()
    for field in ['shape', 'color', 'texture', 'size', 'smell', 'sound', 'temperature']:
        value = getattr(description, field)
        if value and random.random() > loss_probability:
            setattr(result, field, value)
    
    return result


def _interpret_with_framework(
    description: SensoryDescription,
    framework: Dict
) -> SensoryDescription:
    """接收者基于自身认知框架重新解释"""
    # 例如：如果接收者从未见过"圆形"，可能解释为"椭圆形"
    # 如果接收者对某种颜色有偏见，可能记错颜色
    
    result = SensoryDescription()
    
    if description.shape:
        # 认知框架影响形状理解
        result.shape = _distort_shape(description.shape, framework)
    
    if description.color:
        # 色彩词汇可能因语言/文化差异而失真
        result.color = _distort_color(description.color, framework)
    
    # ... 其他字段类似处理
    
    return result
```

### 4.3 多次传播失真示例

```
原始实体: 石头E42 {形状: "圆形", 颜色: "灰色", 质地: "光滑"}

T0: 生物A直接观察
    记忆A: {形状: "圆形", 颜色: "灰色", 确信度: 0.95, 扭曲度: 0.05}

T1: A 向 B 叙述
    表达损失: A忘了说"光滑"
    记忆B: {形状: "圆形", 颜色: "灰色", 确信度: 0.48, 扭曲度: 0.35}

T2: B 向 C 叙述
    B说"可能是圆形"（B本身确信度就不高）
    C的认知: C从未见过灰色石头，以为是"暗色"
    记忆C: {形状: "可能是圆形", 颜色: "暗色", 确信度: 0.24, 扭曲度: 0.65}

T3: C 向 D 叙述
    C说"有个暗色的东西，形状不确定"
    D的想象: D补充为"暗色的方形物体"
    记忆D: {形状: "方形", 颜色: "暗色", 确信度: 0.12, 扭曲度: 0.85}

结果: 经过4次传递，"圆形灰色光滑石头"变成了"方形暗色物体"
```

---

## 五、MemoryLayer 管理器

```python
class MemoryLayer:
    """
    统一记忆层管理器（全局单例）
    
    管理：
    - 客观记忆（Concept）注册表
    - 主观记忆（MemoryInstance）图谱
    - 接触记录（ContactRecord）历史
    """
    
    def __init__(self):
        self._concepts: Dict[str, Concept] = {}
        self._memories: Dict[str, MemoryInstance] = {}  # key: "subject_id:concept_id"
        self._contacts: List[ContactRecord] = []
        self._entity_to_concept: Dict[int, str] = {}    # entity_id -> concept_id
    
    # ========== 客观记忆管理 ==========
    
    def register_entity(self, entity_id: int, entity_type: str,
                       description: SensoryDescription,
                       physical_props: Dict = None) -> Concept:
        """实体创建时注册概念"""
        concept_id = f"entity_{entity_id}_{entity_type}"
        concept = Concept(
            concept_id=concept_id,
            name=f"{entity_type}_{entity_id}",
            concept_type=ConceptType.ENTITY,
            canonical_description=description,
            physical_properties=physical_props or {},
            source_entity_id=entity_id,
            source_entity_type=entity_type,
            created_at=get_current_time()
        )
        self._concepts[concept_id] = concept
        self._entity_to_concept[entity_id] = concept_id
        return concept
    
    def entity_destroyed(self, entity_id: int, timestamp: float) -> None:
        """实体消亡时标记概念"""
        concept_id = self._entity_to_concept.get(entity_id)
        if concept_id and concept_id in self._concepts:
            self._concepts[concept_id].mark_destroyed(timestamp)
            logger.info(f"[MemoryLayer] 实体{entity_id}消亡，概念{concept_id}转为非活跃")
    
    def create_abstract_concept(self, name: str,
                                description: SensoryDescription,
                                concept_type: ConceptType = ConceptType.ABSTRACT) -> Concept:
        """创建抽象/虚构概念（无实体来源）"""
        concept_id = f"abstract_{name}_{generate_id()}"
        concept = Concept(
            concept_id=concept_id,
            name=name,
            concept_type=concept_type,
            canonical_description=description,
            source_entity_id=None,
            is_active=False  # 抽象概念从未有实体
        )
        self._concepts[concept_id] = concept
        return concept
    
    # ========== 接触记录 ==========
    
    def record_contact(self, subject_id: int, subject_type: SubjectType,
                      entity_id: int, contact_type: str,
                      intensity: float = 0.5, context: str = None) -> ContactRecord:
        """记录主体与实体的接触"""
        concept_id = self._entity_to_concept.get(entity_id)
        if not concept_id:
            return None
        
        contact = ContactRecord(
            contact_id=generate_id(),
            subject_id=subject_id,
            subject_type=subject_type,
            entity_id=entity_id,
            concept_id=concept_id,
            contact_type=contact_type,
            timestamp=get_current_time(),
            intensity=intensity,
            context=context
        )
        self._contacts.append(contact)
        
        # 接触后自动形成/更新记忆
        self._form_or_update_memory(subject_id, concept_id, contact)
        
        return contact
    
    # ========== 主观记忆管理 ==========
    
    def _form_or_update_memory(self, subject_id: int, concept_id: str,
                               contact: ContactRecord) -> MemoryInstance:
        """基于接触记录形成或更新记忆"""
        key = f"{subject_id}:{concept_id}"
        
        if key in self._memories:
            # 更新现有记忆
            memory = self._memories[key]
            memory.recall(contact.timestamp)
            # 根据新的接触信息更新感官印象
            memory.sensory_impression = _merge_sensory(
                memory.sensory_impression,
                self._concepts[concept_id].canonical_description,
                contact.intensity
            )
        else:
            # 形成新记忆
            concept = self._concepts[concept_id]
            memory = MemoryInstance(
                memory_id=generate_id(),
                concept_id=concept_id,
                subject_id=subject_id,
                subject_type=contact.subject_type,
                sensory_impression=_form_subjective_from_objective(
                    concept.canonical_description,
                    contact  # 接触时的注意力、情绪影响记忆形成
                ),
                first_contact=contact.timestamp,
                last_recall=contact.timestamp,
                formation_type="direct"
            )
            self._memories[key] = memory
        
        return memory
    
    def recall_memory(self, subject_id: int, concept_id: str) -> Optional[MemoryInstance]:
        """主体回忆某概念的记忆"""
        key = f"{subject_id}:{concept_id}"
        memory = self._memories.get(key)
        
        if memory:
            memory.recall(get_current_time())
        
        return memory
    
    def narrate_memory(self, from_subject: int, to_subject: int,
                      concept_id: str) -> Optional[MemoryInstance]:
        """
        叙述传播：重新生成记忆
        
        不是复制，而是基于描述 + 接收者认知重新生成
        """
        narrator_memory = self.recall_memory(from_subject, concept_id)
        if not narrator_memory:
            return None
        
        # 重新生成（核心算法见第4节）
        new_memory = _regenerate_memory(narrator_memory, to_subject, self)
        
        key = f"{to_subject}:{concept_id}"
        self._memories[key] = new_memory
        
        return new_memory
    
    # ========== 遗忘机制 ==========
    
    def apply_forgetting(self, subject_id: Optional[int] = None,
                        decay_rate: float = 0.01) -> None:
        """
        应用遗忘
        
        规则：
        - 清晰度低于阈值且长时间未回忆的记忆被遗忘
        - 情感强烈的记忆更难遗忘
        - 每个主体有记忆容量上限
        """
        current_time = get_current_time()
        to_forget = []
        
        for key, memory in self._memories.items():
            if subject_id and memory.subject_id != subject_id:
                continue
            
            # 自然衰减
            memory.decay(decay_rate)
            
            # 遗忘判断
            time_since_recall = current_time - memory.last_recall
            emotional_anchor = memory.emotional_tag.intensity
            
            # 遗忘概率 = f(清晰度, 时间, 情感锚定)
            forget_probability = (1 - memory.clarity) * 0.3 + \
                                (time_since_recall / 1000) * 0.5 - \
                                emotional_anchor * 0.2
            
            if forget_probability > 0.8:
                to_forget.append(key)
        
        for key in to_forget:
            del self._memories[key]
    
    def enforce_capacity_limit(self, subject_id: int, max_memories: int = 100) -> None:
        """强制记忆容量上限：遗忘最不重要的记忆"""
        subject_memories = {
            k: v for k, v in self._memories.items()
            if v.subject_id == subject_id
        }
        
        if len(subject_memories) <= max_memories:
            return
        
        # 按重要性排序（情感强度 × 清晰度 × 回忆次数）
        sorted_memories = sorted(
            subject_memories.items(),
            key=lambda kv: kv[1].emotional_tag.intensity *
                          kv[1].clarity *
                          (1 + kv[1].recall_count * 0.1),
            reverse=True
        )
        
        # 遗忘超出容量的记忆
        for key, _ in sorted_memories[max_memories:]:
            del self._memories[key]
```

---

## 六、与 ECS 集成设计

### 6.1 实体生命周期钩子

```python
# 在 World.create_entity() 中
class World:
    def create_entity(self) -> Entity:
        entity = Entity()
        # ... 原有逻辑
        
        # 注册到记忆层（如果实体类型支持）
        if hasattr(entity, '_type') and entity._type in ['animal', 'human', 'plant', 'object']:
            description = self._extract_sensory_description(entity)
            memory_layer.register_entity(entity.id, entity._type, description)
        
        return entity
    
    def remove_entity(self, entity: Entity) -> None:
        # ... 原有清理逻辑
        
        # 通知记忆层实体消亡
        memory_layer.entity_destroyed(entity.id, get_current_time())
```

### 6.2 System 访问记忆层

```python
class AnimalPerceptionSystem(System):
    """感知系统：接触时自动记录到记忆层"""
    
    def update(self, world: World, dt: float) -> None:
        memory_layer = world.get_memory_layer()  # 或通过单例访问
        
        for entity, (perception, space) in world.get_components(...):
            for detected_id, entity_type in perception.detected_entities.items():
                # 自动记录接触
                memory_layer.record_contact(
                    subject_id=entity.id,
                    subject_type=SubjectType.ANIMAL,
                    entity_id=detected_id,
                    contact_type="visual",
                    intensity=0.7
                )


class AnimalSocialSystem(System):
    """社交系统：支持记忆叙述传播"""
    
    def _share_memory(self, world: World, from_entity, to_entity) -> None:
        memory_layer = world.get_memory_layer()
        
        # 获取 from_entity 的随机记忆
        from_memories = memory_layer.get_subject_memories(from_entity.id)
        if not from_memories:
            return
        
        selected_memory = random.choice(from_memories)
        
        # 叙述传播（重新生成，不是复制）
        new_memory = memory_layer.narrate_memory(
            from_subject=from_entity.id,
            to_subject=to_entity.id,
            concept_id=selected_memory.concept_id
        )
        
        if new_memory:
            logger.debug(f"[Social] E{from_entity.id} 向 E{to_entity.id} 叙述了 {selected_memory.concept_id}")
```

### 6.3 存档/读档

```python
class MemoryLayer:
    def serialize(self) -> dict:
        """序列化所有记忆数据"""
        return {
            "concepts": {
                cid: {
                    "concept_id": c.concept_id,
                    "name": c.name,
                    "concept_type": c.concept_type.name,
                    "canonical_description": {
                        "shape": c.canonical_description.shape,
                        "color": c.canonical_description.color,
                        # ...
                    },
                    "source_entity_id": c.source_entity_id,
                    "is_active": c.is_active,
                    "created_at": c.created_at,
                    "destroyed_at": c.destroyed_at,
                }
                for cid, c in self._concepts.items()
            },
            "memories": {
                key: {
                    "memory_id": m.memory_id,
                    "concept_id": m.concept_id,
                    "subject_id": m.subject_id,
                    "sensory_impression": {
                        "shape": m.sensory_impression.shape,
                        "color": m.sensory_impression.color,
                        # ...
                    },
                    "emotional_tag": {
                        "primary": m.emotional_tag.primary,
                        "intensity": m.emotional_tag.intensity,
                    },
                    "confidence": m.confidence,
                    "distortion_level": m.distortion_level,
                    "clarity": m.clarity,
                    "formation_type": m.formation_type,
                    "source_subject_id": m.source_subject_id,
                }
                for key, m in self._memories.items()
            },
            "contacts": [
                {
                    "contact_id": c.contact_id,
                    "subject_id": c.subject_id,
                    "entity_id": c.entity_id,
                    "concept_id": c.concept_id,
                    "contact_type": c.contact_type,
                    "timestamp": c.timestamp,
                    "intensity": c.intensity,
                }
                for c in self._contacts
            ]
        }
    
    def deserialize(self, data: dict) -> None:
        """从存档恢复"""
        # 恢复概念
        for cid, cdata in data["concepts"].items():
            concept = Concept(
                concept_id=cdata["concept_id"],
                name=cdata["name"],
                concept_type=ConceptType[cdata["concept_type"]],
                canonical_description=SensoryDescription(
                    shape=cdata["canonical_description"].get("shape"),
                    color=cdata["canonical_description"].get("color"),
                    # ...
                ),
                source_entity_id=cdata.get("source_entity_id"),
                is_active=cdata["is_active"],
                created_at=cdata["created_at"],
                destroyed_at=cdata.get("destroyed_at"),
            )
            self._concepts[cid] = concept
            if concept.source_entity_id:
                self._entity_to_concept[concept.source_entity_id] = cid
        
        # 恢复记忆
        for key, mdata in data["memories"].items():
            memory = MemoryInstance(
                memory_id=mdata["memory_id"],
                concept_id=mdata["concept_id"],
                subject_id=mdata["subject_id"],
                sensory_impression=SensoryDescription(
                    shape=mdata["sensory_impression"].get("shape"),
                    # ...
                ),
                emotional_tag=EmotionalTag(
                    primary=mdata["emotional_tag"]["primary"],
                    intensity=mdata["emotional_tag"]["intensity"],
                ),
                confidence=mdata["confidence"],
                distortion_level=mdata["distortion_level"],
                clarity=mdata["clarity"],
                formation_type=mdata["formation_type"],
                source_subject_id=mdata.get("source_subject_id"),
            )
            self._memories[key] = memory
        
        # 恢复接触记录
        for cdata in data["contacts"]:
            contact = ContactRecord(
                contact_id=cdata["contact_id"],
                subject_id=cdata["subject_id"],
                entity_id=cdata["entity_id"],
                concept_id=cdata["concept_id"],
                contact_type=cdata["contact_type"],
                timestamp=cdata["timestamp"],
                intensity=cdata["intensity"],
            )
            self._contacts.append(contact)
```

---

## 七、实现路径（确认后启动）

### Phase 1: 核心骨架（3-4 天）
- [ ] 实现 `SensoryDescription`, `EmotionalTag`, `AssociationLink`
- [ ] 实现 `Concept`, `MemoryInstance`, `ContactRecord`
- [ ] 实现 `MemoryLayer` 基础 CRUD
- [ ] 实体生命周期钩子（World.create_entity / remove_entity）

### Phase 2: 记忆形成与传播（3-4 天）
- [ ] `_form_or_update_memory`：接触后自动形成记忆
- [ ] `_regenerate_memory`：叙述传播重新生成
- [ ] 信息损失算法 `_express_with_loss`
- [ ] 认知框架解释 `_interpret_with_framework`

### Phase 3: 遗忘与优化（2-3 天）
- [ ] `apply_forgetting`：自然衰减 + 遗忘判断
- [ ] `enforce_capacity_limit`：容量上限
- [ ] 性能优化（索引、缓存）

### Phase 4: ECS 集成（2-3 天）
- [ ] 修改 `World` 类添加 MemoryLayer 钩子
- [ ] 修改 `AnimalPerceptionSystem` 记录 Contact
- [ ] 修改 `AnimalSocialSystem` 支持叙述传播
- [ ] 修改 `AnimalMemoryComponent` 引用 MemoryLayer

### Phase 5: 存档与测试（2-3 天）
- [ ] `serialize` / `deserialize`
- [ ] 单元测试（概念注册、记忆形成、传播失真、遗忘）
- [ ] 集成测试（完整生命周期）

**总计：约 12-17 个工作日**

---

## 八、与现有 Animal 模块的关系

### 8.1 当前 AnimalMemoryComponent → 升级

```python
# 当前（量化、短期）
@dataclass(slots=True)
class AnimalMemoryComponent(Component):
    memories: List[MemoryEntry] = field(default_factory=list)
    max_memories: int = 20
    decay_rate: float = 0.01

# 升级后（引用统一记忆层）
@dataclass(slots=True)
class AnimalMemoryComponent(Component):
    """
    动物记忆组件（V2）
    
    不再直接存储记忆数据，而是作为统一记忆层的客户端引用
    """
    # 本地缓存（最近活跃的概念ID，用于快速查询）
    active_concept_ids: Set[str] = field(default_factory=set)
    
    # 记忆层引用（运行时注入）
    _memory_layer: Optional[MemoryLayer] = None
    
    def recall(self, concept_id: str) -> Optional[MemoryInstance]:
        """回忆某概念"""
        if self._memory_layer:
            return self._memory_layer.recall_memory(self._entity_id, concept_id)
        return None
    
    def get_all_memories(self) -> List[MemoryInstance]:
        """获取所有记忆"""
        if self._memory_layer:
            return self._memory_layer.get_subject_memories(self._entity_id)
        return []
```

### 8.2 AnimalPerceptionSystem → 增强

```python
# 增强后：感知时自动记录接触
class AnimalPerceptionSystem(System):
    def update(self, world: World, dt: float) -> None:
        memory_layer = world.get_memory_layer()
        
        for entity, (perception, space) in world.get_components(...):
            for detected_id, entity_type in perception.detected_entities.items():
                # 原有逻辑...
                
                # 新增：记录到统一记忆层
                memory_layer.record_contact(
                    subject_id=entity.id,
                    subject_type=SubjectType.ANIMAL,
                    entity_id=detected_id,
                    contact_type="visual",
                    intensity=0.7,
                    context=f"在({space.x}, {space.y})附近"
                )
```

---

## 九、结论

| 维度 | 评估 |
|------|------|
| **技术可行性** | ✅ 可行，Python 对象存储，无技术障碍 |
| **架构兼容性** | ✅ 与现有 ECS 兼容，作为元层服务 |
| **实现复杂度** | 🟡 中等偏高，约 12-17 工作日 |
| **设计成熟度** | ✅ V2 已解决核心问题（结构化、主客观分离、重新生成） |
| **价值** | 🔴 极高，从物理模拟提升到认知/文化模拟 |
| **推荐** | ✅ **建议实现** |

### 等待确认

主人确认以下设计后，我将立即启动 Phase 1 开发：

1. ✅ 结构化感官描述（形状/颜色/质地/大小/气味/声音/温度）
2. ✅ 主体限定动物/人类（SubjectType.ANIMAL / HUMAN）
3. ✅ 记忆传播 = 重新生成（基于描述 + 接收者认知 + 信息损失）
4. ✅ 主客观记忆分离（Concept = 客观，MemoryInstance = 主观）
5. ✅ 实现路径：5 Phase，约 12-17 工作日

---

*文档版本: V2（设计冻结版）*  
*最后更新: 2026-06-08*  
*作者: Agent `coder`*

# Human 模块优化方案 - ECS 架构补充组件与系统

## 一、现有架构分析

### 1.1 当前组件结构（已存在）

| 类别 | 组件名称 | 说明 |
|------|----------|------|
| **基础标识** | HumanComponent | 人类标记 |
| | AgeComponent | 年龄 |
| | GenderComponent | 性别 |
| | BodyComponent | 身体特征 |
| | IdentityComponent | 身份信息 |
| | LocationComponent | 当前位置 |

| **生理状态** | HealthComponent | HP/疲劳/伤害 |
| | PhysiologyNeedsComponent | 需求状态 |

| **认知能力** | BrainComponent | AI智能核心 |
| | MemoryComponent | 事件/地点/人物记忆 |
| | IntentComponent | 当前意图 |
| | TaskComponent | 任务状态 |
| | GoalComponent | 长期目标 |
| | PersonalityComponent | 性格特征 |
| | KnowledgeComponent | 知识技能 |
| | EmotionComponent | 情绪状态 |

| **社交关系** | RelationshipComponent | 伴侣/婚姻状态 |
| | ReproductionComponent | 繁衍相关 |

| **能力属性** | ActionComponent | 动作执行队列 |
| | SearchComponent | 搜索能力 |
| | VisionComponent | 视野范围 |
| | SkillComponent | 技能水平 |

| **物品经济** | EconomyComponent | 经济状态 |
| | InventoryComponent | 背包物品 |

### 1.2 当前系统结构（已存在）

```
human/systems/
├── core/           # 核心调度系统
│   ├── action_system.py
│   ├── planning_system.py
│   └── intent_system.py
├── physiological/   # 生理系统
│   ├── health_system.py
│   ├── hunger_system.py
│   └── physiology_needs_system.py
├── cognitive/       # 认知系统
│   ├── preception_system.py
│   ├── decision_system.py
│   ├── goal_system.py
│   └── emotion_system.py
├── social/          # 社交系统
│   ├── social_system.py
│   ├── pairing_system.py
│   └── reproduction_system.py
├── identity/        # 身份系统
│   ├── identity_system.py
│   └── biology_system.py
├── survival/        # 生存系统
│   ├── seek_food_system.py
│   └── seek_target_system.py
├── action/          # 具体动作系统（已完善）
├── death/           # 死亡处理
└── injury/          # 伤害处理
```

---

## 二、需要补充的组件 - 避免功能重复

### 2.1 ⚠️ 关键发现：现有重复与改进建议

#### 问题 1: Intent 与 Task 边界模糊
- `IntentComponent`（意图）和 `TaskComponent`（任务）职责重叠
- **解决方案**：明确分工
  - `IntentComponent`: "我想吃苹果"（愿望/需求表达）
  - `DesireComponent`: "我渴望学习烹饪"（长期愿望，影响目标生成）
  - `NeedComponent`: "我感到饥饿"（即时生理需求触发器）
  - `TaskComponent`: "做饭"（待执行的具体任务）

#### 问题 2: Memory 结构单一
- 当前只有简单的事件/地点/人物列表
- **解决方案**：扩展记忆系统
  - `EpisodicMemoryComponent`: 事件记忆（我昨天去了哪里）
  - `SemanticMemoryComponent`: 事实知识（苹果是水果）
  - `ProceduralMemoryComponent`: 程序性记忆（如何做蛋糕）
  - `WorkingMemoryComponent`: 工作记忆（短期记忆缓冲区）

#### 问题 3: 情绪系统过于简单
- `EmotionComponent` 可能存在但结构简单
- **解决方案**：增强情绪模型
  - `MoodComponent`: 基础心境（愉快/沮丧/焦虑）
  - `EmotionTrackerComponent`: 情绪强度追踪
  - `AffectComponent`: 情感影响值（对决策的影响系数）

### 2.2 🆕 建议新增组件

#### A. 扩展身体特征组件

**📄 body_detail_component.py** (创建)
```python
@dataclass
class BodyDetailComponent(Component):
    """
    身体细节组件 - 补充 BodyComponent 的细节
    
    包含：
    - 身高、体重、BMI
    - 体型（瘦/匀称/健壮）
    - 外貌特征（发型、瞳色等）
    - 肢体协调性
    """
    height: float = 170.0      # cm
    weight: float = 65.0        # kg
    bmi: float = 0.0            # 自动计算
    body_type: str = "normal"   # thin/fit/athletic/heavy
    appearance_traits: dict = field(default_factory=dict)
```

**📄 stamina_component.py** (创建)
```python
@dataclass
class StaminaComponent(Component):
    """
    体能组件 - 独立的体力系统
    
    特点：
    - 与 Health 分离（受伤 ≠ 没体力）
    - 独立恢复机制
    - 影响移动速度和负重能力
    """
    stamina: float = 100.0       # 当前体能
    max_stamina: float = 100.0   # 最大体能
    current_endurance: float = 1.0  # 耐力系数（训练后提升）
```

**📄 fatigue_detail_component.py** (创建)
```python
@dataclass
class FatigueDetailComponent(Component):
    """
    疲劳细节组件 - 区分不同类型的疲劳
    
    类型：
    - Mental: 精神疲劳（影响决策/专注）
    - Physical: 身体疲劳（影响动作速度）
    - SleepDebt: 睡眠亏空（累计未补觉）
    """
    mental_fatigue: float = 0.0   # 精神疲劳 0-100
    physical_fatigue: float = 0.0 # 身体疲劳 0-100
    sleep_debt: float = 0.0       # 睡眠亏空（小时）
```

#### B. 社交扩展组件

**📄 reputation_component.py** (创建)
```python
@dataclass
class ReputationComponent(Component):
    """
    声誉组件 - 在社区中的评价
    
    包含：
    - 整体声誉值
    - 特定领域专长（如"烹饪好"、"勇敢"）
    - 社会地位
    """
    reputation: float = 50.0           # 整体声誉 0-100
    specialties: dict = field(default_factory=dict)  # {技能: 等级}
    social_status: str = "commoner"   # commoner/noble/outlaw等
    known_for: list = field(default_factory=list)   # ["善于烹饪", "乐于助人"]
```

**📄 acquaintance_component.py** (创建)
```python
@dataclass
class AcquaintanceComponent(Component):
    """
    熟人组件 - 认识的人列表
    
    存储：
    - 认识的人物及其关系程度
    - 社交圈层级（密友/普通朋友/面熟的）
    """
    acquaintances: dict = field(default_factory=dict)  # {entity_id: relationship_data}
    social_circle: list = field(default_factory=list)   # ["邻居", "同事", "同学"]
```

**📄 role_component.py** (创建)
```python
@dataclass
class RoleComponent(Component):
    """
    角色组件 - 在群体中承担的角色
    
    例如：家庭中的父亲/母亲，职场中的经理/员工等
    """
    primary_role: str = ""           # 主要角色（职业）
    family_roles: list = field(default_factory=list)   # ["父亲", "儿子"]
    community_roles: list = field(default_factory=list) # ["志愿者", "邻居"]
```

#### C. 认知扩展组件

**📄 attention_component.py** (创建)
```python
@dataclass
class AttentionComponent(Component):
    """
    专注力组件 - 影响信息处理和任务执行
    
    作用：
    - 低专注时易分心
    - 需要休息恢复
    """
    focus: float = 100.0             # 专注度 0-100
    distraction_threshold: float = 80  # 低于此值容易被干扰
    multitasking_ability: float = 1.0  # 多任务处理能力
```

**📄 curiosity_component.py** (创建)
```python
@dataclass
class CuriosityComponent(Component):
    """
    好奇心组件 - 驱动探索行为的内在动机
    
    特点：
    - 高好奇心 → 更常主动搜索/探索
    - 可通过学习和新体验提升
    """
    curiosity: float = 50.0          # 好奇心水平 0-100
    exploration_drive: float = 1.0   # 探索驱动力系数
    interested_in: list = field(default_factory=list)  # ["历史", "科学", "音乐"]
```

**📄 creativity_component.py** (创建)
```python
@dataclass
class CreativityComponent(Component):
    """
    创造力组件 - 创新和解决问题的能力
    
    应用：
    - 工具制作
    - 艺术创作
    - 问题解决方案生成
    """
    creativity: float = 30.0         # 创造力水平
    originality: float = 1.0         # 独创性倾向
    divergent_thinking: float = 50.0 # 发散思维能力
```

#### D. 道德与价值观组件

**📄 moral_compass_component.py** (创建)
```python
@dataclass
class MoralCompassComponent(Component):
    """
    道德指南针组件 - 决策时的价值判断
    
    维度：
    - 诚实度 vs 欺骗
    - 利他 vs 自私
    - 规则遵守 vs 变通
    """
    honesty: float = 50.0            # 诚实倾向 0-100
    altruism: float = 50.0           # 利他倾向
    rule_following: float = 60.0      # 规则遵守度
    empathy: float = 50.0             # 共情能力
    fairness: float = 50.0            # 公平感
```

#### E. 工具使用组件

**📄 tool_aptitude_component.py** (创建)
```python
@dataclass
class ToolAptitudeComponent(Component):
    """
    工具熟练度组件 - 对特定工具/技能的掌握
    
    示例：
    - 使用石斧的熟练度
    - 制作陶器的能力
    """
    tools: dict = field(default_factory=dict)  # {工具名: 熟练度}
    can_use_tools: list = field(default_factory=list)  # ["石斧", "弓箭"]
```

---

## 三、需要新增或完善的关键系统

### 3.1 ⚠️ 现有问题识别

#### 问题：HealthSystem 与 PhysiologyNeedsSystem 功能重叠？

**分析：**
- `HealthSystem`: 负责 HP/疲劳管理、伤害恢复
- `PhysiologyNeedsSystem`: 应该负责生理需求（饥饿、口渴）触发意图

**结论**：两者职责可以区分，但需要明确边界

### 3.2 🆕 建议新增系统

#### A. 🌡️ EnvironmentAdaptationSystem (环境适应系统)

```python
# human/systems/environment/adaptation_system.py
class EnvironmentAdaptationSystem(System):
    """
    环境适应系统 - 处理季节和气候的影响
    
    功能：
    - 冬季增加保暖需求
    - 夏季增加解渴需求  
    - 影响衣物和行为选择
    - 季节性健康风险（如流感季节）
    """
    
    def update(self, world: World, dt):
        # 检查当前季节/天气
        weather = world.get_entity(WeatherEntity)
        
        for entity in world.entities:
            if not has(entity, HumanComponent):
                continue
            
            human = get_component(entity, HumanComponent)
            
            if is_winter:
                # 寒冷环境增加饥饿感（生火/取暖）
                add_need(human, HungerNeed, multiplier=1.3)
                
            if is_summer:
                # 炎热环境增加口渴感
                add_need(human, ThirstNeed, multiplier=1.5)
```

#### B. 🏠 HousingSystem (住所系统)

```python
# human/systems/social/housing_system.py
class HousingSystem(System):
    """
    住所系统 - 管理居住环境和家庭生活
    
    功能：
    - 家庭关系维护
    - 家宅建设与维护
    - 私有物品存储
    - 家族传承管理
    """
    
    def __init__(self):
        self.homes: dict = {}  # {entity_id: home_entity}
    
    def register_home(self, entity: Entity, home: Entity):
        """为人类注册住所"""
        self.homes[entity] = home
    
    def update_family_relations(self, world: World):
        """更新家庭成员关系状态"""
        for entity in world.entities:
            if has(entity, FamilyRoleComponent):
                # 检查是否在家、与家人的互动等
                pass
```

#### C. 💊 HealthcareSystem (医疗系统)

```python
# human/systems/health/healthcare_system.py
class HealthcareSystem(System):
    """
    医疗保健系统 - 疾病诊断与治疗
    
    功能：
    - 症状检测与疾病判断
    - 治疗方案制定
    - 用药管理
    - 康复追踪
    """
    
    def diagnose(self, entity: Entity) -> list[ Disease ]:
        """根据健康状态诊断疾病"""
        health = get_component(entity, HealthComponent)
        
        diseases = []
        
        # 发热检测
        if health.temperature > 37.5:
            diseases.append(Fever())
        
        # 感染检测
        if any(health.symptoms.values()):
            diseases.append(Infection())
        
        return diseases
    
    def prescribe_treatment(self, diseases: list[ Disease ]) -> Treatment:
        """制定治疗方案"""
        pass
```

#### D. 💵 MoneyAndTradeSystem (货币与交易系统)

```python
# human/systems/economy/money_system.py
class MoneyAndTradeSystem(System):
    """
    货币与交易系统 - 处理经济交换
    
    功能：
    - 货币持有量
    - 买卖交易
    - 市场报价
    - 经济活动记录
    """
    
    def __init__(self):
        self.money: dict = {}  # {entity_id: currency_amount}
        self.market_prices: dict = {}  # {商品: 价格}
    
    def buy(self, seller: Entity, item: str, amount: float) -> bool:
        """从卖家购买商品"""
        pass
    
    def sell(self, buyer: Entity, item: str, amount: float) -> float:
        """向买家出售商品，返回获得金额"""
        pass
```

---

## 四、组件添加策略 - 避免重复

### 4.1 检查清单（添加前必查）

在添加新组件前，按以下步骤检查：

```python
def should_create_component(component_name: str) -> bool:
    """
    组件创建前的检查逻辑
    """
    
    # 1. 检查是否已存在同名组件
    existing = search_components(component_name)
    if existing:
        return False, f"已存在：{existing}"
    
    # 2. 检查是否已有功能相似的组件
    similar = find_similar(existing_components, component_name)
    if similar and similar.confidence > 0.8:
        return False, f"与 {similar.name} 功能重叠"
    
    # 3. 如果是扩展，检查基类/父组件是否存在
    if "Component" in component_name:
        base = get_base_component(component_name)
        if not base:
            return None, "缺少基础组件"
    
    return True, ""

def analyze_component_overlap(new_name: str, existing_components: list):
    """
    分析组件重叠程度
    """
    overlaps = []
    for comp in existing_components:
        # 检查功能描述重叠
        if semantic_similarity(new_name, comp.name) > 0.7:
            overlaps.append({"name": comp.name, "similarity": score})
    
    return overlaps
```

### 4.2 组件命名规范 - 避免混乱

```
规范：{领域}_{功能}_{可选:细分}_component.py

示例：
✅ health_component.py - 基础健康状态
✅ emotion_component.py - 情绪状态  
✅ stamina_component.py - 体能/体力
❌ status_component.py - 太模糊
❌ state_component.py - 太通用
```

---

## 五、实施优先级与建议

### P0 - 高优先级（核心功能）
1. **MemoryComponent** - 升级记忆系统，区分事件/语义/程序性记忆
2. **HealthcareSystem** - 疾病诊断与治疗
3. **EnvironmentAdaptationSystem** - 季节气候适应

### P1 - 中优先级（重要功能）
4. **ReputationComponent** - 社交声誉管理
5. **MoralCompassComponent** - 道德决策支持
6. **HousingSystem** - 住所与家庭关系
7. **MoneyAndTradeSystem** - 货币交易

### P2 - 低优先级（增强功能）
8. **BodyDetailComponent** - 身体细节扩展
9. **ToolAptitudeComponent** - 工具熟练度
10. **CuriosityComponent** - 好奇心驱动探索
11. **CreativityComponent** - 创造力

---

## 六、目录结构与文件清单

### 建议新结构
```
human/
├── components/
│   ├── basic/                    # 已存在
│   ├── abilities/                # 已存在
│   ├── action/                   # 已存在
│   ├── physiological/            # 已存在
│   ├── cognitive/                # 已存在
│   ├── social/                   # 待创建（扩展社交组件）
│   ├── economic/                 # 已存在
│   ├── injury/                   # 已存在
│   └── society/                  # 待创建（新增：声誉、角色等）
│       ├── reputation_component.py
│       ├── role_component.py
│       └── acquaintance_component.py
├── systems/
│   ├── environment/              # 待创建（环境适应系统）
│   │   └── adaptation_system.py
│   ├── health/                   # 待创建（医疗诊断）
│   │   └── healthcare_system.py
│   ├── economy/                  # 待创建（货币交易）
│   │   └── money_system.py
│   └── social/                   # 已存在（扩展）
│       └── housing_system.py
```

---

## 七、关键注意事项

### ⚠️ 功能重叠检测规则

1. **同义检查**：确保新组件名称与现有组件不混淆
2. **职责边界**：每个组件只负责单一职责（SRP）
3. **数据分离**：相关但不同的数据应该分开存储
4. **逻辑独立**：处理逻辑不应交叉依赖

### ✅ 推荐添加顺序

1. 先阅读 `component/__init__.py` 了解现有结构
2. 创建新组件时，在 `__init__.py` 中添加导入和中文说明
3. 确保新组件能被 HumanFactory 正确初始化（如果需要的话）
4. 编写简单的单元测试验证组件独立性

### 📝 代码风格要求

- 保持与现有代码一致的注释格式
- 继承 Component 基类，使用 @dataclass
- 添加必要的类型提示
- 包含中文文档字符串说明用途

---

*这份文档可作为 Human 模块扩展的开发指南。建议按优先级顺序逐步实施，每次只添加少量组件以保持代码可读性。*
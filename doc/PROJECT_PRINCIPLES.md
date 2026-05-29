# 项目设计原则

> 面向开发者：ECS 架构的世界模拟系统核心设计理念与遵循的原则。

---

## 📚 目录

- [核心理念](#核心理念)
- [ECS 架构选择](#ecs-架构选择)
- [设计原则](#设计原则)
- [技术决策](#技术决策)
- [开发哲学](#开发哲学)
- [质量原则](#质量原则)
- [文档工程](#文档工程)

---

## 💡 核心理念

### 1.1 "连续物理量 + 实时视图"理论

**核心思想**：
> 底层只有连续物理量的自然演化，所有离散状态（晴/雨/季节/事件）都是物理量的实时视图。

#### 为什么需要连续物理量？

| 连续物理量 | 离散状态 |
|-----------|---------|
| 真实模拟演化轨迹 | 跳过中间过程，只记录状态点 |
| 可预测未来状态 | 需硬编码状态转移 |
| 自然产生异常事件 | 需预定义事件类型 |
| 支持插值与外推 | 无法插值 |

**示例对比**：

```python
# ❌ 离散季节
from enum import Enum
class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

# ✅ 连续季节（基于天文计算）
class Season(PhysicalClimate):
    """季节是物理量的结果，而非预设状态"""
    def get_season(self, latitude: float, declination: float, ...) -> str:
        # 根据太阳赤纬角和日地距离实时计算
        pass
```

**核心公式**：
```
季节 = f(太阳赤纬角，日地距离，纬度)
   季节
   = f(f(日地距离，时间), 地球轨道参数， latitude)

季节 = f(f(f(日地距离，时间), 地球轨道参数), 纬度)
季节 = f(f(f(f(日地距离，时间)，行星轨道参数)，天文参数)，纬度)
```

---

### 1.2 "物理驱动"的演化模型

**理论依据**：
> 物理系统不依赖随机事件——演化由连续物理量自然驱动。

```
物理演化链路：
太阳位置 → 大气顶辐射 → 连续天气物理量 → 地表光照 → 环境同步
                                              ↓
                                      统计异常检测（无硬编码事件）
```

**连续量示例**：
- 温度（0-50°C 连续值，而非"冷/热"枚举）
- 气压（1000-1050 hPa，而非"高/低"分类）
- 湿度（0-100% 连续值，而非"干燥/潮湿"状态）

#### 实时视图设计哲学

> 系统记录完整物理量的演化轨迹，离散状态（晴/雨/雪）是实时计算的结果视图。

```python
# ❌ 离散天气状态
class WeatherState(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"

# ✅ 物理天气组件 (连续量)
class PhysicalWeatherComponent(Component):
    """物理天气组件：所有量均为连续物理量"""
    
    @dataclass
    class Data:
        """连续物理量"""
        temperature: float  # °C，非离散状态
        relative_humidity: float  # %，连续量
        air_pressure: float  # hPa，连续量
        wind_speed: float  # km/h，连续量
        wind_direction: float  # degree，连续角
        cloud_cover: float  # 0-1，连续量
        rainfall: float  # mm/h，连续量
        precipitation_type: float  # -1: snow, 0: rain, 1: drizzle (连续量)
        sky_condition: float  # 0: clear, 0.3: partly cloudy
        visibility: float  # km，连续量
        snow_depth: float  # cm，连续量

    # 离散状态是实时视图
    @property
    def is_sunny(self, world):
        # 实时计算：基于 cloud_cover 和 sky_condition
        return world.cloud_cover < 0.2 and world.sky_condition > 0.5
    
    @property
    def is_raining(self, world):
        # 实时计算：基于 rainfall 和 precipitation_type
        return (world.rainfall > 0) and (world.precipitation_type > -0.5)
```

---

### 1.3 "统计异常检测"理论

**核心理念**：
> 不预设"下雨"、"雪"等事件类型，而是通过滑动窗口检测物理偏离。

```
统计异常检测流程:
滑动窗口（720 样本≈30 天）→ 计算统计量 → 检测偏离 → 标记异常
                                    ↓
                              触发事件（动态生成类型）
```

```python
weather_event_system:
"""天气事件系统"""
    
    from scipy import stats
    
    def check_event(self, world):
        """通过统计异常检测天气事件"""
        mean_temp = compute_mean(world, window=720)  # 30 天均值
        std_temp = compute_std(world, window=720)    # 30 天标准差
        
        # 检测统计异常
        if abs(temp - mean_temp) > 2 * std_temp:
            # 统计异常！触发"极端天气"事件
            # 具体类型（热/冷/多雨）由物理量决定
            pass
```

---

## 🏗️ ECS 架构选择

### 2.1 为什么选择 ECS？

| 问题 | ECS 优势 |
|------|-----------|
| 高内聚低耦合？ | ✅ System 只依赖 World 索引，不直接引用 Component |
| 单一职责？ | ✅ System 只处理单一行为；Component 只存储单一维度 |
| 数据与逻辑分离？ | ✅ Component 纯数据；System 纯逻辑 |
| 可扩展性？ | ✅ 注册新 System 只需 World 提供索引 |
| 性能？ | ✅ 双向索引实现 O(1) 查询 |

#### 传统架构的缺陷

```python
# ❌ 传统架构：紧密耦合
class GameEntity:
    def __init__(self):
        self.position = Position()      # 数据
        self.velocity = Velocity()      # 数据
        self.health = Health()          # 数据
        self.update_position()          # 逻辑
        self.render()                   # 逻辑
        self.damage(target)             # 逻辑

# 问题：
# 1. 实体持有逻辑（违反单一职责）
# 2. 数据与逻辑混在一起
# 3. 难以复用 System
```

#### ECS 架构的优势

```python
# ✅ ECS 架构：数据与逻辑分离
@dataclass
class PositionComponent(Component):
    x: int = Position
    y: int = y

@dataclass
class VelocityComponent(Component):
    vx: float = 0.0
    vy: float = 0.0

class MoveSystem(System):
    """移动系统：只处理移动逻辑"""
    def update(self, world: World, dt: float):
        # 处理所有具有这两个组件的实体
        for eid, pos, vel in world.get_components(
            PositionComponent, VelocityComponent
        ):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt

# 优势：
# 1. Component 纯数据
# 2. System 纯逻辑
# 3. System 只处理单一职责
# 4. 可扩展性强
```

---

## 📐 设计原则

### 3.1 单一职责原则 (SRP)

```
✅ 每个 System 只处理单一职责
✅ 每个 Component 只描述单一维度
❌ 一个 System 同时处理多个不相关行为
```

**违反示例**：

```python
# ❌ 违反 SRP
class AllInOneSystem(System):
    def update(self, world, dt):
        # 1. 处理天气演化
        weather_system.update(world, dt)
        
        # 2. 处理资源再生
        resource_system.update(world, dt)
        
        # 3. 处理生物代谢
        bio_system.update(world, dt)
        
        # 4. 处理人类行为
        human_system.update(world, dt)
        
        pass
```

**正确做法**：

```python
class WeatherSystem(System):
    """天气系统（单一职责：天气演化）"""
    def update(self, world, dt):
        # 只处理天气
        pass

class ResourceSystem(System):
    """资源系统"""
    def update(self, world, dt):
        # 只处理资源
        pass

# 通过 priority 控制执行顺序
```

---

### 3.2 开闭原则 (OCP)

```
✅ 对扩展开放，对修改封闭
```

**ECS 实现**：

```python
# 扩展：新增 Component
@dataclass
class NewComponent:
    new_data: int = 0

# 扩展：新增 System
class NewSystem(System):
    def update(self, world, dt):
        # 处理 new_data
        pass

# 注册
world.register_system(NewSystem, priority=5)

# 无需修改原有代码
```

---

### 3.3 里氏替换原则 (LSP)

```
子类必须能被父类替换而不影响程序
```

**应用**：

```python
class Weather(System):
    def update(self, world, dt):
        pass

class PhysicalWeatherSystem(Weather):
    """物理天气系统：继承 Weather 并扩展功能"""
    def update(self, world, dt):
        super().update(world, dt)
        # 添加物理演化逻辑
```

---

### 3.4 接口隔离原则 (ISP)

```
客户不应依赖它不使用的接口
```

**分离的接口**：

```python
class IWorldReader:
    """只读的 World 操作"""
    def get_component(self, component_type):
        ...
    def get_system(self, system_type):
        ...

class IWorldWriter:
    """写操作"""
    def add_entity(self):
        ...
    def remove_entity(self):
        ...

# 只读取的系统实现 IWorldReader
class ReadOnlySystem(System):
    def update(self, world, dt):
        # 只调用 get_component/get_system
```

---

### 3.5 依赖倒置原则 (DIP)

```
依赖抽象，而非具体实现
```

**ECS 实现**：

```python
# 系统依赖抽象 (Component 抽象)，而非具体实现
@dataclass
class PositionComponent(Component):
    x: int = 0
    y: int = 0

class MoveSystem(System):
    def update(self, world, dt):
        # 依赖抽象：遍历所有 PositionComponent
        for eid, pos in world.get_components(PositionComponent):
            # 不依赖具体 PositionComponent 实例
            ...
```

---

## 🔧 技术决策

### 4.1 Python 数据类 (Dataclass)

**选择原因**：
- ✅ 简洁：`@dataclass` 自动生成 `__init__`
- ✅ 类型检查：原生支持类型提示
- ✅ 性能：__slots__ 优化
- ✅ 序列化：自动支持 JSON

**示例**：

```python
@dataclass
class PositionComponent(Component):
    x: int = 0
    y: int = 0

# 生成：
def __init__(self, x=None, y=None):
    self.x = x if x is not None else 0
    self.y = y if y is not None else 0
```

### 4.2 双向索引

**设计原则**：

```
✅ 数据与逻辑分离
❌ Component ↔️ Component 直接关联
```

**实现**：

```python
class World:
    # 双向索引
    _components: dict[type, dict[int, Component]]
    
    def get_components(self, *types) -> dict:
        # 通过索引快速查询
        pass
```

### 4.3 World 作为全局服务中心

**职责**：

```python
class World:
    # 维护 Entity ↔ Component ↔ System 的绑定关系
    # 提供统一的查询服务
    def get_component(self, component_type, entity_id):
        pass
    
    def get_system(self, system_type):
        pass
    
    def add_component(self, entity_id, component):
        pass
```

---

## 🎯 开发哲学

### 5.1 渐进式开发

```
1. 定义 Component
2. 实现 System
3. 注册到 World
4. 测试
```

**示例流程**：

```python
# Step 1: Step 1: Define Component (定义组件)
@dataclass
class HealthComponent(Component):
    health: int = 100

# Step 2: Implement System (实现系统)
class HealthSystem(System):
    def update(self, world, dt):
        # 更新健康
        pass

# Step 3: Register to World (注册到 World)
world.register_system(HealthSystem)

# Step 4: Test (测试)
world.run_simulation(100)
```

### 5.2 最小化原则

**核心思想**：
> 每个 System 只做最少必要的处理。

**反面案例**：

```python
# ❌ 过度复杂
def update(self, world, dt):
    # 同时做所有事
    pass

# ✅ 最小化
def update(self, world, dt):
    # 只做一件事
    pass
```

### 5.3 可组合系统

**设计目标**：

```
✅ System 可组合使用（不相互关联）
❌ System 之间直接通信
```

**组合示例**：

```python
# ✅ 组合使用
class WeatherSystem(System):
    def update(self, world, dt):
        # 天气演化

class HumanActionSystem(System):
    def update(self, world, dt):
        # 人类行为

# World 自动编排执行顺序
world.register_system(WeatherSystem, priority=10)
world.register_system(HumanActionSystem, priority=20)
```

---

## 🏆 质量原则

### 6.1 性能原则

```python
# ✅ 使用双向索引（O(1)）
components = world.get_components(Component)

# ❌ 手动遍历（O(n)）
for entity in world.all_entities:
    if type(entity) == Component:
        pass
```

### 6.2 内存原则

```python
# ✅ 重用对象
@dataclass
class CachedComponent:
    pass

# ❌ 频繁创建
def update(self, world, dt):
    new_component = Component()  # 每次都创建
```

### 6.3 正确性原则

```python
# ✅ 使用类型检查
@dataclass
class ValidComponent(Component):
    valid_field: int = 0

# ❌ 无校验
@dataclass
class UnsafeComponent:
    safe_field: any = None
```

---

## 📋 文档工程原则

### 7.1 文档层次

```
README.md          → 面向用户（是什么、怎么用）
DEVELOPER_GUIDE.md → 面向贡献者（如何扩展）
DESIGN_PATTERNS.md → 设计模式
PROJECT_ARCHITECTURE.md → 架构设计
PROJECT_PRINCIPLES.md → 核心设计原则
```

**职责划分**：

| 文档 | 目标读者 | 内容示例 |
|------|---------|---------|
| README.md | 新用户/开发者 | 快速开始、架构概览、模块导航 |
| DEVELOPER_GUIDE.md | 贡献者 | 如何添加新系统、最佳实践、调试技巧 |
| DESIGN_PATTERNS.md | 资深开发者 | 设计模式应用、架构模式 |
| PROJECT_PRINCIPLES.md | 所有开发者 | 核心理念、技术决策、质量原则 |
| architecture.md | 开发者 | 模块架构、组件依赖、执行流水线 |
| TROUBLESHOOTING.md | 开发者 | 常见问题、错误处理、调试技巧 |
| DESIGN_SUMMARY.md | 所有读者 | 设计总结、核心数据流、性能优化 |

### 7.2 生物学模拟：连续演化的生命

**核心思想**：
> 生命也是连续的物理演化——阶段转换由累积物理量驱动，而非硬编码状态机。

#### GDD（有效积温）驱动生命周期

```python
# ✅ GDD 驱动阶段推进（连续物理量）
# 温度高 → GDD 累积快 → 生长快速
# 温度低 → GDD 累积慢 → 生长缓慢
# 极端条件 → GDD 零增长 → 生长停滞

# ❌ 硬编码阶段转换（离散状态）
if age > 24:
    stage = "mature"  # 忽略温度变量
```

**生物学中的连续物理量**：

| 传统离散模型 | 连续物理量模型 |
|-------------|---------------|
| 发芽/不发芽（二值） | GDD 累积 + 随机阈值（连续） |
| 幼年/成年/老年（枚举） | 衰老度 0→1（连续） |
| 高/矮（分类） | 株高 = f(biomass)（连续） |
| 耐寒/不耐寒（二值） | cold_tolerance 基因（连续值 0~1+） |
| 遗传/新物种（硬编码） | 基因漂变（连续变异 ±20%） |

#### 基因型 vs 表现型

```python
# ✅ 基因型（基因强度）→ 表现型（实际性状）
# 基因是"潜能在存"，表现型是"实际表现"
class Gene:
    name: str                # 基因名称
    strength: float          # 基因强度（连续值）
    mutation_rate: float     # 变异概率

class MorphologyComponent(Component):
    height: float            # 表现型：实际株高
    stem_thickness: float    # 表现型：实际茎粗
```

#### 遗传传递：连续性 + 随机性

```
亲本基因型 (连续向量)
    ↓ genome.copy()        # 精确复制
子代基因型 (连续向量)
    ↓ 每个基因以概率变异    # ±20% 随机偏移
子代基因型 (连续向量)
    ↓ 多代积累
群体基因多样性 (连续分布)
```

**设计原则**：
- 连续数值的变异产生自然多样性，而非硬编码的"突变/不突变"
- 子代继承亲本的"策略"而非"精确数值"
- 环境筛选适应度高的基因组合，不预设"好/坏"基因

---

### 7.3 动物模块设计原则

```
✅ 通用 ECS 架构：动物与植物共享生物学底层组件
✅ 工厂模式：统一创建接口，组件化组装
✅ 物种预设：数据驱动，新增物种只需配置文件
❌ 动物与植物硬编码耦合：通过通用的生物学层交互
```

---

## 📋 文档工程原则

```python
# ✅ 好文档（示例）
"""
World 类：管理实体与组件绑定关系

职责:
  - 维护 Entity ↔ Component ↔ System 索引
  - 提供统一的查询服务

核心方法:
  - create_entity(): 创建实体
  - get_components(): 获取组件
  - get_system(): 获取系统
  - add_component(): 添加组件
  - remove_entity(): 删除实体
```

```python
# ❌ 坏文档（示例）
class World:
    def add_component(entity, component):
        # 添加组件
        pass
```

---

## 🔚 总结与建议

### 核心原则清单（快速查阅）

| 原则 | 说明 | 示例 |
|------|------|------|
| 连续物理量 | 天气/季节用连续量 | 温度 0-50°C，非"冷/热" |
| 统计异常检测 | 检测物理偏离 | 720 样本窗口 |
| 单一职责 | 每个 System 只做一件事 | 天气/生物/人类独立系统 |
| 双向索引 | O(1) 查询 | World 维护索引 |
| 开闭原则 | 扩展不修改 | 注册新 System |
| 性能导向 | 用索引不用遍历 | get_components() |
| 文档质量 | 详细、准确 | README + DEVELOPER_GUIDE |

---

**版本**: v2.2  
**最后更新**: 2026 年 5 月 28 日  
**维护者**: ECS Core Team  
**联系**: github@example.com

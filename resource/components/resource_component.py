
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:resource_component.py
@说明:通用资源组件
@时间:2026/04/16 20:25:07
@作者:Sherry
@版本:2.0
'''

from core.component import Component
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum, auto

class ResourceState(Enum):
    """资源状态枚举"""
    AVAILABLE = auto()  # 可用
    DEPLETED = auto()   # 耗尽
    LOCKED = auto()     # 锁定
    REGENERATING = auto()  # 再生中

@dataclass
class ResourceComponent(Component):
    """
    描述环境中的资源，支持更丰富的属性和操作。
    
    属性:
        resource_type: 资源类型（如树木、果实、动物）
        amount: 当前资源数量
        max_amount: 资源最大容量
        quality: 资源质量（0.0-1.0）
        regenerable: 是否可再生
        regen_rate: 再生速率（单位/时间）
        state: 资源当前状态
        metadata: 自定义元数据字典
    """
    resource_type: str
    amount: float = 0.0
    max_amount: float = 100.0
    quality: float = 1.0
    regenerable: bool = False
    regen_rate: float = 0.0
    state: ResourceState = ResourceState.AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate_amount()
        self._validate_quality()
        self._update_state()
    
    def _validate_amount(self):
        """验证资源数量是否合法"""
        if self.amount < 0:
            self.amount = 0
        if self.max_amount <= 0:
            self.max_amount = 100.0  # 默认值
        if self.amount > self.max_amount:
            self.amount = self.max_amount
    
    def _validate_quality(self):
        """验证资源质量是否合法"""
        if self.quality < 0.0:
            self.quality = 0.0
        elif self.quality > 1.0:
            self.quality = 1.0
    
    def _update_state(self):
        """根据当前数量更新资源状态"""
        if self.state == ResourceState.LOCKED:
            return  # 锁定状态不自动更新
            
        if self.amount <= 0:
            self.state = ResourceState.DEPLETED
        elif self.amount < self.max_amount and self.regenerable:
            self.state = ResourceState.REGENERATING
        else:
            self.state = ResourceState.AVAILABLE
    
    def consume(self, amount: float) -> float:
        """
        消耗资源
        
        参数:
            amount: 尝试消耗的数量
            
        返回:
            实际消耗的数量
        """
        if self.state == ResourceState.LOCKED or self.state == ResourceState.DEPLETED:
            return 0.0
            
        actual_amount = min(amount, self.amount)
        self.amount -= actual_amount
        self._update_state()
        return actual_amount
    
    def add(self, amount: float) -> float:
        """
        添加资源
        
        参数:
            amount: 尝试添加的数量
            
        返回:
            实际添加的数量
        """
        if self.state == ResourceState.LOCKED:
            return 0.0
            
        actual_amount = min(amount, self.max_amount - self.amount)
        self.amount += actual_amount
        self._update_state()
        return actual_amount
    
    def regenerate(self, delta_time: float = 1.0):
        """
        资源再生
        
        参数:
            delta_time: 时间增量（默认为1.0）
        """
        if not self.regenerable or self.state == ResourceState.LOCKED:
            return
            
        regen_amount = self.regen_rate * delta_time
        self.add(regen_amount)
    
    def lock(self):
        """锁定资源"""
        self.state = ResourceState.LOCKED
    
    def unlock(self):
        """解锁资源"""
        self._update_state()
    
    def is_available(self) -> bool:
        """检查资源是否可用"""
        return self.state == ResourceState.AVAILABLE
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        self.metadata[key] = value

# 示例用法
if __name__ == "__main__":
    # 创建一个可再生资源
    tree = ResourceComponent(
        resource_type="树木",
        amount=50.0,
        max_amount=100.0,
        quality=0.8,
        regenerable=True,
        regen_rate=5.0
    )
    
    print(f"初始状态: 数量={tree.amount}, 状态={tree.state.name}")
    
    # 消耗资源
    consumed = tree.consume(30.0)
    print(f"消耗了 {consumed} 单位资源")
    print(f"当前状态: 数量={tree.amount}, 状态={tree.state.name}")
    
    # 资源再生
    tree.regenerate(2.0)  # 再生2个时间单位
    print(f"再生后状态: 数量={tree.amount}, 状态={tree.state.name}")
    
    # 设置和获取元数据
    tree.set_metadata("species", "橡树")
    tree.set_metadata("age", 50)
    print(f"树木种类: {tree.get_metadata('species')}, 年龄: {tree.get_metadata('age')}")


# from core.component import Component
# from dataclasses import dataclass

# @dataclass
# class ResourceComponent(Component):
#     """
#     描述环境中的资源。
#     包括资源类型和数量。
#     """
#     resource_type: str  # 资源类型（如树木、果实、动物）
#     amount: float       # 资源数量
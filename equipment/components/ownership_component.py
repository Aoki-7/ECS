#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:ownership_component.py
@说明:所有权组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class OwnershipComponent(Component):
    """
    所有权组件 - 纯数据版
    存储物品所有权信息。
    """
    # 所有者
    owner_id: Optional[int] = None
    
    # 所有权历史
    ownership_history: List[Dict] = field(default_factory=list)
    
    # 可见性
    is_visible: bool = True
    visibility_range: float = 10.0
    
    # 共享权限
    shared_with: List[int] = field(default_factory=list)
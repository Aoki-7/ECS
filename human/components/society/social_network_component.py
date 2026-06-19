#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_network_component.py
@说明:社交网络组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Set

from core.component import Component

@dataclass(slots=True)
class SocialNetworkComponent(Component):
    """
    社交网络组件 - 纯数据版
    存储社交网络关系。
    """
    # 网络成员
    members: Set[int] = field(default_factory=set)
    
    # 连接关系 {(entity_id1, entity_id2): strength}
    connections: Dict[tuple, float] = field(default_factory=dict)
    
    # 网络统计
    network_size: int = 0
    average_connectivity: float = 0.0
    
    # 影响力中心
    influence_centers: List[int] = field(default_factory=list)

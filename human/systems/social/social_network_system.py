#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
社交网络系统

管理 SocialNetworkComponent 的动态演化：
- 同步 network_size 与 members 数量
- 重新计算平均连接度
- 连接强度自然衰减
- 维护影响力中心列表
"""

from core.system import System
from core.world import World

from human.components.society.social_network_component import SocialNetworkComponent


class SocialNetworkSystem(System):
    """社交网络维护系统"""

    tick_interval = 5
    priority = 40

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        for entity, (network) in world.get_components(SocialNetworkComponent):
            # 同步成员数量
            network.network_size = len(network.members)

            # 重新计算平均连接度
            if network.network_size > 1:
                network.average_connectivity = len(network.connections) / network.network_size
            else:
                network.average_connectivity = 0.0

            # 连接强度自然衰减
            decayed = {}
            for pair, strength in network.connections.items():
                new_strength = max(0.0, strength - 0.002)
                if new_strength > 0.0:
                    decayed[pair] = new_strength
            network.connections = decayed

            # 影响力中心：取连接度最高的前 3 个成员
            if network.members:
                centrality = {}
                for (a, b), strength in network.connections.items():
                    centrality[a] = centrality.get(a, 0.0) + strength
                    centrality[b] = centrality.get(b, 0.0) + strength
                network.influence_centers = sorted(
                    centrality, key=centrality.get, reverse=True
                )[:3]
            else:
                network.influence_centers = []
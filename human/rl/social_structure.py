#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会结构系统：自动形成部落、村庄，有领导者和分工
"""
import logging
import random
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from core.system import System
from core.world import World
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from civilization.settlement.components.settlement_component import SettlementComponent, SettlementType

logger = logging.getLogger(__name__)

class RoleType(Enum):
    """角色类型"""
    LEADER = auto()      # 领导者
    WORKER = auto()      # 工人
    FARMER = auto()      # 农民
    HUNTER = auto()      # 猎人
    CRAFTSMAN = auto()   # 工匠
    SOLDIER = auto()     # 士兵
    TEACHER = auto()     # 教师
    HEALER = auto()      # 医者

@dataclass
class SocialGroup:
    """社会群体：部落或村庄"""
    group_id: int
    name: str
    group_type: str = "tribe"  # tribe / village / town / city
    leader_id: Optional[int] = None
    members: List[int] = field(default_factory=list)
    roles: Dict[int, RoleType] = field(default_factory=dict)  # 实体ID -> 角色
    settlement_id: Optional[int] = None
    territory: List[Tuple[float, float]] = field(default_factory=list)  # 领土范围
    created_time: float = 0.0
    is_active: bool = True

class SocialStructureSystem(System):
    """社会结构系统：自动形成部落、村庄，有领导者和分工"""
    tick_interval = 10  # 每10帧更新一次

    def __init__(self):
        self.groups: Dict[int, SocialGroup] = {}
        self.next_group_id = 0
        self.entity_groups: Dict[int, int] = {}  # 实体ID -> 群体ID

    def update(self, world: World, dt: float):
        """更新社会结构系统"""
        # 1. 形成新群体
        self._form_groups(world)

        # 2. 吸纳新成员
        self._absorb_new_members(world)

        # 3. 合并部落
        self._merge_groups(world)

        # 4. 选举领导者
        self._elect_leaders(world)

        # 5. 分配角色
        self._assign_roles(world)

        # 6. 升级群体
        self._upgrade_groups(world)

    def _form_groups(self, world: World):
        """形成新群体"""
        # 获取所有没有加入群体的人类
        ungrouped_humans = []
        for e, (human, pos) in world.get_components(HumanComponent, SpaceComponent):
            if e.id not in self.entity_groups:
                ungrouped_humans.append((e.id, pos.x, pos.y))

        # 如果有足够的人类，形成新群体
        if len(ungrouped_humans) >= 5:
            # 选择5个最近的人类形成群体
            center_x = sum(x for _, x, _ in ungrouped_humans) / len(ungrouped_humans)
            center_y = sum(y for _, _, y in ungrouped_humans) / len(ungrouped_humans)
            # 按距离排序
            ungrouped_humans.sort(key=lambda h: ((h[1]-center_x)**2 + (h[2]-center_y)**2)**0.5)
            members = [h[0] for h in ungrouped_humans[:5]]
            # 创建新群体
            group = SocialGroup(
                group_id=self.next_group_id,
                name=f"部落{self.next_group_id}",
                group_type="tribe",
                members=members,
                created_time=0.0
            )
            self.groups[group.group_id] = group
            for member_id in members:
                self.entity_groups[member_id] = group.group_id
            self.next_group_id += 1
            logger.info(f"[SocialStructure] 形成新部落: {group.name}, 成员: {members}")

    def _absorb_new_members(self, world: World):
        """吸纳新成员：让未加入群体的人类加入现有部落"""
        # 获取所有未加入群体的人类
        ungrouped_humans = []
        for e, (human, pos) in world.get_components(HumanComponent, SpaceComponent):
            if e.id not in self.entity_groups:
                ungrouped_humans.append((e.id, pos.x, pos.y))

        if not ungrouped_humans:
            return

        # 让每个未加入的人类尝试加入最近的部落
        for human_id, x, y in ungrouped_humans:
            nearest_group = None
            nearest_distance = float('inf')

            for group in self.groups.values():
                if not group.is_active:
                    continue

                # 计算部落中心位置
                if group.members:
                    member_positions = []
                    for member_id in group.members[:5]:  # 只取前5个成员计算中心
                        pos = world.get_component(member_id, SpaceComponent)
                        if pos:
                            member_positions.append((pos.x, pos.y))

                    if member_positions:
                        center_x = sum(x for x, _ in member_positions) / len(member_positions)
                        center_y = sum(y for _, y in member_positions) / len(member_positions)
                        distance = ((x - center_x)**2 + (y - center_y)**2)**0.5

                        if distance < nearest_distance:
                            nearest_distance = distance
                            nearest_group = group

            # 如果找到最近的部落且距离不远，加入该部落
            if nearest_group and nearest_distance < 50.0:  # 50单位距离内
                nearest_group.members.append(human_id)
                self.entity_groups[human_id] = nearest_group.group_id
                logger.info(f"[SocialStructure] 新成员加入: 实体{human_id} 加入 {nearest_group.name}")

    def _merge_groups(self, world: World):
        """合并部落：当两个部落距离很近时合并"""
        groups_to_merge = []

        # 检查所有部落对
        group_list = list(self.groups.values())
        for i in range(len(group_list)):
            for j in range(i + 1, len(group_list)):
                group1 = group_list[i]
                group2 = group_list[j]

                if not group1.is_active or not group2.is_active:
                    continue

                # 计算两个部落的中心距离
                if group1.members and group2.members:
                    # 获取部落1的中心
                    pos1 = world.get_component(group1.members[0], SpaceComponent)
                    # 获取部落2的中心
                    pos2 = world.get_component(group2.members[0], SpaceComponent)

                    if pos1 and pos2:
                        distance = ((pos1.x - pos2.x)**2 + (pos1.y - pos2.y)**2)**0.5

                        # 如果距离很近且都是部落，合并它们
                        if distance < 30.0 and group1.group_type == "tribe" and group2.group_type == "tribe":
                            groups_to_merge.append((group1, group2))

        # 执行合并
        for group1, group2 in groups_to_merge:
            if group1.group_id in self.groups and group2.group_id in self.groups:
                # 合并成员
                for member_id in group2.members:
                    if member_id not in group1.members:
                        group1.members.append(member_id)
                        self.entity_groups[member_id] = group1.group_id

                # 合并角色
                for member_id, role in group2.roles.items():
                    if member_id not in group1.roles:
                        group1.roles[member_id] = role

                # 标记部落2为不活跃
                group2.is_active = False
                del self.groups[group2.group_id]

                logger.info(f"[SocialStructure] 部落合并: {group2.name} 合并到 {group1.name}, 新成员数: {len(group1.members)}")

    def _elect_leaders(self, world: World):
        """选举领导者"""
        for group in self.groups.values():
            if group.leader_id is None and len(group.members) > 0:
                # 选择最强壮的成员作为领导者（简化：随机选择）
                leader_id = random.choice(group.members)
                group.leader_id = leader_id
                group.roles[leader_id] = RoleType.LEADER
                logger.info(f"[SocialStructure] 选举领导者: 实体{leader_id} 成为 {group.name} 的领导者")

    def _assign_roles(self, world: World):
        """分配角色"""
        for group in self.groups.values():
            # 如果角色数量不足，分配新角色
            if len(group.roles) < len(group.members):
                # 获取没有角色的成员
                unassigned_members = [m for m in group.members if m not in group.roles]
                # 分配角色
                for member_id in unassigned_members:
                    # 简化：随机分配角色
                    role = random.choice([RoleType.WORKER, RoleType.FARMER, RoleType.HUNTER, RoleType.CRAFTSMAN])
                    group.roles[member_id] = role
                    logger.debug(f"[SocialStructure] 分配角色: 实体{member_id} 成为 {role.name}")

    def _upgrade_groups(self, world: World):
        """升级群体"""
        for group in self.groups.values():
            # 根据成员数量升级群体类型
            if group.group_type == "tribe" and len(group.members) >= 10:
                group.group_type = "village"
                group.name = f"村庄{group.group_id}"
                logger.info(f"[SocialStructure] 升级群体: {group.name} 从部落升级为村庄")
                # 创建对应的定居点
                self._create_settlement_for_group(world, group, SettlementType.VILLAGE)
            elif group.group_type == "village" and len(group.members) >= 50:
                group.group_type = "town"
                group.name = f"城镇{group.group_id}"
                logger.info(f"[SocialStructure] 升级群体: {group.name} 从村庄升级为城镇")
                # 更新定居点类型
                self._update_settlement_type(world, group, SettlementType.TOWN)
            elif group.group_type == "town" and len(group.members) >= 200:
                group.group_type = "city"
                group.name = f"城市{group.group_id}"
                logger.info(f"[SocialStructure] 升级群体: {group.name} 从城镇升级为城市")
                # 更新定居点类型
                self._update_settlement_type(world, group, SettlementType.CITY)

    def _create_settlement_for_group(self, world: World, group: SocialGroup, settlement_type: SettlementType):
        """为社会群体创建定居点"""
        # 计算群体中心位置
        if not group.members:
            return

        member_positions = []
        for member_id in group.members[:10]:  # 只取前10个成员计算中心
            pos = world.get_component(member_id, SpaceComponent)
            if pos:
                member_positions.append((pos.x, pos.y))

        if not member_positions:
            return

        center_x = sum(x for x, _ in member_positions) / len(member_positions)
        center_y = sum(y for _, y in member_positions) / len(member_positions)

        # 创建定居点
        settlement = SettlementComponent(
            name=group.name,
            settlement_type=settlement_type,
            center_x=center_x,
            center_y=center_y,
            radius=20.0 + len(group.members) * 0.5,  # 根据人口调整半径
        )

        # 将所有成员加入定居点
        for member_id in group.members:
            settlement.add_resident(member_id)

        # 创建定居点实体
        settlement_entity = world.create_entity()
        world.add_component(settlement_entity, settlement)
        group.settlement_id = settlement_entity.id

        logger.info(f"[SocialStructure] 创建定居点: {settlement.name}, 类型: {settlement_type.name}, 人口: {settlement.get_population()}")

    def _update_settlement_type(self, world: World, group: SocialGroup, settlement_type: SettlementType):
        """更新定居点类型"""
        if group.settlement_id:
            settlement = world.get_component(group.settlement_id, SettlementComponent)
            if settlement:
                settlement.settlement_type = settlement_type
                settlement.name = group.name
                settlement._update_type()  # 触发类型更新
                logger.info(f"[SocialStructure] 更新定居点类型: {settlement.name} -> {settlement_type.name}")

    def get_group_info(self, group_id: int) -> Optional[SocialGroup]:
        """获取群体信息"""
        return self.groups.get(group_id)

    def get_entity_group(self, entity_id: int) -> Optional[SocialGroup]:
        """获取实体的群体"""
        group_id = self.entity_groups.get(entity_id)
        return self.groups.get(group_id) if group_id is not None else None

    def get_role_distribution(self) -> Dict[RoleType, int]:
        """获取角色分布"""
        role_counts = {}
        for group in self.groups.values():
            for role in group.roles.values():
                role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts
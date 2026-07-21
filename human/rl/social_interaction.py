#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社会互动系统：战争、贸易、外交等复杂社会互动
"""
import logging
import random
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from core.system import System
from core.world import World
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from human.rl.social_structure import SocialStructureSystem, SocialGroup, RoleType

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """互动类型"""
    WAR = auto()             # 战争
    TRADE = auto()           # 贸易
    DIPLOMACY = auto()       # 外交
    ALLIANCE = auto()        # 联盟
    RAID = auto()            # 突袭
    MIGRATION = auto()       # 迁徙
    CULTURAL_EXCHANGE = auto()  # 文化交流
    KNOWLEDGE_SHARING = auto()  # 知识分享
    FESTIVAL = auto()        # 节日庆典
    COMPETITION = auto()     # 竞争比赛
    MARRIAGE = auto()        # 联姻
    TREATY = auto()          # 条约签订

@dataclass
class SocialInteraction:
    """社会互动：两个群体之间的互动"""
    interaction_id: int
    interaction_type: InteractionType
    group1_id: int
    group2_id: int
    start_time: float = 0.0
    duration: float = 0.0
    is_active: bool = True
    result: Optional[str] = None

class SocialInteractionSystem(System):
    """社会互动系统：处理群体之间的战争、贸易、外交等互动"""
    tick_interval = 50  # 每50帧更新一次

    def __init__(self):
        self.interactions: Dict[int, SocialInteraction] = {}
        self.next_interaction_id = 0
        self.group_relations: Dict[Tuple[int, int], float] = {}  # (群体1ID, 群体2ID) -> 关系值 (-100 ~ 100)

    def update(self, world: World, dt: float):
        """更新社会互动系统"""
        # 获取社会结构系统
        social_system = None
        for system in world.systems:
            if isinstance(system, SocialStructureSystem):
                social_system = system
                break

        if not social_system or len(social_system.groups) < 2:
            return

        # 1. 初始化群体关系
        self._init_group_relations(social_system)

        # 2. 生成社会互动
        self._generate_interactions(world, social_system)

        # 3. 处理互动结果
        self._process_interactions(world, social_system)

    def _init_group_relations(self, social_system: SocialStructureSystem):
        """初始化群体关系"""
        group_ids = list(social_system.groups.keys())
        for i in range(len(group_ids)):
            for j in range(i + 1, len(group_ids)):
                group1_id = group_ids[i]
                group2_id = group_ids[j]
                key = (min(group1_id, group2_id), max(group1_id, group2_id))
                if key not in self.group_relations:
                    # 初始关系随机
                    self.group_relations[key] = random.uniform(-20, 20)

    def _generate_interactions(self, world: World, social_system: SocialStructureSystem):
        """生成社会互动"""
        if len(social_system.groups) < 2:
            return

        # 随机选择两个群体进行互动
        group_ids = list(social_system.groups.keys())
        if len(group_ids) < 2:
            return

        group1_id, group2_id = random.sample(group_ids, 2)
        group1 = social_system.groups[group1_id]
        group2 = social_system.groups[group2_id]

        # 根据群体关系决定互动类型
        key = (min(group1_id, group2_id), max(group1_id, group2_id))
        relation = self.group_relations[key]

        # 关系差 -> 战争/突袭/竞争
        if relation < -30:
            interaction_type = random.choice([
                InteractionType.WAR,
                InteractionType.RAID,
                InteractionType.COMPETITION
            ])
        # 关系一般 -> 贸易/外交/文化交流/知识分享
        elif relation < 30:
            interaction_type = random.choice([
                InteractionType.TRADE,
                InteractionType.DIPLOMACY,
                InteractionType.CULTURAL_EXCHANGE,
                InteractionType.KNOWLEDGE_SHARING,
                InteractionType.COMPETITION
            ])
        # 关系好 -> 联盟/贸易/文化交流/节日庆典/联姻
        else:
            interaction_type = random.choice([
                InteractionType.ALLIANCE,
                InteractionType.TRADE,
                InteractionType.CULTURAL_EXCHANGE,
                InteractionType.FESTIVAL,
                InteractionType.MARRIAGE,
                InteractionType.TREATY
            ])

        # 创建互动
        interaction = SocialInteraction(
            interaction_id=self.next_interaction_id,
            interaction_type=interaction_type,
            group1_id=group1_id,
            group2_id=group2_id,
            start_time=0.0,
            duration=random.uniform(10, 50)
        )
        self.interactions[interaction.interaction_id] = interaction
        self.next_interaction_id += 1

        logger.info(f"[SocialInteraction] 生成互动: {group1.name} 与 {group2.name} 进行 {interaction_type.name}")

    def _process_interactions(self, world: World, social_system: SocialStructureSystem):
        """处理互动结果"""
        for interaction in list(self.interactions.values()):
            if not interaction.is_active:
                continue

            # 互动持续时间结束
            interaction.duration -= 1
            if interaction.duration <= 0:
                interaction.is_active = False
                self._resolve_interaction(world, social_system, interaction)

    def _resolve_interaction(self, world: World, social_system: SocialStructureSystem, interaction: SocialInteraction):
        """解决互动结果"""
        group1 = social_system.groups.get(interaction.group1_id)
        group2 = social_system.groups.get(interaction.group2_id)

        if not group1 or not group2:
            return

        key = (min(interaction.group1_id, interaction.group2_id), max(interaction.group1_id, interaction.group2_id))

        if interaction.interaction_type == InteractionType.WAR:
            # 战争：人口较多的群体获胜
            if len(group1.members) > len(group2.members):
                winner, loser = group1, group2
            else:
                winner, loser = group2, group1

            # 失败者失去部分成员
            loss_count = max(1, len(loser.members) // 4)
            for _ in range(loss_count):
                if loser.members:
                    lost_member = loser.members.pop()
                    if lost_member in social_system.entity_groups:
                        del social_system.entity_groups[lost_member]
                    if lost_member in loser.roles:
                        del loser.roles[lost_member]

            # 关系恶化
            self.group_relations[key] = max(-100, self.group_relations[key] - 30)
            interaction.result = f"{winner.name} 战胜 {loser.name}"
            logger.info(f"[SocialInteraction] 战争结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.TRADE:
            # 贸易：双方关系改善
            self.group_relations[key] = min(100, self.group_relations[key] + 10)
            interaction.result = f"{group1.name} 与 {group2.name} 进行贸易"
            logger.info(f"[SocialInteraction] 贸易结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.DIPLOMACY:
            # 外交：关系小幅改善
            self.group_relations[key] = min(100, self.group_relations[key] + 5)
            interaction.result = f"{group1.name} 与 {group2.name} 进行外交"
            logger.info(f"[SocialInteraction] 外交结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.ALLIANCE:
            # 联盟：关系大幅改善
            self.group_relations[key] = min(100, self.group_relations[key] + 20)
            interaction.result = f"{group1.name} 与 {group2.name} 结成联盟"
            logger.info(f"[SocialInteraction] 联盟结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.RAID:
            # 突袭：抢夺资源
            self.group_relations[key] = max(-100, self.group_relations[key] - 20)
            interaction.result = f"{group1.name} 突袭 {group2.name}"
            logger.info(f"[SocialInteraction] 突袭结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.CULTURAL_EXCHANGE:
            # 文化交流：双方关系改善，知识互相传播
            self.group_relations[key] = min(100, self.group_relations[key] + 15)
            interaction.result = f"{group1.name} 与 {group2.name} 进行文化交流"
            logger.info(f"[SocialInteraction] 文化交流结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.KNOWLEDGE_SHARING:
            # 知识分享：双方关系改善，知识传播
            self.group_relations[key] = min(100, self.group_relations[key] + 12)
            interaction.result = f"{group1.name} 与 {group2.name} 分享知识"
            logger.info(f"[SocialInteraction] 知识分享结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.FESTIVAL:
            # 节日庆典：双方关系大幅改善
            self.group_relations[key] = min(100, self.group_relations[key] + 25)
            interaction.result = f"{group1.name} 与 {group2.name} 共同举办节日庆典"
            logger.info(f"[SocialInteraction] 节日庆典结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.COMPETITION:
            # 竞争比赛：关系可能改善或恶化
            if random.random() < 0.5:
                self.group_relations[key] = min(100, self.group_relations[key] + 5)
                interaction.result = f"{group1.name} 与 {group2.name} 进行友好竞争"
            else:
                self.group_relations[key] = max(-100, self.group_relations[key] - 5)
                interaction.result = f"{group1.name} 与 {group2.name} 进行激烈竞争"
            logger.info(f"[SocialInteraction] 竞争结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.MARRIAGE:
            # 联姻：双方关系大幅改善，可能合并群体
            self.group_relations[key] = min(100, self.group_relations[key] + 30)
            interaction.result = f"{group1.name} 与 {group2.name} 联姻"
            logger.info(f"[SocialInteraction] 联姻结果: {interaction.result}")

        elif interaction.interaction_type == InteractionType.TREATY:
            # 条约签订：双方关系稳定
            self.group_relations[key] = min(100, self.group_relations[key] + 18)
            interaction.result = f"{group1.name} 与 {group2.name} 签订条约"
            logger.info(f"[SocialInteraction] 条约签订结果: {interaction.result}")

    def get_group_relation(self, group1_id: int, group2_id: int) -> float:
        """获取两个群体的关系值"""
        key = (min(group1_id, group2_id), max(group1_id, group2_id))
        return self.group_relations.get(key, 0.0)

    def get_interaction_history(self) -> List[SocialInteraction]:
        """获取互动历史"""
        return list(self.interactions.values())

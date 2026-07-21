#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类行为可视化系统：展示动作序列和协作关系
"""
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from core.system import System
from core.world import World
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from space.space_component import SpaceComponent
from human.rl.action_primitives import ActionPrimitive, ActionPrimitiveType

logger = logging.getLogger(__name__)

@dataclass
class BehaviorRecord:
    """行为记录：存储人类的动作序列和协作关系"""
    entity_id: int
    timestamp: float
    action_type: ActionPrimitiveType
    target_entity: Optional[int] = None
    target_position: Optional[Tuple[float, float]] = None
    success: bool = True
    cooperation_partners: List[int] = field(default_factory=list)
    goal_type: Optional[str] = None

class BehaviorVisualizer(System):
    """行为可视化系统：记录和展示人类行为"""
    tick_interval = 10  # 每10帧更新一次

    def __init__(self, max_records: int = 1000):
        """
        初始化行为可视化系统
        Args:
            max_records: 最大记录数量
        """
        self.max_records = max_records
        self.behavior_records: List[BehaviorRecord] = []
        self.entity_behaviors: Dict[int, List[BehaviorRecord]] = {}  # 实体ID -> 行为记录
        self.cooperation_networks: Dict[int, List[int]] = {}  # 实体ID -> 协作伙伴
        self.action_sequences: Dict[int, List[ActionPrimitiveType]] = {}  # 实体ID -> 动作序列

    def update(self, world: World, dt: float):
        """更新行为可视化"""
        # 记录所有人类的行为
        for e, (human, intent, pos) in world.get_components(HumanComponent, IntentComponent, SpaceComponent):
            entity_id = e.id
            # 记录当前行为
            if hasattr(intent, 'current_action') and intent.current_action:
                record = BehaviorRecord(
                    entity_id=entity_id,
                    timestamp=time.time(),
                    action_type=intent.current_action.type,
                    target_entity=intent.current_action.target_entity,
                    target_position=intent.current_action.target_position,
                    success=True,
                    cooperation_partners=getattr(intent, 'cooperation_partners', []),
                    goal_type=getattr(intent, 'goal_type', None)
                )
                self._add_record(record)

        # 打印行为统计
        if len(self.behavior_records) % 100 == 0:
            self._print_behavior_stats()

    def _add_record(self, record: BehaviorRecord):
        """添加行为记录"""
        self.behavior_records.append(record)
        if len(self.behavior_records) > self.max_records:
            self.behavior_records.pop(0)

        # 更新实体行为记录
        if record.entity_id not in self.entity_behaviors:
            self.entity_behaviors[record.entity_id] = []
        self.entity_behaviors[record.entity_id].append(record)

        # 更新协作网络
        if record.cooperation_partners:
            if record.entity_id not in self.cooperation_networks:
                self.cooperation_networks[record.entity_id] = []
            for partner in record.cooperation_partners:
                if partner not in self.cooperation_networks[record.entity_id]:
                    self.cooperation_networks[record.entity_id].append(partner)

        # 更新动作序列
        if record.entity_id not in self.action_sequences:
            self.action_sequences[record.entity_id] = []
        self.action_sequences[record.entity_id].append(record.action_type)
        # 保持动作序列长度不超过20
        if len(self.action_sequences[record.entity_id]) > 20:
            self.action_sequences[record.entity_id].pop(0)

    def _print_behavior_stats(self):
        """打印行为统计"""
        logger.info("=" * 60)
        logger.info("人类行为统计")
        logger.info("=" * 60)
        logger.info(f"总行为记录数: {len(self.behavior_records)}")
        logger.info(f"活跃实体数: {len(self.entity_behaviors)}")
        logger.info(f"协作网络数: {len(self.cooperation_networks)}")

        # 动作频率统计
        action_counts = {}
        for record in self.behavior_records:
            action_type = record.action_type.name
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        logger.info("\n动作频率:")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {action}: {count}")

        # 协作关系统计
        logger.info("\n协作关系:")
        for entity_id, partners in list(self.cooperation_networks.items())[:5]:
            logger.info(f"  实体{entity_id}: 协作伙伴{len(partners)}个 - {partners}")

        # 动作序列示例
        logger.info("\n动作序列示例:")
        for entity_id, sequence in list(self.action_sequences.items())[:3]:
            logger.info(f"  实体{entity_id}: {' -> '.join([a.name for a in sequence[-5:]])}")

    def get_entity_behavior_summary(self, entity_id: int) -> Dict:
        """获取实体的行为摘要"""
        if entity_id not in self.entity_behaviors:
            return {"error": "实体不存在"}

        records = self.entity_behaviors[entity_id]
        action_counts = {}
        for record in records:
            action_type = record.action_type.name
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        return {
            "entity_id": entity_id,
            "total_actions": len(records),
            "action_counts": action_counts,
            "cooperation_partners": self.cooperation_networks.get(entity_id, []),
            "recent_actions": [r.action_type.name for r in records[-10:]]
        }

    def get_cooperation_network(self) -> Dict[int, List[int]]:
        """获取协作网络"""
        return self.cooperation_networks.copy()

    def get_action_sequences(self) -> Dict[int, List[ActionPrimitiveType]]:
        """获取所有实体的动作序列"""
        return self.action_sequences.copy()

    def export_behavior_data(self, path: str):
        """导出行为数据到文件"""
        import json
        data = {
            "behavior_records": [
                {
                    "entity_id": r.entity_id,
                    "timestamp": r.timestamp,
                    "action_type": r.action_type.name,
                    "target_entity": r.target_entity,
                    "target_position": r.target_position,
                    "success": r.success,
                    "cooperation_partners": r.cooperation_partners,
                    "goal_type": r.goal_type
                }
                for r in self.behavior_records
            ],
            "cooperation_networks": self.cooperation_networks,
            "action_sequences": {eid: [a.name for a in seq] for eid, seq in self.action_sequences.items()}
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"行为数据已导出到 {path}")

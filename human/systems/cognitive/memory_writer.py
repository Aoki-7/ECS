from human.systems.cognitive.memory_management_system import MemoryManagementSystem
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_writer.py
@说明:记忆写入器

职责：
    - 将感知到的人、地点、异常写入记忆
    - 支持传统记忆组件和统一记忆层
'''

import logging
from typing import List

from core.world import World
from human.components.perception.vision_component import VisionComponent
from human.components.cognitive.memory_component import MemoryComponent

logger = logging.getLogger(__name__)


class MemoryWriter:
    """记忆写入器"""

    def write_to_memory(
        self, world: World, observer, observer_x: float, observer_y: float,
        vision: VisionComponent, visible_ids: list, memory: MemoryComponent
    ):
        """将感知到的人、地点、异常写入记忆（传统记忆组件 + 统一记忆层）"""
        from biology.lifecycle.components.morphology_component import MorphologyComponent
        from resource.food.components.food_component import FoodComponent
        from resource.water.components.water_component import WaterComponent
        from plant.components.plant_component import PlantComponent
        from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
        from human.components.basic.human_component import HumanComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except Exception as e:
            logger.warning(f"[MemoryWriter] 获取世界时间失败: {e}")

        # === 统一记忆层集成 ===
        memory_layer = world.get_memory_layer()
        from memory_layer import SubjectType

        for eid in visible_ids:
            target = world.query_entity(eid)
            if target is None:
                continue

            t_space = world.get_component(target, 'SpaceComponent')
            dist = 0.0
            if t_space is not None:
                dist = ((t_space.x - observer_x) ** 2 + (t_space.y - observer_y) ** 2) ** 0.5

            # 人类 → 记录人物
            if world.get_component(target, HumanComponent) is not None:
                name = ""
                from identity.name_component import NameComponent
                nc = world.get_component(target, NameComponent)
                if nc is not None:
                    name = nc.get_full_name()
                MemoryManagementSystem.record_person(memory, 
                    entity_id=eid,
                    name=name or f"E{eid}",
                    relationship="seen",
                    location=(t_space.x, t_space.y) if t_space else None,
                    time=current_time,
                )
                if memory_layer is not None:
                    memory_layer.record_observation(
                        observer_id=observer.id,
                        subject_type=SubjectType.PERSON,
                        subject_id=eid,
                        position=(t_space.x, t_space.y) if t_space else None,
                        details={"name": name, "distance": dist},
                        confidence=1.0 - min(1.0, dist / max(1.0, vision.radius)),
                    )

            # 资源（食物/水）→ 记录地点
            elif world.get_component(target, FoodComponent) is not None or \
                 world.get_component(target, WaterComponent) is not None:
                resource_type = "food" if world.get_component(target, FoodComponent) else "water"
                MemoryManagementSystem.record_place(memory, 
                    place_id=eid,
                    place_type=resource_type,
                    location=(t_space.x, t_space.y) if t_space else None,
                    time=current_time,
                )
                if memory_layer is not None:
                    memory_layer.record_observation(
                        observer_id=observer.id,
                        subject_type=SubjectType.RESOURCE,
                        subject_id=eid,
                        position=(t_space.x, t_space.y) if t_space else None,
                        details={"type": resource_type, "distance": dist},
                        confidence=1.0 - min(1.0, dist / max(1.0, vision.radius)),
                    )

            # 植物 → 记录地点
            elif world.get_component(target, PlantComponent) is not None:
                MemoryManagementSystem.record_place(memory, 
                    place_id=eid,
                    place_type="plant",
                    location=(t_space.x, t_space.y) if t_space else None,
                    time=current_time,
                )

            # 尸体/死亡标记 → 记录异常事件
            elif world.get_component(target, DeadTagComponent) is not None:
                MemoryManagementSystem.add_event(memory, 
                    event_type="perception_alert",
                    description=f"发现尸体 E{eid}",
                    location=(t_space.x, t_space.y) if t_space else None,
                    time=current_time,
                )
                if memory_layer is not None:
                    memory_layer.record_observation(
                        observer_id=observer.id,
                        subject_type=SubjectType.EVENT,
                        subject_id=eid,
                        position=(t_space.x, t_space.y) if t_space else None,
                        details={"alert": "dead_body", "distance": dist},
                        confidence=1.0,
                    )

            # 生命周期阶段变化（如婴儿、老年）→ 记录事件
            lc = world.get_component(target, LifeCycleComponent)
            if lc is not None and lc.stage != "adult":
                MemoryManagementSystem.add_event(memory, 
                    event_type="perception_life_stage",
                    description=f"看到 {lc.stage} 阶段的生命体 E{eid}",
                    location=(t_space.x, t_space.y) if t_space else None,
                    time=current_time,
                )

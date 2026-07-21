#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追踪单个人类直到死亡，并输出修正后的报告（年龄单位：世界年）"""
import sys
import os
import time
import logging

sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from core.world import World
from full_simulation import FullSimulationLoop
from human.components.basic.human_component import HumanComponent
from human.components.basic.identity_component import IdentityComponent
from biology.components.gender_component import GenderComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.health_status_component import HealthStatusComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.social.social_component import SocialComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent


def get_components_snapshot(world, entity_id):
    """获取追踪目标的完整组件快照（用于最终报告）"""
    life = world.get_component(entity_id, LifeCycleComponent)
    return {
        'human': world.get_component(entity_id, HumanComponent),
        'identity': world.get_component(entity_id, IdentityComponent),
        'gender': world.get_component(entity_id, GenderComponent),
        'life': life,
        'health': world.get_component(entity_id, HealthStatusComponent),
        'memory': world.get_component(entity_id, MemoryComponent),
        'skill': world.get_component(entity_id, SkillComponent),
        'social': world.get_component(entity_id, SocialComponent),
        'inventory': world.get_component(entity_id, InventoryComponent),
        'economy': world.get_component(entity_id, EconomyComponent),
        'knowledge': world.get_component(entity_id, KnowledgeComponent),
        'tribe': world.get_component(entity_id, TribeMembershipComponent),
        'age_str': life.format_age() if life else 'unknown',
    }


def is_dead(world, entity_id):
    if entity_id not in world.entities:
        return True
    life = world.get_component(entity_id, LifeCycleComponent)
    if life and getattr(life, 'stage', 0) == LifeCycleComponent.DEAD:
        return True
    health = world.get_component(entity_id, HealthStatusComponent)
    if health and health.hp <= 0:
        return True
    return False


def format_inventory(inventory, world):
    if inventory is None:
        return 0, []
    return len(inventory.items), [
        f"item {item_id}: {world.get_component(item_id, type('C', (), {})) or '?' }"
        for item_id in inventory.items
    ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='追踪单个人类直到死亡')
    parser.add_argument('--human-count', type=int, default=10, help='初始人类数量')
    parser.add_argument('--max-steps', type=int, default=250, help='最大追踪步数')
    parser.add_argument('--delta-hours', type=float, default=10.0, help='每步代表的小时数')
    args = parser.parse_args()

    max_steps = args.max_steps
    delta_hours = args.delta_hours

    sim = FullSimulationLoop(World())
    sim.init()
    sim.create_initial_resources()
    sim.create_initial_population(human_count=args.human_count)

    # 选择第一个出现的人类作为追踪对象
    target_id = None
    for entity, (human,) in sim.world.get_components(HumanComponent):
        target_id = entity.id
        break
    if target_id is None:
        print('未找到可追踪的人类实体')
        return

    identity = sim.world.get_component(target_id, IdentityComponent)
    name = identity.name if identity else f'Entity {target_id}'
    life = sim.world.get_component(target_id, LifeCycleComponent)
    if life is not None:
        life.max_age = 25.0

    print(f'开始追踪 {name} (ID={target_id})，每步 {delta_hours}h，最多运行 {max_steps} 步...')

    start = time.time()
    history = []
    death_step = None
    final_snapshot = None
    final_memory_events = []
    final_relations = {}
    final_known_techs = set()

    for step in range(max_steps):
        if is_dead(sim.world, target_id):
            death_step = step
            # 在死亡瞬间记录最后的快照（部分组件可能已被移除）
            final_snapshot = get_components_snapshot(sim.world, target_id)
            break

        # 记录本步开始前的记忆事件数，用于检测新事件
        memory = sim.world.get_component(target_id, MemoryComponent)
        social = sim.world.get_component(target_id, SocialComponent)
        knowledge = sim.world.get_component(target_id, KnowledgeComponent)
        prev_event_count = len(memory.events) if memory else 0

        sim.update(delta_hours=delta_hours)

        # 重新读取（sim.step 后组件可能被替换/移除）
        memory = sim.world.get_component(target_id, MemoryComponent)
        social = sim.world.get_component(target_id, SocialComponent)
        knowledge = sim.world.get_component(target_id, KnowledgeComponent)
        life = sim.world.get_component(target_id, LifeCycleComponent)
        health = sim.world.get_component(target_id, HealthStatusComponent)

        # 保存记忆/关系/技术的快照（防止死亡时组件被清理）
        if memory is not None:
            final_memory_events = list(memory.events)
        if social is not None:
            final_relations = dict(social.relations)
        if knowledge is not None:
            final_known_techs = set(knowledge.known_technologies)

        new_events = final_memory_events[prev_event_count:]
        history.append({
            'step': step,
            'age': life.current_age if life else 0.0,
            'hp': health.hp if health else 0.0,
            'events_count': len(final_memory_events),
            'relations_count': len(final_relations),
            'new_events': [e['description'] for e in new_events],
        })

    elapsed = time.time() - start

    if final_snapshot is None:
        final_snapshot = get_components_snapshot(sim.world, target_id)

    identity = final_snapshot['identity']
    gender = final_snapshot['gender']
    life = final_snapshot['life']
    health = final_snapshot['health']
    skill = final_snapshot['skill']
    economy = final_snapshot['economy']
    tribe = final_snapshot['tribe']
    inventory = final_snapshot['inventory']

    known_techs = sorted(final_known_techs)
    relations = final_relations
    inventory_count = len(inventory.items) if inventory else 0
    death_reason = getattr(life, 'death_reason', None) if life else None
    final_status = '死亡' if is_dead(sim.world, target_id) else '存活'

    print('\n' + '=' * 60)
    print('  追踪报告：', name)
    print('=' * 60)
    print(f'  实体 ID: {target_id}')
    print(f'  性别: {gender.gender.name if gender else "unknown"}, 阵营: {identity.faction if identity else "unknown"}')
    print(f'  寿命: {life.format_age() if life and hasattr(life, "format_age") else (life.current_age if life else "?")}')
    print(f'  最终状态: {final_status}')
    print(f'  生命值: {health.hp if health else 0.0}/{health.max_hp if health else 0.0}')
    print(f'  伤口数量: {len(health.wounds) if health and health.wounds else 0}')
    print(f'  死因: {death_reason if death_reason else "未记录"}')
    print(f'  死亡/停止步数: {death_step} / 总尝试步数: {max_steps}')
    print(f'  模拟耗时: {elapsed:.1f} 秒')
    print(f'  所属部落: {tribe.tribe_id if tribe else "无"}')
    print(f'  财富: {economy.wealth if economy else 0.0}')
    print(f'  已知技术: {known_techs}')
    if skill and skill.skills:
        print('  技能等级:')
        for k, v in skill.skills.items():
            print(f'    - {k}: {v}')
    print(f'  社交关系: {len(relations)} 条')
    for target_id_rel, rel_type in list(relations.items())[:10]:
        print(f'    - {rel_type}: entity {target_id_rel}')
    print(f'  库存物品: {inventory_count}')
    print(f'  记忆事件数: {len(final_memory_events)}')
    print('  关键事件 (按时间倒序，前 20 条):')
    for event in reversed(final_memory_events[-20:]):
        print(f'    - {event}')
    print('  生命曲线 (每 50 步采样):')
    print('        step     age(y)       hp   events  relations')
    for sample in history[::50]:
        print(f'        {sample["step"]:>4} {sample["age"]:>8.1f} {sample["hp"]:>8.1f} {sample["events_count"]:>7} {sample["relations_count"]:>9}')
    print('=' * 60)


if __name__ == '__main__':
    main()

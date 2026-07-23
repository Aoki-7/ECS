#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追踪单个人类直到死亡，并输出报告"""
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
from human.components.social.tribe_membership_component import TribeMembershipComponent


def get_human_components(world, entity_id):
    return {
        'identity': world.get_component(entity_id, IdentityComponent),
        'gender': world.get_component(entity_id, GenderComponent),
        'life': world.get_component(entity_id, LifeCycleComponent),
        'health': world.get_component(entity_id, HealthStatusComponent),
        'memory': world.get_component(entity_id, MemoryComponent),
        'skill': world.get_component(entity_id, SkillComponent),
        'social': world.get_component(entity_id, SocialComponent),
        'inventory': world.get_component(entity_id, InventoryComponent),
        'economy': world.get_component(entity_id, EconomyComponent),
        'tribe': world.get_component(entity_id, TribeMembershipComponent),
    }


def is_dead(world, entity_id):
    if entity_id not in world.entities:
        return True
    life = world.get_component(entity_id, LifeCycleComponent)
    if life and life.stage == LifeCycleComponent.DEAD:
        return True
    health = world.get_component(entity_id, HealthStatusComponent)
    if health and health.hp <= 0:
        return True
    return False


def format_age(age_value):
    # AgeSystem 使用 YEAR_PER_STEP 0.05，所以 current_age 单位是年
    return f"{age_value:.1f} 年"


def main():
    max_steps = 300
    delta_hours = 1.0

    sim = FullSimulationLoop(World())
    sim.init()
    sim.create_initial_resources()
    sim.create_initial_population(human_count=10)

    target_id = None
    for entity, (human,) in sim.world.get_components(HumanComponent):
        target_id = entity.id
        break
    if target_id is None:
        print("未找到可追踪的人类实体")
        return

    identity = sim.world.get_component(target_id, IdentityComponent)
    name = identity.name if identity else f"Entity {target_id}"
    life = sim.world.get_component(target_id, LifeCycleComponent)
    if life is not None:
        life.max_age = 30.0

    print(f"开始追踪 {name} (ID={target_id})，每步 {delta_hours}h，最多运行 {max_steps} 步...")

    history = []
    death_step = None
    start = time.perf_counter()

    for step in range(max_steps):
        sim.update(delta_hours=delta_hours)
        if is_dead(sim.world, target_id):
            death_step = step + 1
            break
        if step % 30 == 0:
            comps = get_human_components(sim.world, target_id)
            history.append({
                'step': step + 1,
                'age': comps['life'].current_age if comps['life'] else 0,
                'hp': comps['health'].hp if comps['health'] else 0,
                'events': len(comps['memory'].events) if comps['memory'] else 0,
                'relations': len(comps['social'].relations) if comps['social'] else 0,
                'inventory': len(comps['inventory'].items) if comps['inventory'] else 0,
                'wealth': comps['economy'].wealth if comps['economy'] else 0,
                'tribe': comps['tribe'].tribe_id if comps['tribe'] else None,
                'known_techs': list(comps['memory'].known_technologies) if hasattr(comps['memory'], 'known_technologies') else [],
            })

    elapsed = time.perf_counter() - start
    comps = get_human_components(sim.world, target_id)
    print_report(comps, death_step, max_steps, elapsed, history, target_id)


def print_report(comps, death_step, max_steps, elapsed, history, target_id):
    life = comps['life']
    health = comps['health']
    identity = comps['identity']
    gender = comps['gender']
    social = comps['social']
    memory = comps['memory']
    skill = comps['skill']
    inventory = comps['inventory']
    economy = comps['economy']
    tribe = comps['tribe']

    print("\n" + "=" * 60)
    print(f"  追踪报告：{identity.name if identity else f'Entity {target_id}'}")
    print("=" * 60)
    print(f"  实体 ID: {target_id}")
    print(f"  性别: {gender.gender if gender else '未知'}, 阵营: {identity.faction if identity else '无'}")
    print(f"  寿命: {format_age(life.current_age) if life else '未知'}")
    print(f"  最终状态: {LifeCycleComponent.STAGE_NAMES.get(life.stage, '未知') if life else '未知'}")
    print(f"  生命值: {health.hp if health else '?'}/{health.max_hp if health else '?'}")
    print(f"  伤口数量: {len(health.wounds) if health else 0}")
    print(f"  死因: {life.death_reason if life and life.death_reason else '未记录'}")
    print(f"  死亡/停止步数: {death_step if death_step else '未死亡'} / 总尝试步数: {max_steps}")
    print(f"  模拟耗时: {elapsed:.1f} 秒")
    print(f"  所属部落: {tribe.tribe_id if tribe else '无'}")
    print(f"  财富: {economy.wealth if economy else 0.0}")
    print(f"  已知技术: {list(getattr(memory, 'known_technologies', [])) if memory else []}")
    print(f"  技能等级:")
    if skill:
        for name, level in skill.skills.items():
            print(f"    - {name}: {level}")
    else:
        print(f"    - 无")
    print(f"  社交关系: {len(social.relations) if social else 0} 条")
    if social and social.relations:
        for other_id, relation in list(social.relations.items())[:20]:
            print(f"    - {other_id}: {relation}")
    print(f"  库存物品: {len(inventory.items) if inventory else 0}")
    if inventory and inventory.items:
        for item_entity, qty in list(inventory.items.items())[:20]:
            print(f"    - {item_entity}: {qty:.2f}")
    print(f"  记忆事件数: {len(memory.events) if memory else 0}")
    if memory and memory.events:
        print(f"  关键事件 (按时间倒序，前 20 条):")
        for event in sorted(memory.events, key=lambda e: e.get('time', 0), reverse=True)[:20]:
            print(f"    - {event}")
    else:
        print(f"  关键事件: 无")

    print(f"\n  生命曲线 (每 30 步采样):")
    print(f"    {'step':>8} {'age(y)':>8} {'hp':>8} {'events':>8} {'relations':>10} {'inventory':>10} {'wealth':>8}")
    for h in history:
        print(f"    {h['step']:>8} {h['age']:>8.1f} {h['hp']:>8.1f} {h['events']:>8} {h['relations']:>10} {h['inventory']:>10} {h['wealth']:>8.1f}")
    print("=" * 60)


if __name__ == '__main__':
    main()
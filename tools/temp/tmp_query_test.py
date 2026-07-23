#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.world import World
from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.social.social_component import SocialComponent
from human.human_factory import HumanFactory

world = World()
entity = HumanFactory.create_human(world, name='Test', x=0, y=0)

print('Query SkillComponent:')
for item in world.get_components(SkillComponent):
    print(type(item), len(item), item)

print('Query SkillComponent, KnowledgeComponent:')
for item in world.get_components(SkillComponent, KnowledgeComponent):
    print(type(item), len(item), item)

print('Query SkillComponent, KnowledgeComponent, MemoryComponent:')
for item in world.get_components(SkillComponent, KnowledgeComponent, MemoryComponent):
    print(type(item), len(item), item)
    for sub in item[1]:
        print(type(sub), sub)
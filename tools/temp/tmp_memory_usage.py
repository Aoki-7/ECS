import os
import re

# 分析旧版 MemoryComponent 的字段使用
target_fields = [
    'events', 'places', 'people', 'recent_successes', 'MAX_EVENTS', 'MAX_PEOPLE'
]

files_using_memory = [
    'biology/lifecycle/death/systems/death_event_system.py',
    'civilization/systems/civilization_system.py',
    'civilization/systems/technology_system.py',
    'examples/long_term_simulation.py',
    'examples/rl_intent_demo.py',
    'human/entities/human_entity.py',
    'human/rl/environment.py',
    'human/rl/hierarchical_rl_intent_system.py',
    'human/rl/rl_intent_system.py',
    'human/rules/human_rules.py',
    'human/systems/action/drink_system.py',
    'human/systems/action/eat_system.py',
    'human/systems/action/harvest_system.py',
    'human/systems/action/movement_system.py',
    'human/systems/action/planting_system.py',
    'human/systems/action/search_strategies.py',
    'human/systems/action/search_system.py',
    'human/systems/action/sleep_system.py',
    'human/systems/action/socialize_system.py',
    'human/systems/cognitive/attention_allocator.py',
    'human/systems/cognitive/decision_system.py',
    'human/systems/cognitive/memory_decay_system.py',
    'human/systems/cognitive/memory_management_system.py',
    'human/systems/cognitive/memory_writer.py',
    'human/systems/cognitive/perception_system.py',
    'human/systems/core/intent_system.py',
    'human/systems/core/resource_finder.py',
    'human/systems/interaction/dialogue_system.py',
    'human/systems/social/recruit_system.py',
    'human/systems/social/tribe_system.py',
    'tests/human/test_circadian_integration.py',
    'tests/human/test_human_memory_integration.py',
    'tests/human/test_memory_management_system.py',
    'tests/human/rl/test_extended_rl.py',
    'tests/human/rl/test_hierarchical_rl.py',
    'tests/human/rl/test_rl_intent.py',
]

for field in target_fields:
    print(f'=== Field: {field} ===')
    count = 0
    for file_path in files_using_memory:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找类似 memory.events 或 mem.events 的访问
                    pattern = r'\b\w+\.' + re.escape(field) + r'\b'
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f'  {file_path}: {len(matches)} usages')
                        count += len(matches)
            except Exception as e:
                print(f'  Error reading {file_path}: {e}')
    print(f'Total: {count}')
    print()
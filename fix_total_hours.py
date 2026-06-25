import os
import re

# Files that need total_hours fix (from runtime errors)
target_files = [
    'environment/physics_weather/systems/weather_event_system.py',  # WeatherEventGen
    'human/systems/social/recruit_system.py',  # RecruitSystem
    'human/systems/social/leadership_system.py',  # LeadershipSystem
    'human/systems/social/reproduction_system.py',  # ReproductionSystem
]

for filepath in target_files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace world.get_time().total_hours with safe version
        new_content = re.sub(
            r'world\.get_time\(\)\.total_hours',
            '(world.get_time().total_hours if world.get_time() else 0.0)',
            content
        )
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'[已修复] {filepath}')
        else:
            print(f'[无需修改] {filepath}')
    else:
        print(f'[不存在] {filepath}')

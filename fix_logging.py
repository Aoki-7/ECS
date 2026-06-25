import os, re

# 批量添加 isEnabledFor 检查
files_to_fix = [
    'animal\\systems\\animal_migration_system.py',
    'animal\\systems\\animal_reproduction_system.py',
    'animal\\systems\\animal_social_system.py',
    'animal\\systems\\animal_territory_system.py',
    'animal\\systems\\grazing_system.py',
    'animal\\systems\\predation_system.py',
    'biology\\ecology\\population_dynamics_system.py',
    'biology\\ecology\\speciation_migrator.py',
    'biology\\ecology\\trophic_level_system.py',
    'biology\\lifecycle\\corpse\\systems\\corpse_system.py',
    'biology\\systems\\needs_system.py',
    'biology\\systems\\smell_diffusion_system.py',
    'civilization\\systems\\crafting_system.py',
    'civilization\\systems\\product_creator.py',
]

for rel_path in files_to_fix:
    path = os.path.join(os.getcwd(), rel_path)
    if not os.path.exists(path):
        print(f'SKIP (not found): {rel_path}')
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 logger.debug(f"...") 为条件检查版本
    original = content
    content = re.sub(
        r'([ \t]+)logger\.debug\(f"([^"]+)"\)',
        r'\1if logger.isEnabledFor(logging.DEBUG):\n\1    logger.debug(f"\2")',
        content
    )
    
    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'FIXED: {rel_path}')
    else:
        print(f'NO CHANGE: {rel_path}')

print('Done')

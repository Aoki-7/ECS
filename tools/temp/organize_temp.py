import os
import shutil

# 本次架构分析产生的临时文件
analysis_files = [
    'tools/memory_usage.txt',
    'tools/migration_files.txt',
    'tools/project_structure.txt',
    'tools/tmp_cleanup.py',
    'tools/tmp_cleanup2.py',
    'tools/tmp_compare.py',
    'tools/tmp_memory_usage.py',
    'tools/tmp_move_tools.py',
    'tools/tmp_search.py',
]

temp_dir = 'tools/temp'
os.makedirs(temp_dir, exist_ok=True)

moved = []
for f in analysis_files:
    if os.path.exists(f):
        try:
            shutil.move(f, os.path.join(temp_dir, os.path.basename(f)))
            moved.append(f)
            print(f'Moved: {f}')
        except Exception as e:
            print(f'Error moving {f}: {e}')
    else:
        print(f'Not found: {f}')

print(f'\nTotal moved: {len(moved)}')
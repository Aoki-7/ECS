import os
import shutil

files_to_move = [
    'tmp_search.py',
    'tmp_compare.py',
    'tmp_memory_usage.py',
    'tmp_move_tools.py',
    'project_structure.txt',
    'migration_files.txt',
    'memory_usage.txt',
]

tools_dir = 'tools'
os.makedirs(tools_dir, exist_ok=True)

moved = []
for f in files_to_move:
    if os.path.exists(f):
        try:
            shutil.move(f, os.path.join(tools_dir, f))
            moved.append(f)
            print(f'Moved: {f}')
        except Exception as e:
            print(f'Error moving {f}: {e}')
    else:
        print(f'Not found: {f}')

print(f'\nTotal moved: {len(moved)}')
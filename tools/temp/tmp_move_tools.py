import os
import shutil

files_to_move = [
    'benchmark.py',
    'debug_settlement.py',
    'filter_results.py',
    'find_final_stats.py',
    'find_social_structure.py',
    'perf_test.py',
    'simulation_monitor.py',
    'summarize_results.py',
    'tmp_query_test.py',
    'tmp_track_human.py',
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
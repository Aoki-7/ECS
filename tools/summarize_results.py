import json
from collections import Counter

with open('scan_results.json', encoding='utf-8') as f:
    data = json.load(f)

def is_real_file(path):
    ignore = ['scan_audit.py', 'analyze_results.py', 'check_perf.py', 
              'check_component_purity.py', 'calculate_code_nums.py', 
              'full_simulation.py', 'simulation_monitor.py']
    for i in ignore:
        if i in path:
            return False
    return True

# 获取真实问题（排除扫描脚本误报）
real_bugs = [b for b in data['critical_bugs'] if is_real_file(b['file']) and '递归' not in b['risk']]
real_arch = [a for a in data['architecture_issues'] if is_real_file(a['file'])]
real_perf = [p for p in data['performance_issues'] if is_real_file(p['file'])]
missing = data['missing_capabilities']

print(f'真实严重BUG: {len(real_bugs)}')
print(f'真实架构问题: {len(real_arch)}')
print(f'真实性能问题: {len(real_perf)}')
print(f'缺失能力: {len(missing)}')

# 按文件分组统计
bug_files = Counter(b['file'] for b in real_bugs)
print('\n严重BUG最多的文件:')
for f, c in bug_files.most_common(10):
    print(f'  {f}: {c}')

# 架构问题最多的文件
arch_files = Counter(a['file'] for a in real_arch)
print('\n架构问题最多的文件:')
for f, c in arch_files.most_common(10):
    print(f'  {f}: {c}')

# 性能问题最多的文件
perf_files = Counter(p['file'] for p in real_perf)
print('\n性能问题最多的文件:')
for f, c in perf_files.most_common(10):
    print(f'  {f}: {c}')

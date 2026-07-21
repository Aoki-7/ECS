import json

with open('scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def is_real_file(path):
    ignore = ['scan_audit.py', 'analyze_results.py', 'check_perf.py', 
              'check_component_purity.py', 'calculate_code_nums.py', 'full_simulation.py']
    for i in ignore:
        if i in path:
            return False
    return True

# 严重BUG（排除递归误报和扫描脚本）
real_bugs = [b for b in data['critical_bugs'] if is_real_file(b['file']) and '递归' not in b['risk']]
print('真实严重BUG:', len(real_bugs))
for b in real_bugs[:15]:
    print(f"  {b['file']}:{b['line']}")
    print(f"    风险: {b['risk'][:100]}")
    print(f"    修复: {b['fix'][:100]}")
    print()

# 架构问题
real_arch = [a for a in data['architecture_issues'] if is_real_file(a['file'])]
print('真实架构问题:', len(real_arch))
for a in real_arch[:15]:
    print(f"  {a['file']}:{a['line']}")
    print(f"    风险: {a['risk'][:100]}")
    print(f"    修复: {a['fix'][:100]}")
    print()

# 性能问题
real_perf = [p for p in data['performance_issues'] if is_real_file(p['file'])]
print('真实性能问题:', len(real_perf))
for p in real_perf[:15]:
    print(f"  {p['file']}:{p['line']}")
    print(f"    风险: {p['risk'][:100]}")
    print(f"    修复: {p['fix'][:100]}")
    print()

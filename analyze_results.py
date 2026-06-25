import json
from collections import Counter

with open('scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 严重BUG分类 ===')
bugs = data['critical_bugs']
categories = Counter()
for b in bugs:
    if '静默吞异常' in b['risk']:
        categories['静默吞异常'] += 1
    elif 'while True' in b['risk']:
        categories['无限循环'] += 1
    elif '集合' in b['risk'] or '字典' in b['risk']:
        categories['集合遍历修改'] += 1
    elif 'None' in b['risk'] or 'AttributeError' in b['risk']:
        categories['空引用'] += 1
    elif 'EventBus' in b['risk']:
        categories['Event泄漏'] += 1
    elif '内存泄漏' in b['risk']:
        categories['内存泄漏'] += 1
    elif '递归' in b['risk']:
        categories['递归无限制'] += 1
    else:
        categories['其他'] += 1

for k, v in categories.most_common():
    print(f'  {k}: {v}')

print('\n=== 架构问题分类 ===')
arch = data['architecture_issues']
arch_cats = Counter()
for a in arch:
    if '业务方法' in a['risk']:
        arch_cats['Component含业务逻辑'] += 1
    elif 'System' in a['risk'] and '行' in a['risk']:
        arch_cats['System过重'] += 1
    elif '封装' in a['risk']:
        arch_cats['破坏封装'] += 1
    elif 'Event' in a['risk']:
        arch_cats['Event风暴'] += 1
    else:
        arch_cats['其他'] += 1

for k, v in arch_cats.most_common():
    print(f'  {k}: {v}')

print('\n=== 性能问题分类 ===')
perf = data['performance_issues']
perf_cats = Counter()
for p in perf:
    if '嵌套' in p['risk'] or 'O(n' in p['risk']:
        perf_cats['嵌套循环'] += 1
    elif 'IO' in p['risk']:
        perf_cats['Tick内IO'] += 1
    elif '对象' in p['risk']:
        perf_cats['高频对象创建'] += 1
    elif '日志' in p['risk']:
        perf_cats['热路径日志'] += 1
    elif '重复' in p['risk']:
        perf_cats['重复获取组件'] += 1
    else:
        perf_cats['其他'] += 1

for k, v in perf_cats.most_common():
    print(f'  {k}: {v}')

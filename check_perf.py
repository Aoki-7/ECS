import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

perf = data['performance_issues']
print('性能问题:', len(perf))
for p in perf[:20]:
    print(f"  {p['file']}:{p['line']}: {p['risk'][:80]}")

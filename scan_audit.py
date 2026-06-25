import os, re, sys
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(r'D:\个人助手\workspace\ECS')

results = {
    'critical_bugs': [],
    'architecture_issues': [],
    'performance_issues': [],
    'missing_capabilities': [],
    'suspected_issues': [],
}

def add_issue(category, file_path, line_no, code_snippet, risk, fix):
    rel_path = str(file_path.relative_to(PROJECT_ROOT)) if file_path.is_relative_to(PROJECT_ROOT) else str(file_path)
    results[category].append({
        'file': rel_path,
        'line': line_no,
        'code': code_snippet.strip()[:200],
        'risk': risk,
        'fix': fix,
    })

def scan_critical_bugs():
    """扫描严重BUG"""
    for f in PROJECT_ROOT.rglob('*.py'):
        if 'test' in f.name.lower() or 'reports' in str(f):
            continue
        try:
            content = f.read_text(encoding='utf-8')
            lines = content.split('\n')
        except:
            continue

        for i, line in enumerate(lines, 1):
            # 1. 静默吞异常
            if re.match(r'\s*except\s*:\s*pass\s*$', line):
                add_issue('critical_bugs', f, i, line,
                    "静默吞异常，隐藏真实错误，导致调试困难",
                    "改为 `except Exception as e: logger.warning(f'...: {e}')`")

            # 2. while True 无退出条件
            if 'while True' in line:
                # 检查后续是否有break/return
                next_20 = '\n'.join(lines[i:min(i+20, len(lines))])
                if 'break' not in next_20 and 'return' not in next_20 and 'raise' not in next_20:
                    add_issue('critical_bugs', f, i, line,
                        "while True 无退出条件，可能导致无限循环",
                        "添加break/return条件或max_iter限制")

            # 3. 集合遍历中修改
            if 'for ' in line and ('.remove(' in line or '.pop(' in line):
                add_issue('critical_bugs', f, i, line,
                    "在遍历集合时修改集合，导致RuntimeError或遗漏元素",
                    "先收集要删除的元素，遍历结束后再删除")

            # 4. get_component后无None检查直接访问
            if 'get_component' in line and '=' in line:
                var = line.split('=')[0].strip().split()[-1]
                next_5 = '\n'.join(lines[i:min(i+5, len(lines))])
                if var and f'{var}.' in next_5 and 'if ' not in next_5 and 'None' not in next_5:
                    add_issue('critical_bugs', f, i, line,
                        f"get_component结果'{var}'可能为None，直接访问属性会AttributeError",
                        f"添加 `if {var} is not None:` 检查")

            # 5. 直接修改遍历中的字典
            if 'for ' in line and 'in ' in line and 'items()' in line:
                next_10 = '\n'.join(lines[i:min(i+10, len(lines))])
                if 'del ' in next_10 or 'pop(' in next_10:
                    add_issue('critical_bugs', f, i, line,
                        "遍历字典时可能修改字典结构",
                        "使用list(dict.items())或先收集键再删除")

            # 6. EventBus订阅未清理（内存泄漏）
            if 'subscribe' in line and 'unsubscribe' not in content:
                add_issue('critical_bugs', f, i, line,
                    "EventBus订阅后无对应unsubscribe，长期运行导致内存泄漏",
                    "在on_remove或实体销毁时调用unsubscribe")

            # 7. 创建实体后未使用（泄漏）
            if 'create_entity' in line and '=' in line:
                var = line.split('=')[0].strip().split()[-1]
                rest = '\n'.join(lines[i:])
                if var and re.search(rf'\b{re.escape(var)}\b', rest) is None:
                    add_issue('critical_bugs', f, i, line,
                        "创建实体后未引用，可能导致内存泄漏",
                        "确保实体被添加到World或有其他引用")

            # 8. 递归调用无深度限制
            if 'def ' in line and '(' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if func_name in content[:content.find(line)]:
                    add_issue('critical_bugs', f, i, line,
                        "函数可能递归调用自身，无深度限制可能导致栈溢出",
                        "添加递归深度限制或改为迭代实现")

def scan_architecture():
    """扫描ECS架构问题"""
    for f in PROJECT_ROOT.rglob('*.py'):
        if 'test' in f.name.lower():
            continue
        try:
            content = f.read_text(encoding='utf-8')
            lines = content.split('\n')
        except:
            continue

        for i, line in enumerate(lines, 1):
            # 1. Component含业务逻辑（方法定义）
            if 'class ' in line and 'Component' in line:
                class_start = i
                # 找类结束位置
                class_end = len(lines)
                for j in range(i, min(i+50, len(lines))):
                    if j > i and lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                        class_end = j
                        break
                class_body = '\n'.join(lines[i:class_end])
                # 检查是否有非__init__、非to_dict、非from_dict的方法
                methods = re.findall(r'\n\s+def (\w+)\(', class_body)
                data_methods = {'__init__', '__post_init__', 'to_dict', 'from_dict', '__getattr__', '__setattr__', '__repr__', '__eq__', '__hash__'}
                biz_methods = [m for m in methods if m not in data_methods]
                if biz_methods:
                    add_issue('architecture_issues', f, i, line,
                        f"Component含业务方法{biz_methods}，违反ECS纯数据原则",
                        f"将{biz_methods}迁移到对应System")

            # 2. System过重（行数>200）
            if 'class ' in line and 'System' in line and 'Component' not in line:
                class_start = i
                class_end = len(lines)
                for j in range(i, min(i+300, len(lines))):
                    if j > i and lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                        class_end = j
                        break
                class_lines = class_end - class_start
                if class_lines > 200:
                    add_issue('architecture_issues', f, i, line,
                        f"System类{class_lines}行，超过200行，职责过重",
                        "拆分为多个子System，每个职责单一")

            # 3. World直接操作（非委托）
            if 'world._entity_manager' in line or 'world._component_store' in line:
                add_issue('architecture_issues', f, i, line,
                    "直接访问World内部属性，破坏封装",
                    "使用World提供的公共API")

            # 4. 重复Query（同一Tick多次查询相同组件）
            if 'get_components' in line:
                # 简单检测：同一函数内多次get_components
                pass  # 需要更复杂的函数级分析

            # 5. Event风暴（高频publish）
            if 'publish' in line and 'tick' in content.lower():
                add_issue('architecture_issues', f, i, line,
                    "Tick内可能高频publish事件，导致Event风暴",
                    "使用Event缓冲或批量处理，降低publish频率")

def scan_performance():
    """扫描性能问题"""
    for f in PROJECT_ROOT.rglob('*.py'):
        if 'test' in f.name.lower():
            continue
        try:
            content = f.read_text(encoding='utf-8')
            lines = content.split('\n')
        except:
            continue

        for i, line in enumerate(lines, 1):
            # 1. O(n²)嵌套循环
            if 'for ' in line:
                next_30 = '\n'.join(lines[i:min(i+30, len(lines))])
                nested = next_30.count('for ') + next_30.count('while ')
                if nested >= 2:
                    add_issue('performance_issues', f, i, line,
                        f"嵌套循环深度{nested}，可能O(n²)或更差",
                        "使用空间索引、缓存或批处理优化")

            # 2. Tick内IO操作
            if ('open(' in line or 'write(' in line or 'read(' in line or 'save(' in line or 'load(' in line) and 'def update' in content:
                add_issue('performance_issues', f, i, line,
                    "Tick内可能执行IO操作，阻塞模拟线程",
                    "将IO操作移到单独线程或使用异步IO")

            # 3. 高频对象创建
            if 'new ' in line or 'create_' in line or 'dict()' in line or 'list()' in line:
                if 'def update' in content or 'tick' in content.lower():
                    add_issue('performance_issues', f, i, line,
                        "Tick内高频创建对象，增加GC压力",
                        "使用对象池或预分配")

            # 4. 重复获取组件
            if 'get_component' in line:
                var = line.split('=')[0].strip().split()[-1] if '=' in line else ''
                if var:
                    rest = '\n'.join(lines[i:min(i+20, len(lines))])
                    # 检查同一变量是否再次get_component
                    if f'get_component' in rest and var in rest:
                        add_issue('performance_issues', f, i, line,
                            "同一Tick内重复获取组件，浪费CPU",
                            "缓存组件引用，避免重复查询")

            # 5. 热路径日志
            if 'logger.' in line or 'print(' in line:
                if 'def update' in content or 'tick' in content.lower():
                    add_issue('performance_issues', f, i, line,
                        "Tick内高频日志，IO开销大",
                        "使用logger.isEnabledFor检查或降低日志级别")

def scan_missing_capabilities():
    """扫描世界模拟能力缺失"""
    # 检查已存在的组件/系统
    all_components = set()
    all_systems = set()
    for f in PROJECT_ROOT.rglob('*.py'):
        name = f.name.lower()
        if 'component' in name:
            all_components.add(name.replace('_component.py', ''))
        if 'system' in name and 'system' in name:
            all_systems.add(name.replace('_system.py', ''))

    # 生理维度检查
    physiological = {'hunger', 'thirst', 'sleep', 'energy', 'health', 'temperature', 'disease', 'immune'}
    missing_phys = physiological - all_components
    if missing_phys:
        add_issue('missing_capabilities', PROJECT_ROOT / 'human', 0, '',
            f"生理维度缺失组件: {missing_phys}",
            f"新增组件: {missing_phys}")

    # 心理维度检查
    psychological = {'emotion', 'personality', 'mood', 'stress', 'memory', 'cognition'}
    missing_psych = psychological - all_components
    if missing_psych:
        add_issue('missing_capabilities', PROJECT_ROOT / 'human', 0, '',
            f"心理维度缺失组件: {missing_psych}",
            f"新增组件: {missing_psych}")

    # 社会维度检查
    social = {'relationship', 'social', 'tribe', 'family', 'reputation', 'culture', 'political'}
    missing_social = social - all_components
    if missing_social:
        add_issue('missing_capabilities', PROJECT_ROOT / 'human', 0, '',
            f"社会维度缺失组件: {missing_social}",
            f"新增组件: {missing_social}")

    # 行为维度检查
    behavioral = {'goal', 'plan', 'intent', 'action', 'behavior', 'skill', 'learning'}
    missing_behav = behavioral - all_components
    if missing_behav:
        add_issue('missing_capabilities', PROJECT_ROOT / 'human', 0, '',
            f"行为维度缺失组件: {missing_behav}",
            f"新增组件: {missing_behav}")

    # 生态维度检查
    ecological = {'ecosystem', 'biodiversity', 'niche', 'competition', 'symbiosis', 'predation'}
    missing_eco = ecological - all_components
    if missing_eco:
        add_issue('missing_capabilities', PROJECT_ROOT / 'ecology', 0, '',
            f"生态维度缺失组件: {missing_eco}",
            f"新增组件: {missing_eco}")

# 执行扫描
print("扫描严重BUG...")
scan_critical_bugs()
print(f"发现 {len(results['critical_bugs'])} 个严重BUG")

print("扫描架构问题...")
scan_architecture()
print(f"发现 {len(results['architecture_issues'])} 个架构问题")

print("扫描性能问题...")
scan_performance()
print(f"发现 {len(results['performance_issues'])} 个性能问题")

print("扫描缺失能力...")
scan_missing_capabilities()
print(f"发现 {len(results['missing_capabilities'])} 个缺失能力")

# 输出摘要
print("\n=== 扫描摘要 ===")
print(f"严重BUG: {len(results['critical_bugs'])}")
print(f"架构问题: {len(results['architecture_issues'])}")
print(f"性能问题: {len(results['performance_issues'])}")
print(f"缺失能力: {len(results['missing_capabilities'])}")

# 保存结果到文件
import json
with open('scan_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("结果已保存到 scan_results.json")

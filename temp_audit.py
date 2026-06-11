import os
import ast

print('=== core/ 目录结构 ===')
for root, dirs, files in os.walk('core'):
    if '__pycache__' in root:
        continue
    level = root.replace('core', '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for f in files:
        if f.endswith('.py'):
            print(f'{subindent}{f}')

print('\n=== 检查各模块边界 ===')
# 检查每个模块的导入
module_imports = {}
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root or '.git' in root or 'reports' in root:
        continue
    module = root.split(os.sep)[0] if root != '.' else 'root'
    if module not in module_imports:
        module_imports[module] = {'imports': set(), 'imported_by': set()}
    
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        parts = alias.name.split('.')
                        if parts[0] in ['human', 'animal', 'plant', 'biology', 'civilization', 'environment', 'resource', 'equipment']:
                            module_imports[module]['imports'].add(parts[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        parts = node.module.split('.')
                        if parts[0] in ['human', 'animal', 'plant', 'biology', 'civilization', 'environment', 'resource', 'equipment']:
                            module_imports[module]['imports'].add(parts[0])
        except:
            pass

# 找出跨层导入
layer_order = {'core': 0, 'space': 1, 'time_module': 1, 'save_load': 1, 'config': 1,
               'environment': 2, 'biology': 3, 'plant': 3, 'animal': 3, 'human': 3,
               'civilization': 4, 'resource': 4, 'equipment': 4, 'memory_layer': 5,
               'identity': 3, 'physiology': 3, 'garbage': 3, 'decomposer': 3,
               'death_archive': 3, 'rules': 4, 'presentation': 5, 'application': 6,
               'integration_tests': 6, 'world': 2}

print('\n=== 跨层导入（高层导入低层 = 正常，低层导入高层 = 问题） ===')
for module, info in sorted(module_imports.items()):
    if not info['imports']:
        continue
    my_layer = layer_order.get(module, 99)
    for imported in sorted(info['imports']):
        imported_layer = layer_order.get(imported, 99)
        if imported_layer > my_layer:
            print(f'  问题: {module} (L{my_layer}) -> {imported} (L{imported_layer})')
        elif imported_layer < my_layer:
            print(f'  正常: {module} (L{my_layer}) -> {imported} (L{imported_layer})')

print('\n=== core/ 下非核心内容检查 ===')
core_files = []
for root, dirs, files in os.walk('core'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            path = os.path.join(root, f)
            # 检查是否包含业务逻辑
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                tree = ast.parse(content)
                has_business_logic = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # 检查方法数量
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        real_methods = [m for m in methods if m.name not in ('__init__', 'to_dict', 'from_dict', '__post_init__')]
                        if real_methods:
                            has_business_logic = True
                            print(f'  含方法: {f:40s} -> {node.name} ({len(real_methods)} methods)')
                if not has_business_logic:
                    core_files.append(f)
            except:
                pass

print(f'\n  纯数据/工具文件: {len(core_files)}')
for f in core_files:
    print(f'    {f}')

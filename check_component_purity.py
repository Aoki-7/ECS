import os
import ast

def check_component_purity(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = ''
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                
                if base_name == 'Component':
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name in ('__init__', 'to_dict', 'from_dict', '__post_init__', '__repr__'):
                                continue
                            if not item.name.startswith('_'):
                                issues.append(f'  {node.name}.{item.name}')
    return issues

components_dir = '.'
for root, dirs, files in os.walk(components_dir):
    for file in files:
        if file.endswith('_component.py'):
            filepath = os.path.join(root, file)
            issues = check_component_purity(filepath)
            if issues:
                print(f'{filepath}:')
                for issue in issues:
                    print(issue)
                print()

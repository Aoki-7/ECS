import ast
import os

def get_dataclass_fields(file_path):
    """获取 dataclass 的字段名"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        fields = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'Component':
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                fields.append(item.target.id)
        return fields
    except Exception as e:
        return [f'ERROR: {e}']

components = [
    ('Disease', 'biology/components/disease_component.py', 'human/components/health/disease_component_v4.py'),
    ('Emotion', 'human/components/cognitive/emotion_component.py', 'human/components/cognitive/emotion_component_v4.py'),
    ('Memory', 'human/components/cognitive/memory_component.py', 'human/components/cognitive/memory_component_v4.py'),
    ('Social', 'human/components/social/social_component.py', 'human/components/social/social_component_v4.py'),
]

for name, old_path, new_path in components:
    print(f'=== {name}Component ===')
    old_fields = get_dataclass_fields(old_path)
    new_fields = get_dataclass_fields(new_path)
    print(f'Old fields: {old_fields}')
    print(f'New fields: {new_fields[:10]}...')
    print(f'Common fields: {set(old_fields) & set(new_fields)}')
    print(f'Only in old: {set(old_fields) - set(new_fields)}')
    print(f'Only in new: {set(new_fields) - set(old_fields)}')
    print()
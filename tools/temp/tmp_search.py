import os

patterns = [
    ('DiseaseComponent (biology)', 'from biology.components.disease_component import'),
    ('EmotionComponent (old)', 'from human.components.cognitive.emotion_component import'),
    ('MemoryComponent (old)', 'from human.components.cognitive.memory_component import'),
    ('SocialComponent (old)', 'from human.components.social.social_component import'),
]

for name, pattern in patterns:
    print(f'=== {name} ===')
    count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', '.git', 'venv', 'tool_results']]
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                try:
                    with open(path, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                        if pattern in content:
                            print(f'  {path}')
                            count += 1
                except Exception:
                    pass
    print(f'Total: {count}')
    print()

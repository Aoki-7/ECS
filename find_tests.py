import os

test_dirs = []
for root, dirs, files in os.walk('.'):
    if 'test' in os.path.basename(root).lower() and os.path.basename(root) not in ['.pytest_cache', '__pycache__']:
        test_dirs.append(root)
    if 'conftest.py' in files:
        test_dirs.append(root + ' (has conftest.py)')

print('Found', len(test_dirs), 'test-related directories:')
for d in test_dirs[:20]:
    print('  ', d)

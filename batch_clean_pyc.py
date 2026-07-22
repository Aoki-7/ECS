import os
import shutil
from pathlib import Path

# 修改为你的项目根目录，"."表示当前目录
ROOT_DIR = Path(".")

def clean_python_cache(root_dir: Path):
    pycache_count = 0
    pyc_count = 0

    # 删除 __pycache__
    for pycache_dir in root_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)
            pycache_count += 1
            print(f"删除目录: {pycache_dir}")

    # 删除 .pyc 文件
    for pyc_file in root_dir.rglob("*.pyc"):
        if pyc_file.is_file():
            pyc_file.unlink()
            pyc_count += 1
            print(f"删除文件: {pyc_file}")

    print("\n====== 清理完成 ======")
    print(f"删除 __pycache__ 目录: {pycache_count} 个")
    print(f"删除 .pyc 文件: {pyc_count} 个")


if __name__ == "__main__":
    clean_python_cache(ROOT_DIR)
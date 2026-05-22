#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境模块测试统一运行入口

运行所有测试:
    cd D:\个人助手\workspace\ECS
    python -m environment.tests.runner

或单独运行某一模块:
    python -m environment.tests.test_components
    python -m environment.tests.test_physics
    python -m environment.tests.test_systems
    python -m environment.tests.test_pipeline
    python -m environment.tests.test_scenarios
"""

import sys
import os
import io

# 强制 UTF-8 输出（避免 Windows GBK 编码错误）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from environment.tests.base import T

# 各测试模块
from environment.tests import test_components
from environment.tests import test_physics
from environment.tests import test_systems
from environment.tests import test_pipeline
from environment.tests import test_scenarios


MODULES = [
    ("组件单元测试", test_components),
    ("物理常量与边界", test_physics),
    ("系统单元测试", test_systems),
    ("管线与工厂", test_pipeline),
    ("场景与长期稳定性", test_scenarios),
]


def run_all():
    T.reset()
    print("=" * 55)
    print("  环境模块综合测试套件")
    print("=" * 55)

    for name, module in MODULES:
        print(f"\n{'-' * 55}")
        print(f"  >> {name}")
        print(f"{'-' * 55}")
        try:
            module.run()
        except Exception as e:
            T.fail(f"模块 {name} 抛出异常", str(e))
            import traceback
            traceback.print_exc()

    return T.summary()


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)

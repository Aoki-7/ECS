#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
application/ — 应用层

职责：
    - 编排领域系统（domain/）和框架（core/）
    - 提供模拟入口（SimulationLoop）
    - 管理生命周期（初始化 → 运行 → 清理）

设计原则：
    - 本层是框架与领域之间的胶水层
    - 允许导入任何下层模块（core, space, time_module, environment, human, biology, ...）
    - 不允许被 domain/ 内的业务系统反向导入
"""

from .simulation_loop import SimulationLoop

__all__ = ["SimulationLoop"]

"""
社交系统包 — 关系维护、配对、繁衍

依赖:
    - human/systems/
    - human/
    - core/
    - biology/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交系统包 — 关系管理与群体行为

包含：
    - SocialSystem      : 社交网络维护（关系亲密度更新、社交能量恢复）
    - PairingSystem     : 配对系统（择偶标准评估、配对提议与接受）
    - ReproductionSystem: 人类繁衍（怀孕、分娩、育儿分配）
    - TribeSystem       : 部落管理（成员归属、领土划分、领导权）

与 biology/lifecycle/birth/ 的关系：
    - social/ 的 ReproductionSystem 处理人类特有的社会性繁衍（择偶、育儿）
    - biology/lifecycle/birth/ 处理通用的出生创建逻辑
"""


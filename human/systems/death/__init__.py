"""
human/systems/death 子模块

依赖:
    - human/
    - core/
    - biology/
    - space/
    - environment/
    - memory_layer/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类死亡系统包 — 人类特有的死亡处理

说明：
    - 通用死亡判定已迁移至 biology/lifecycle/death/（统一版 CreatureDeathTriggerSystem）
    - 本目录保留人类特有的死亡后续处理（如遗产分配、社会关系断裂）
    - HumanDeathTriggerSystem: 检测人类特有死亡条件（绝望、过劳等）
"""


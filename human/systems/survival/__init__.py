"""
人类系统 — 最复杂的智能实体（认知、社交、经济、行动流水线） 的 子模块

依赖：
    - human.systems/
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生存系统包 — 资源获取与危机应对

包含：
    - SeekFoodSystem   : 寻食逻辑（评估食物稀缺度、选择觅食策略）
    - SeekTargetSystem : 通用目标搜索（根据意图类型选择最优目标实体）
    - ShelterSystem    : 庇护所寻找（恶劣天气时的遮蔽需求）

与 systems/action/ 的关系：
    - survival/ 负责"决定去找什么"（策略层）
    - action/ 负责"实际去找到并获取"（执行层）
"""


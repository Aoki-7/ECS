"""
认知系统包 — 感知→情绪→思维→目标→决策→规划

依赖:
    - human/systems/
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
认知系统包 — 感知、情绪、思维与决策

包含：
    - PerceptionSystem : 环境感知（视野填充、威胁识别、资源发现）
    - EmotionSystem    : 情绪更新（生理→环境→行为→社交四层驱动）
    - ThoughtSystem    : 内心独白生成（基于情绪+需求+当前行为）
    - GoalSystem       : 长期目标管理（按人生阶段设定目标）
    - DecisionSystem   : 多层决策（生理+情绪+性格+记忆+目标综合评估）

数据流：
    PerceptionSystem → EmotionSystem → ThoughtSystem → GoalSystem
    → DecisionSystem → IntentSystem（core/）
"""



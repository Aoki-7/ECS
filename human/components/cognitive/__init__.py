#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认知组件包 — 人类的思维、决策与记忆

包含：
    - BrainComponent      : 思维核心（当前思考内容、决策模式）
    - IntentComponent     : 当前意图（目标实体、目标位置、预期结果）
    - TaskComponent       : 任务状态（任务队列、当前进度、优先级）
    - GoalComponent       : 长期目标（人生阶段目标、成就追踪）
    - MemoryComponent     : 记忆存储（事件记忆、空间记忆、社交记忆）
    - PersonalityComponent: 性格特征（五大人格维度、风险偏好）
    - KnowledgeComponent  : 知识技能（已知配方、地图信息、文化知识）

认知流水线：
    PerceptionSystem → EmotionSystem → ThoughtSystem → GoalSystem
    → IntentSystem → DecisionSystem → PlanningSystem → ActionSystem

感知-记忆反馈环路（v2.0）：
    PerceptionSystem 将视觉发现实时写入 MemoryComponent
        · 看到人类 → record_person（名字、关系、信任度）
        · 看到资源 → record_place（食物/水源位置、情感值）
        · 看到异常 → add_event（尸体/敌人警报事件）
    SearchSystem 从 MemoryComponent 读取历史位置辅助搜索
        · 视觉扫描失败 → 记忆回溯 → 扩大探索 → 随机漫游
        · 发现目标后立即 record_place，无需等待动作完成
    MemoryDecaySystem 定期衰减过期记忆
        · events：按 impact + age 衰减，低 impact 旧事件优先遗忘
        · places：按 visits + last_visit 衰减，少访问地点逐渐遗忘
        · people：按 trust 衰减，低信任度人物逐渐遗忘
"""

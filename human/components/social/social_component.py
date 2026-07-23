#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_component.py
@说明:社交组件 - 统一入口（转发到v4版本）
@时间:2026/07/20
@版本:4.0

注意：此文件现在重定向到 social_component_v4.py，以实现版本统一。
旧的 v2 实现已备份到 social_component_legacy.py。
新版组件提供完整的 v2 API 兼容属性（relations/relation_strength/conflicts 等）。
'''

from human.components.social.social_component_v4 import (
    SocialManagerComponent,
    Relationship,
    SocialInteraction,
    SocialRoleInfo,
    SocialStatusInfo,
    RelationshipType,
    RelationshipStrength,
    SocialRole,
    SocialStatus,
    InteractionType,
)

# 为旧版导入提供兼容别名
SocialComponent = SocialManagerComponent

__all__ = [
    "SocialComponent",
    "SocialManagerComponent",
    "Relationship",
    "SocialInteraction",
    "SocialRoleInfo",
    "SocialStatusInfo",
    "RelationshipType",
    "RelationshipStrength",
    "SocialRole",
    "SocialStatus",
    "InteractionType",
]
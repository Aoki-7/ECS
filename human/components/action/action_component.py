#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:action_component.py
@说明:行为组件（兼容代理）
@时间:2026/03/13
@版本:2.0

已迁移至 core/components/action_component.py
此文件保留用于向后兼容，将在下一版本中删除。
'''

from core.components.action_component import ActionComponent, ActionType, ActionStatus

__all__ = ["ActionComponent", "ActionType", "ActionStatus"]

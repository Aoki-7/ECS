#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ActionManagementSystem 测试

v4.0 新增 — 测试动作管理系统的纯数据化迁移
"""

import pytest

from core.world import World
from core.entity import Entity

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.systems.action.action_management_system import ActionManagementSystem


class TestActionManagementSystem:
    """测试动作管理系统"""

    @pytest.fixture
    def action(self):
        return ActionComponent()

    def test_reset(self, action):
        """测试重置动作"""
        action.current_action = ActionType.EAT
        action.status = ActionStatus.RUNNING
        action.progress = 0.5
        action.target_entity = 42

        ActionManagementSystem.reset(action)

        assert action.current_action == ActionType.IDLE
        assert action.status == ActionStatus.IDLE
        assert action.progress == 0.0
        assert action.target_entity is None

    def test_queue_action(self, action):
        """测试加入队列"""
        ActionManagementSystem.queue_action(action, ActionType.EAT)
        ActionManagementSystem.queue_action(action, ActionType.DRINK)

        assert len(action.action_queue) == 2
        assert action.action_queue[0] == ActionType.EAT

    def test_dequeue_action(self, action):
        """测试取出队列"""
        action.action_queue = [ActionType.EAT, ActionType.DRINK]

        next_action = ActionManagementSystem.dequeue_action(action)
        assert next_action == ActionType.EAT
        assert len(action.action_queue) == 1

    def test_dequeue_empty(self, action):
        """测试空队列"""
        next_action = ActionManagementSystem.dequeue_action(action)
        assert next_action == ActionType.IDLE

    def test_clear_queue(self, action):
        """测试清空队列"""
        action.action_queue = [ActionType.EAT, ActionType.DRINK]
        ActionManagementSystem.clear_queue(action)
        assert len(action.action_queue) == 0

    def test_is_idle(self, action):
        """测试空闲状态"""
        assert ActionManagementSystem.is_idle(action) is True

        action.current_action = ActionType.EAT
        assert ActionManagementSystem.is_idle(action) is False

    def test_is_running(self, action):
        """测试运行状态"""
        assert ActionManagementSystem.is_running(action) is False

        action.status = ActionStatus.RUNNING
        assert ActionManagementSystem.is_running(action) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
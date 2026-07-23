#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具背包组件，存储实体拥有的所有工具
"""
from dataclasses import dataclass, field
from typing import List, Optional
from core.component import Component
from .tool_component import ToolComponent
from .tool_type import ToolType

@dataclass(slots=True)
class ToolInventoryComponent(Component):
    """工具背包组件"""
    tools: List[ToolComponent] = field(default_factory=list)
    active_tool_type: Optional[ToolType] = None  # 当前装备的工具类型

    def add_tool(self, tool: ToolComponent):
        """添加工具"""
        self.tools.append(tool)
        # 自动装备第一个对应类型的工具
        if self.active_tool_type is None:
            self.active_tool_type = tool.tool_type

    def get_tool(self, tool_type: ToolType) -> Optional[ToolComponent]:
        """获取指定类型的可用工具（未损坏的）"""
        for tool in self.tools:
            if tool.tool_type == tool_type and not tool.is_broken():
                return tool
        return None

    def get_active_tool(self) -> Optional[ToolComponent]:
        """获取当前装备的工具"""
        if self.active_tool_type is None:
            return None
        return self.get_tool(self.active_tool_type)

    def equip_tool(self, tool_type: ToolType):
        """装备指定类型的工具"""
        if self.get_tool(tool_type) is not None:
            self.active_tool_type = tool_type

    def remove_broken_tools(self):
        """移除所有损坏的工具"""
        self.tools = [t for t in self.tools if not t.is_broken()]

    def has_tool(self, tool_type: ToolType) -> bool:
        """是否有可用的指定类型工具"""
        return self.get_tool(tool_type) is not None
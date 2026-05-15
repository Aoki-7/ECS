


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:component_generator.py
@说明:自动生成ECS组件的工具类
@时间:2026/03/09 10:33:48
@作者:Sherry
@版本:1.0
'''


import os
import re
from datetime import datetime

class ComponentGenerator:
    """
    ECS Component 自动生成器
    """

    def __init__(self, output_dir="components"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ------------------------------
    # 工具
    # ------------------------------

    def _camel_to_snake(self, name):
        """驼峰转snake"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _build_fields(self, fields):
        """生成字段代码"""
        lines = []

        for name, typ, default, comment in fields:

            if isinstance(default, str):
                default = f'"{default}"'

            lines.append(
                f"    {name}: {typ} = {default}  # {comment}"
            )

        return "\n".join(lines)

    # ------------------------------
    # 生成component代码
    # ------------------------------

    def generate_component(self, component):

        name = component["name"]
        fields = component.get("fields", [])
        doc = component.get("doc", "ECS Component")

        field_code = self._build_fields(fields)

        code = f'''"""
Auto generated ECS component
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from dataclasses import dataclass

from core.component import Component

@dataclass
class {name}(Component):
    """{doc}"""

{field_code}
'''

        return code

    # ------------------------------
    # 写入文件
    # ------------------------------

    def write_file(self, component):

        code = self.generate_component(component)

        file_name = self._camel_to_snake(component["name"]) + ".py"

        path = os.path.join(self.output_dir, file_name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        return path

    # ------------------------------
    # 批量生成
    # ------------------------------

    def batch_generate(self, components):

        paths = []

        for comp in components:

            path = self.write_file(comp)
            paths.append(path)

        return paths


# ==============================
# 示例
# ==============================

if __name__ == "__main__":

    generator = ComponentGenerator(output_dir=".")

    components = [

        {
            "name": "MaterialComponent",
            "doc": "材料属性组件",
            "fields": [
                ("hardness", "float", 0.0, "材料硬度"),
                ("toughness", "float", 0.0, "韧性"),
                ("density", "float", 0.0, "密度")
            ]
        },

        {
            "name": "GeometryComponent",
            "doc": "几何属性组件",
            "fields": [
                ("length", "float", 0.0, "长度"),
                ("thickness", "float", 0.0, "厚度"),
                ("weight", "float", 0.0, "重量")
            ]
        },

        {
            "name": "AttributeModifierComponent",
            "doc": "属性修正组件",
            "fields": [
                ("attack", "float", 0.0, "攻击力"),
                ("crit", "float", 0.0, "暴击率"),
                ("speed", "float", 0.0, "攻击速度")
            ]
        }

    ]

    paths = generator.batch_generate(components)

    print("生成完成:")
    for p in paths:
        print(p)
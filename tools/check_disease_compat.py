#!/usr/bin/env python
import sys
sys.path.insert(0, r'D:\个人助手\workspace\ECS')

from biology.components.disease_component import DiseaseComponent, DiseaseType
from human.components.health.disease_component_v4 import DiseaseManagerComponent

# 测试1: 旧版组件现在指向新版
assert DiseaseComponent is DiseaseManagerComponent
print("DiseaseComponent 别名正确")

# 测试2: 默认构造
dc = DiseaseComponent()
assert dc.disease_name == "unknown"
assert dc.infection_type == "bacterial"
assert dc.severity == 0.0
assert dc.contagiousness == 0.0
assert dc.stage == "incubation"
assert dc.symptoms == []
assert dc.duration == 0
assert dc.max_duration == 100
assert dc.is_terminal is False
print("默认 v2 字段正确")

# 测试3: 写 v2 字段并反映到底层疾病结构
dc.disease_name = "流感"
dc.infection_type = "viral"
dc.severity = 0.6
dc.contagiousness = 0.7
dc.stage = "active"
dc.symptoms = ["发烧", "咳嗽"]
dc.duration = 5
dc.max_duration = 50

assert dc.disease_name == "流感"
assert dc.infection_type == "viral"
assert 0.5 < dc.severity < 0.8
assert dc.contagiousness == 0.7
assert dc.stage == "active"
assert dc.symptoms == ["发烧", "咳嗽"]
assert dc.duration == 5
assert dc.max_duration == 50

# is_terminal 会提升 severity 到 CRITICAL
dc.is_terminal = True
assert dc.is_terminal is True
assert len(dc.current_diseases) == 1
print("v2 字段写入/读取正确")

# 测试4: DiseaseType 可用
assert DiseaseType.FLU.value == "flu"
print("DiseaseType 兼容枚举正确")

print("\n所有 DiseaseManagerComponent v2 兼容层检查通过")
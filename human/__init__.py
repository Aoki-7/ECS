#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:
@时间:2026/03/13 11:07:49
@作者:Sherry
@版本:1.0
'''

# Entity: Human_001
#  ├── SpaceComponent
#  ├── IdentityComponent
#  ├── BodyComponent
#  ├── NeedsComponent
#  ├── HealthComponent
#  ├── InventoryComponent
#  ├── ActionComponent
#  ├── BrainComponent
#  ├── SocialComponent
#  └── VelocityComponent

# Systems
#  ├── DecitionSystem 根据需求生成行为
#  ├── MovementSystem 移动系统
#  ├── NeedsSystem 随着时间推移更新生理需求 包括饥饿、口渴等
#  ├── NeedsComponent
"""
human/systems/identity 子模块

依赖:
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
身份系统包 — 人类身份的管理与演化

包含：
    - IdentitySystem : 身份合法性检查（阵营一致性、角色冲突检测）
    - AgeSystem      : 年龄增长与人生阶段切换（童年→青少年→成年→老年）
    - NamingSystem   : 命名规则（文化预设姓名的生成与更新）

与 identity/ 模块的关系：
    - identity/ 提供身份数据组件（BiologyComponent, SocialComponent）
    - human/systems/identity/ 提供身份逻辑处理
"""


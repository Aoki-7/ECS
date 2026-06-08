# memory/ 目录说明

> **注意：此目录为旧记忆系统的笔记存档，非活跃代码。**

## 状态

- **旧记忆系统**: 已迁移至 `memory_layer/`
- **此目录**: 仅保留历史笔记（`2026-05-17.md`）
- **活跃代码**: 请使用 `memory_layer/` 模块

## 迁移说明

| 旧系统 | 新系统 |
|--------|--------|
| `memory/`（笔记/草稿） | `memory_layer/`（完整实现） |
| 无代码实现 | 15 个 Python 文件 |
| 无测试 | 53 个测试 |

## 新系统位置

```
memory_layer/
├── memory_layer.py          # 全局管理器
├── concept.py               # 客观记忆
├── memory_instance.py       # 主观记忆
├── sensory_description.py   # 结构化感官
├── emotional_tag.py         # 情感标签
├── contact_record.py        # 接触记录
├── association_link.py      # 联想链接
├── cognitive_framework.py   # 认知框架
├── memory_distortion.py     # 扭曲引擎
├── memory_registration_system.py  # 自动注册
├── memory_persistence.py    # 持久化
└── tests/                   # 53 个测试
```

## 清理计划

- [x] 确认 `memory/` 无活跃代码
- [ ] 未来可考虑删除此目录（保留笔记到 `doc/`）

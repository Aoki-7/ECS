# ECS World Simulation - Web 开发套件

基于 FastAPI + Vite/React + SQLite 的 ECS 世界模拟系统 Web 开发套件。

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端 | FastAPI | 0.100+ |
| 前端 | Vite + React + TypeScript | 18+ |
| 数据库 | SQLite | 3.35+ |
| 实时通信 | WebSocket | — |

## 快速启动

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./start.sh
```

### 手动启动
```bash
# 后端
cd D:\个人助手\workspace\ECS
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd D:\个人助手\workspace\ECS\frontend
npm install
npm run dev
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

## API 路由

### World
- `GET /world/stats` - World 统计信息
- `GET /world/query` - 组件查询
- `GET /world/archetypes` - Archetype 信息
- `GET /world/entities` - 实体列表

### Entity
- `GET /entity/{id}` - 实体详情
- `GET /entity/{id}/components` - 实体组件
- `POST /entity/` - 创建实体
- `PUT /entity/{id}` - 更新实体
- `DELETE /entity/{id}` - 删除实体

### System
- `POST /system/run` - 运行模拟
- `POST /system/pause` - 暂停模拟
- `POST /system/resume` - 恢复模拟
- `POST /system/step` - 单步执行
- `GET /system/status` - 系统状态
- `GET /system/list` - 系统列表

### Snapshot
- `POST /snapshot/save` - 保存快照
- `POST /snapshot/load/{id}` - 加载快照
- `GET /snapshot/list` - 快照列表
- `DELETE /snapshot/{id}` - 删除快照

### History
- `GET /history/` - 历史记录
- `GET /history/timeline` - 时间轴
- `GET /history/events` - 事件列表

### WebSocket
- `WS /ws/events` - 实时事件流

## 架构

```
ECS/
├── api/              # FastAPI 后端
│   ├── main.py       # 入口
│   ├── dependencies.py # 依赖注入
│   ├── routers/      # API 路由
│   ├── schemas/      # Pydantic 模型
│   └── websocket/    # WebSocket
├── frontend/         # Vite/React 前端
│   ├── src/
│   │   ├── components/ # 共享组件
│   │   ├── pages/      # 页面
│   │   ├── services/   # API 客户端
│   │   ├── hooks/      # React Hooks
│   │   ├── store/      # 状态管理
│   │   └── types/      # TypeScript 类型
│   └── package.json
├── db/               # SQLite 数据库
│   ├── config.py     # 连接管理
│   ├── models/       # 数据模型
│   ├── repositories/ # 数据访问
│   └── services/     # 业务逻辑
└── start.bat         # 一键启动
```

## 性能优化

- **后端**: GZip 压缩、统计缓存、分页查询
- **前端**: 请求缓存、WebSocket 心跳、增量更新
- **数据库**: 索引优化、批量插入

## 测试

```bash
# 全量测试
pytest -x -q

# API 测试
pytest tests/api/ -v

# 数据库测试
pytest tests/db/ -v

# 性能测试
pytest tests/api/test_performance.py -v
```

## 版本

v4.0.0 - 2026-06-13

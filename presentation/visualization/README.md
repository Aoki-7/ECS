# ECS 世界模拟实时可视化

## 架构

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   浏览器前端     │ ◄────────────────► │  Python 后端     │
│  (HTML/Canvas)  │   JSON 数据推送    │   (ECS World)   │
└─────────────────┘                    └─────────────────┘
```

## 启动步骤

### 1. 启动后端服务器

```bash
cd presentation/visualization
python world_server.py
```

服务器启动后会：
- 创建 ECS 世界（植物/动物/人类/建筑/农田/土壤）
- 运行模拟循环（10 ticks/秒）
- 监听 WebSocket 连接 `ws://localhost:8765`

### 2. 打开前端仪表盘

用浏览器打开 `world_realtime_dashboard.html`

或者使用 Python 简易 HTTP 服务器：

```bash
cd presentation/visualization
python -m http.server 8080
```

然后访问 `http://localhost:8080/world_realtime_dashboard.html`

## 数据流

```
Tick 0: 后端计算 → 收集状态 → JSON序列化 → WebSocket推送 → 前端更新
Tick 1: 后端计算 → 收集状态 → JSON序列化 → WebSocket推送 → 前端更新
Tick 2: 后端计算 → 收集状态 → JSON序列化 → WebSocket推送 → 前端更新
...
```

## 通信协议

### 后端 → 前端 (每 tick 推送)

```json
{
  "tick": 100,
  "timestamp": 1717900000,
  "statistics": {
    "total_entities": 97,
    "humans": 12,
    "animals": 15,
    "plants": 33,
    "buildings": 7,
    "farms": 10,
    "soil_patches": 15
  },
  "entities": [
    {"id": 1, "type": "human", "x": 50.5, "y": 30.2},
    {"id": 2, "type": "plant", "x": 120.0, "y": 80.5}
  ],
  "environment": {
    "temperature": 22.5,
    "humidity": 0.5,
    "rainfall": 0.0,
    "wind_speed": 1.0
  },
  "knowledge": {
    "crafting": 150,
    "farming": 30,
    "technologies": 5
  },
  "systems": [
    {"name": "CollisionSystem", "enabled": true}
  ],
  "history": [
    {"tick": 0, "humans": 10, "animals": 15, "plants": 30, "buildings": 3, "farms": 8}
  ]
}
```

### 前端 → 后端 (控制命令)

```json
// 暂停
{"command": "pause"}

// 继续
{"command": "resume"}

// 调整速度
{"command": "speed", "interval": 0.05}
```

## 文件说明

| 文件 | 职责 |
|------|------|
| `world_server.py` | WebSocket 服务器 + ECS 世界模拟 |
| `world_realtime_dashboard.html` | 实时可视化前端 |
| `world_simulation_dashboard.py` | 静态数据导出（备用） |
| `world_simulation_dashboard.html` | 静态可视化（备用） |
| `civilization_dashboard.py` | 文明演化静态导出 |
| `civilization_dashboard.html` | 文明演化静态可视化 |

## 技术栈

- **后端**: Python + asyncio + websockets + ECS 框架
- **前端**: HTML5 + Canvas + Chart.js + Tailwind CSS
- **通信**: WebSocket (JSON)
- **无构建工具**: 直接运行，无需 npm/webpack

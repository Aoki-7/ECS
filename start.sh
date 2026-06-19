#!/bin/bash
# ECS World Simulation 一键启动脚本 (Linux/Mac)
# 同时启动后端 FastAPI 和前端 Vite

set -e

ECS_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ECS_ROOT"

# 清理可能遗留的旧 PID 文件
rm -f .ecs_backend.pid .ecs_frontend.pid

echo "=========================================="
echo "   ECS World Simulation 一键启动"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python3 未安装"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] Node.js 未安装"
    exit 1
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "[错误] npm 未安装"
    exit 1
fi

echo "[检查] Python: $(python3 --version)"
echo "[检查] Node.js: $(node --version)"
echo "[检查] npm: $(npm --version)"
echo ""

echo "[1/4] 初始化数据库..."
python3 -c "from db.config import init_db; init_db()"
echo "[完成] 数据库初始化完成"
echo ""

# 检查前端依赖
echo "[2/4] 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "[信息] 首次运行，安装前端依赖..."
    cd frontend
    npm install
    cd ..
else
    echo "[完成] 前端依赖已安装"
fi
echo ""

# 启动后端
echo "[3/4] 启动后端 FastAPI (端口 8000)..."
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "$BACKEND_PID" > .ecs_backend.pid
echo "[完成] 后端已启动 (PID: $BACKEND_PID)"
echo ""

# 等待后端启动
echo "[等待] 等待后端就绪..."
sleep 3
echo "[完成] 后端就绪"
echo ""

# 启动前端
echo "[4/4] 启动前端 Vite (端口 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$ECS_ROOT/.ecs_frontend.pid"
cd ..
echo "[完成] 前端已启动 (PID: $FRONTEND_PID)"
echo ""

echo "=========================================="
echo "   ECS World Simulation 启动完成!"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 前端: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 关闭所有服务..."

# 关闭指定 PID 的进程及其子进程
kill_tree() {
    local root_pid=$1
    local all_pids=()

    collect_children() {
        local pid=$1
        local children=""
        if command -v pgrep &> /dev/null; then
            children=$(pgrep -P "$pid" 2>/dev/null || true)
        else
            children=$(ps -o pid= -o ppid= -e 2>/dev/null | awk -v p="$pid" '$2 == p { print $1 }' || true)
        fi
        echo "$children"
    }

    collect() {
        local pid=$1
        all_pids+=("$pid")
        local children
        children=$(collect_children "$pid")
        for child in $children; do
            collect "$child"
        done
    }

    collect "$root_pid"

    # 先尝试优雅终止
    for pid in "${all_pids[@]}"; do
        kill -TERM "$pid" 2>/dev/null || true
    done
    sleep 1
    # 强制清理残留进程
    for pid in "${all_pids[@]}"; do
        kill -KILL "$pid" 2>/dev/null || true
    done
}

stop_service() {
    local pidfile=$1
    local name=$2
    if [ ! -f "$pidfile" ]; then
        return 0
    fi
    local pid
    pid=$(cat "$pidfile" | tr -d ' \t\n\r')
    rm -f "$pidfile"
    if [ -z "$pid" ]; then
        return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "[信息] $name (PID: $pid) 已不在运行"
        return 0
    fi
    echo "[关闭] 正在停止 $name (PID: $pid)..."
    kill_tree "$pid"
    echo "[完成] $name 已停止"
}

cleanup() {
    echo ""
    echo "[关闭] 正在关闭服务..."
    stop_service ".ecs_backend.pid" "后端"
    stop_service ".ecs_frontend.pid" "前端"
    echo "[完成] 服务已关闭"
    exit 0
}

trap cleanup INT TERM EXIT

# 等待
wait

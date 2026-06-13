#!/bin/bash
# ECS World Simulation 停止脚本 (Linux/Mac)
# 只停止由 start.sh 启动的后端/前端实例，避免误杀其他进程

set -e

ECS_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ECS_ROOT"

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

# 读取 PID 文件并安全停止
stop_by_pidfile() {
    local pidfile=$1
    local name=$2
    local marker=$3

    if [ ! -f "$pidfile" ]; then
        echo "[信息] 未找到 $name PID 文件 ($pidfile)，跳过"
        return 0
    fi

    local pid
    pid=$(cat "$pidfile" | tr -d ' \t\n\r')
    rm -f "$pidfile"

    if [ -z "$pid" ]; then
        echo "[信息] $name PID 文件为空"
        return 0
    fi

    if ! kill -0 "$pid" 2>/dev/null; then
        echo "[信息] $name (PID: $pid) 未运行"
        return 0
    fi

    # 校验命令行，避免 PID 被复用后误杀
    local cmdline=""
    if command -v ps &> /dev/null && ps -p "$pid" -o args= &> /dev/null; then
        cmdline=$(ps -p "$pid" -o args= 2>/dev/null || true)
    elif [ -r "/proc/$pid/cmdline" ]; then
        cmdline=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)
    fi

    if [ -n "$cmdline" ] && [[ "$cmdline" != *"$marker"* ]]; then
        echo "[警告] $name PID 文件中的进程 ($pid) 命令行不匹配，为避免误杀跳过"
        return 0
    fi

    echo "[停止] 正在停止 $name (PID: $pid)..."
    kill_tree "$pid"
    echo "[完成] $name 已停止"
}

echo "=========================================="
echo "   ECS World Simulation 停止"
echo "=========================================="
echo ""

stop_by_pidfile ".ecs_backend.pid" "后端" "uvicorn"
stop_by_pidfile ".ecs_frontend.pid" "前端" "npm run dev"

echo ""
echo "=========================================="
echo "   ECS World Simulation 已停止"
echo "=========================================="

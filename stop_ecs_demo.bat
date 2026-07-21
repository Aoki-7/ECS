@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

set SILENT=%1
if not "%SILENT%"=="silent" (
    echo ==============================================
    echo 🛑 ECS世界模拟Demo一键停止脚本
    echo ==============================================
)

cd /d "D:\个人助手\workspace\ECS"

:: 停止后端进程
if exist tmp_backend.pid (
    set /p BACKEND_PID=<tmp_backend.pid
    if not "%SILENT%"=="silent" echo 正在停止后端服务，PID: !BACKEND_PID!
    taskkill /F /PID !BACKEND_PID! > nul 2>&1
    del /f /q tmp_backend.pid > nul 2>&1
    if not "%SILENT%"=="silent" echo ✅ 后端服务已停止
) else (
    if not "%SILENT%"=="silent" echo 未找到后端PID文件，尝试强制清理相关Python进程
    taskkill /F /IM python.exe /FI "COMMANDLINE eq %*demo_server.py%" > nul 2>&1
)

:: 停止前端进程
if exist tmp_frontend.pid (
    set /p FRONTEND_PID=<tmp_frontend.pid
    if not "%SILENT%"=="silent" echo 正在停止前端服务，PID: !FRONTEND_PID!
    taskkill /F /PID !FRONTEND_PID! > nul 2>&1
    del /f /q tmp_frontend.pid > nul 2>&1
    if not "%SILENT%"=="silent" echo ✅ 前端服务已停止
) else (
    if not "%SILENT%"=="silent" echo 未找到前端PID文件，尝试强制清理相关Node进程
    taskkill /F /IM node.exe /FI "COMMANDLINE eq %*vite%" > nul 2>&1
)

:: 清理残留临时文件
del /f /q tmp*.pid > nul 2>&1

if not "%SILENT%"=="silent" (
    echo.
    echo ==============================================
    echo ✅ 所有服务已停止，资源已清理
    echo ==============================================
    pause > nul
)

@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ==============================================
echo 🚀 ECS世界模拟Demo一键启动脚本
echo ==============================================

cd /d "D:\个人助手\workspace\ECS"

:: 确保日志目录存在
if not exist logs mkdir logs

:: 先停止可能残留的进程
call stop_ecs_demo.bat silent > nul 2>&1

:: 启动后端服务
echo [1/2] 正在启动后端服务 (端口8000)...
start /B python presentation/visualization/demo_server.py > logs/demo_server_runtime.log 2>&1
timeout /t 4 /nobreak > nul

:: 获取后端PID
for /f "tokens=2 delims==" %%a in ('wmic process where "name='python.exe' and commandline like '%%demo_server.py%%'" get processid /value 2^>nul') do (
    set BACKEND_PID=%%a
    echo !BACKEND_PID! > tmp_backend.pid
    echo ✅ 后端启动成功，PID: !BACKEND_PID!
)

if not exist tmp_backend.pid (
    echo ❌ 后端启动失败，请检查 logs/demo_server_runtime.log
    pause
    exit /b 1
)

:: 启动前端服务
echo [2/2] 正在启动前端服务 (端口3000)...
cd frontend
start /B npm run dev > ../logs/demo_frontend_runtime.log 2>&1
timeout /t 6 /nobreak > nul

:: 获取前端PID
for /f "tokens=2 delims==" %%a in ('wmic process where "name='node.exe' and commandline like '%%vite%%'" get processid /value 2^>nul') do (
    set FRONTEND_PID=%%a
    echo !FRONTEND_PID! > ../tmp_frontend.pid
    echo ✅ 前端启动成功，PID: !FRONTEND_PID!
)

if not exist ../tmp_frontend.pid (
    echo ❌ 前端启动失败，请检查 logs/demo_frontend_runtime.log
    taskkill /F /PID !BACKEND_PID! > nul 2>&1
    del ../tmp_backend.pid
    pause
    exit /b 1
)

echo.
echo ==============================================
echo 🎉 所有服务启动完成！
echo 🌐 访问地址：http://localhost:3000
echo 📝 运行日志：logs/ 目录下
echo 🛑 停止服务：双击运行 stop_ecs_demo.bat
echo ==============================================
echo 按任意键关闭此窗口，服务将继续后台运行...
pause > nul

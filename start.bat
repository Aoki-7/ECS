@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM ECS World Simulation One-click Startup
REM Start backend FastAPI and frontend Vite

echo ==========================================
echo    ECS World Simulation Startup
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)

REM Check npm
call npm --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm not found
    pause
    exit /b 1
)

echo [OK] Python: 
python --version
echo [OK] Node.js: 
node --version
echo [OK] npm: 
call npm --version
echo.

REM Set project path
set "ECS_ROOT=%~dp0"
cd /d "%ECS_ROOT%"

REM Clean up any stale PID files from previous runs
if exist ".ecs_backend.pid" del ".ecs_backend.pid" >nul 2>&1
if exist ".ecs_frontend.pid" del ".ecs_frontend.pid" >nul 2>&1

echo [1/4] Initializing database...
python -c "from db.config import init_db; init_db()"
if errorlevel 1 (
    echo [ERROR] Database initialization failed
    pause
    exit /b 1
)
echo [OK] Database initialized
echo.

REM Check frontend dependencies
echo [2/4] Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo [INFO] First run, installing frontend dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] Frontend dependency installation failed
        pause
        exit /b 1
    )
    cd ..
) else (
    echo [OK] Frontend dependencies installed
)
echo.

REM Start backend - use cmd /c start to avoid PowerShell alias conflict
echo [3/4] Starting backend FastAPI (port 8000)...
cmd /c start "ECS_Backend" cmd /k "cd /d "%ECS_ROOT%" && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
if errorlevel 1 (
    echo [ERROR] Backend startup failed
    pause
    exit /b 1
)
echo [OK] Backend started
echo.

REM Wait for backend window to be ready, then capture its PID
echo [WAIT] Waiting for backend...
ping -n 4 127.0.0.1 >nul
call :capture_pid "ECS_Backend" ".ecs_backend.pid" "uvicorn"
echo [OK] Backend ready
echo.

REM Start frontend - use cmd /c start to avoid PowerShell alias conflict
echo [4/4] Starting frontend Vite (port 3000)...
cmd /c start "ECS_Frontend" cmd /k "cd /d "%ECS_ROOT%\frontend" && npm run dev"
if errorlevel 1 (
    echo [ERROR] Frontend startup failed
    pause
    exit /b 1
)
echo [OK] Frontend started
echo.

REM Wait for frontend window to be ready, then capture its PID
ping -n 3 127.0.0.1 >nul
call :capture_pid "ECS_Frontend" ".ecs_frontend.pid" "npm run dev"
echo.

echo ==========================================
echo    ECS World Simulation Started!
echo ==========================================
echo.
echo Access:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services...
pause >nul

REM Stop services by recorded PID (targeted), fallback to window title if needed
call :stop_by_pidfile ".ecs_backend.pid" "Backend" "ECS_Backend"
call :stop_by_pidfile ".ecs_frontend.pid" "Frontend" "ECS_Frontend"

REM Fallback: close any remaining console windows created by this script
cmd /c taskkill /FI "WINDOWTITLE eq ECS_Backend" /F >nul 2>&1
cmd /c taskkill /FI "WINDOWTITLE eq ECS_Frontend" /F >nul 2>&1

echo.
echo [OK] All services stopped
pause
endlocal
goto :eof

REM --- Subroutines ---

:capture_pid
set "TITLE=%~1"
set "PIDFILE=%~2"
set "MARKER=%~3"
set "CAPTURED_PID="
for /f "usebackq delims=" %%i in (`powershell -Command "Get-WmiObject Win32_Process | Where-Object CommandLine -like '*%ECS_ROOT%*%MARKER%*' | Select-Object -First 1 -ExpandProperty ProcessId"`) do (
    set "CAPTURED_PID=%%i"
)
if defined CAPTURED_PID (
    > "%PIDFILE%" echo !CAPTURED_PID!
    echo [OK] %TITLE% PID recorded: !CAPTURED_PID!
) else (
    echo [WARN] Could not record %TITLE% PID
)
goto :eof

:stop_by_pidfile
set "PIDFILE=%~1"
set "NAME=%~2"
set "WINTITLE=%~3"

if not exist "%PIDFILE%" goto :stop_by_pidfile_fallback

set "PID="
for /f "usebackq delims=" %%i in ("%PIDFILE%") do set "PID=%%i"
if not defined PID (
    del "%PIDFILE%" >nul 2>&1
    goto :stop_by_pidfile_fallback
)

tasklist /FI "PID eq %PID%" /NH /FO CSV 2>nul | findstr /I /C:"%PID%" >nul
if errorlevel 1 (
    echo [INFO] %NAME% [PID %PID%] is not running
    del "%PIDFILE%" >nul 2>&1
    goto :stop_by_pidfile_fallback
)

echo [STOP] Stopping %NAME% [PID %PID%]...
taskkill /PID %PID% /T /F >nul 2>&1
if errorlevel 1 (
    echo [WARN] Failed to stop %NAME% [PID %PID%]
) else (
    echo [OK] %NAME% stopped [PID %PID%]
)
del "%PIDFILE%" >nul 2>&1
goto :eof

:stop_by_pidfile_fallback
echo [INFO] %NAME% PID file not found, trying window title fallback...
cmd /c taskkill /FI "WINDOWTITLE eq %WINTITLE%" /T /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] %NAME% is not running
) else (
    echo [OK] %NAME% stopped via window title
)
goto :eof

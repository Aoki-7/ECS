@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM ECS World Simulation Stop Script
REM Stop only the backend/frontend instances started by start.bat

echo ==========================================
echo    ECS World Simulation Stop
echo ==========================================
echo.

REM Set project path
set "ECS_ROOT=%~dp0"
cd /d "%ECS_ROOT%"

REM Stop by recorded PID first (targeted), fallback to window title if no PID file
call :stop_by_pidfile ".ecs_backend.pid" "Backend" "ECS_Backend"
call :stop_by_pidfile ".ecs_frontend.pid" "Frontend" "ECS_Frontend"

echo.
echo ==========================================
echo    ECS World Simulation Stopped
echo ==========================================
echo.
pause
endlocal
goto :eof

REM --- Subroutines ---

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

tasklist /FI "PID eq !PID!" /NH /FO CSV 2>nul | findstr /I /C:"!PID!" >nul
if errorlevel 1 (
    echo [INFO] %NAME% [PID !PID!] is not running
    del "%PIDFILE%" >nul 2>&1
    goto :stop_by_pidfile_fallback
)

echo [STOP] Stopping %NAME% [PID !PID!]...
taskkill /PID !PID! /T /F >nul 2>&1
if errorlevel 1 (
    echo [WARN] Failed to stop %NAME% [PID !PID!]
) else (
    echo [OK] %NAME% stopped [PID !PID!]
)
del "%PIDFILE%" >nul 2>&1
goto :eof

:stop_by_pidfile_fallback
REM Fallback: stop by the unique window title created by start.bat
echo [INFO] %NAME% PID file not found, trying window title fallback...
taskkill /FI "WINDOWTITLE eq %WINTITLE%" /T /F >nul 2>&1
if errorlevel 1 (
    echo [INFO] %NAME% is not running
) else (
    echo [OK] %NAME% stopped via window title
)
goto :eof

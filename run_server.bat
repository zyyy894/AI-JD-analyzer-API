@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv was not found.
    echo Create it with: py -3.10 -m venv .venv
    exit /b 1
)

".venv\Scripts\python.exe" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] .venv is invalid or points to a missing Python installation.
    echo Recreate it with: py -3.10 -m venv .venv
    exit /b 1
)

if not exist ".env" (
    echo [ERROR] .env was not found in the project root.
    echo Copy .env.example to .env and fill in the model configuration.
    exit /b 1
)

".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8001

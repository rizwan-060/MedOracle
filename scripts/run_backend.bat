@echo off
setlocal
echo ==================================================
echo   Starting MedOracle Backend Server (FastAPI)
echo ==================================================

cd /d "%~dp0..\backend"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at backend\.venv
    echo Please ensure the virtual environment is set up.
    exit /b 1
)

echo Working directory: %CD%
echo Using Python: .venv\Scripts\python.exe
echo Starting Uvicorn on http://127.0.0.1:8000 ...
echo Press Ctrl+C to stop.
echo.

.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

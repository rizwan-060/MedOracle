@echo off
setlocal
echo ==================================================
echo   Setting up MedOracle Backend Environment
echo ==================================================

cd /d "%~dp0..\backend"

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment at backend\.venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        exit /b 1
    )
)

echo [INFO] Installing / verifying dependencies from requirements.txt ...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    exit /b 1
)

echo.
echo ==================================================
echo   MedOracle backend setup completed successfully!
echo ==================================================

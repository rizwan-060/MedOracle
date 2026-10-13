@echo off
setlocal enabledelayedexpansion
echo ==================================================
echo   Verifying MedOracle Project Structure
echo ==================================================

cd /d "%~dp0.."

set ERRORS=0

for %%D in (backend backend\app backend\app\core backend\app\api backend\app\database backend\app\agents backend\app\clinical backend\app\graph backend\tests docs frontend) do (
    if not exist "%%D" (
        echo [MISSING DIR] %%D
        set /a ERRORS+=1
    ) else (
        echo [OK DIR] %%D
    )
)

for %%F in (backend\requirements.txt backend\.env.example backend\app\main.py backend\app\core\config.py IMPLEMENTATION_PLAN.md PROJECT_STATUS.md API_CONTRACT.md) do (
    if not exist "%%F" (
        echo [MISSING FILE] %%F
        set /a ERRORS+=1
    ) else (
        echo [OK FILE] %%F
    )
)

echo --------------------------------------------------
if !ERRORS! equ 0 (
    echo [SUCCESS] All verified directories and files are present!
) else (
    echo [WARNING] Encountered !ERRORS! missing items.
)

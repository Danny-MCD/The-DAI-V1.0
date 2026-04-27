@echo off
setlocal
echo ==========================================
echo    FOREX-V2AI: FINAL RECOVERY & SETUP
echo ==========================================

:: 1. Check Python
python --version | findstr "3.12" >nul
if %errorlevel% neq 0 (
    echo ERROR: Python 3.12 required.
    pause
    exit /b
)

:: 2. Cleanup Git Index (The "Nuke" Command)
echo [1/4] Forcing Git to forget tracked venv files...
git rm -r --cached venv/ >nul 2>&1
git rm -r --cached python/src/venv/ >nul 2>&1
git lfs install >nul 2>&1

:: 3. Create venv in the ROOT (Correct Position)
if not exist "venv" (
    echo [2/4] Creating Virtual Environment in ROOT...
    python -m venv venv
)

:: 4. Install
echo [3/4] Installing Libraries...
call .\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [4/4] Sync Complete!
echo ==========================================
echo TO PUSH CLEANLY:
echo 1. git add .
echo 2. git commit -m "Moved venv to root and fixed tracking"
echo 3. git push
echo ==========================================
pause
@echo off
setlocal
echo ==========================================
echo     FOREX-V2AI: HYBRID CONDA SETUP
echo ==========================================

:: 1. Cleanup Git Index (Keep your safety logic)
echo [1/4] Cleaning Git tracking...
git rm -r --cached venv/ >nul 2>&1
git lfs install >nul 2>&1

:: 2. Create Conda Environment with the CORRECT version
echo [2/4] Ensuring Python 3.12 Environment exists...
:: This creates the env if it doesn't exist, specifically with 3.12
call conda create -n forex_bot python=3.12 -y

:: 3. Activate and Install
echo [3/4] Installing Libraries into 'forex_bot'...
call conda activate forex_bot
python -m pip install --upgrade pip
:: This will look for your requirements.txt file
pip install -r requirements.txt

echo [4/4] Setup Complete!
echo ==========================================
echo TO START WORK:
echo 1. conda activate forex_bot
echo 2. python python/src/feature_factory.py
echo ==========================================
pause
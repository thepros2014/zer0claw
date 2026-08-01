@echo off
cd /d "%~dp0"
TITLE Kraken AI Margin Trading Engine
COLOR 0A
cls

echo =========================================================================
echo         KRAKEN AI MARGIN TRADING ENGINE - STANDALONE LAUNCHER
echo =========================================================================
echo.
echo [1/3] Auto-provisioning Python Virtual Environment and dependencies...
powershell -ExecutionPolicy Bypass -File .\install_kraken_ai.ps1

echo [2/3] Starting AI Trading Dashboard on port 8001...
cd trading-dashboard
start /b ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
cd ..

echo [3/3] Launching Kraken AI Margin Trading Engine...
cd kraken-bot
start /b ..\.venv\Scripts\python.exe bot.py
cd ..

timeout /t 3 >nul

if exist "config.json" (
    echo [INFO] Existing Setup Detected - Opening Trading Dashboard...
    start http://127.0.0.1:8001/dashboard
) else if exist "trading-dashboard\config.json" (
    echo [INFO] Existing Setup Detected - Opening Trading Dashboard...
    start http://127.0.0.1:8001/dashboard
) else (
    echo [INFO] First-Time Startup Detected - Opening Setup Wizard...
    start http://127.0.0.1:8001/setup
)

echo.
echo =========================================================================
echo  System is Live! AI Trading Engine ^& Dashboard Running.
echo  Dashboard URL: http://127.0.0.1:8001/dashboard
echo  Setup URL:     http://127.0.0.1:8001/setup
echo =========================================================================
echo.
echo Press any key to stop the AI Engine...
pause >nul

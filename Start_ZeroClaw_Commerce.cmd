@echo off
TITLE ZeroClaw Commerce Master Launcher
COLOR 0A
cls

echo =========================================================================
echo         ZEROCLAW COMMERCE MASTER ALL-IN-ONE LAUNCHER
echo =========================================================================
echo.
echo [1/3] Starting FastAPI Commerce Gateway on port 8000...
cd fastapi-gateway
start /b uvicorn app.main:app --host 127.0.0.1 --port 8000
cd ..

echo [2/3] Auto-provisioning Telegram, Discord, and WhatsApp bots...
powershell -ExecutionPolicy Bypass -File .\install_bots.ps1

echo [3/3] Launching Storefront Bots & Opening Setup Wizard...
cd telegram-bot
start /b python bot.py
cd ..

timeout /t 2 >nul
start http://127.0.0.1:8000/setup

echo.
echo =========================================================================
echo  System is Live! All Storefront Bots & Gateway Running.
echo  Dashboard URL: http://127.0.0.1:8000/dashboard
echo  Setup Wizard:  http://127.0.0.1:8000/setup
echo =========================================================================
echo.
echo Press any key to stop all ZeroClaw Commerce services...
pause >nul

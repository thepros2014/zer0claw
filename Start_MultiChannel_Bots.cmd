@echo off
TITLE ZeroClaw Commerce Multi-Channel Launcher
COLOR 0A
cls

echo =========================================================================
echo       ZEROCLAW COMMERCE MASTER MULTI-CHANNEL LAUNCHER
echo =========================================================================
echo.
echo [1/3] Starting FastAPI Commerce Gateway on port 8000...
cd fastapi-gateway
start /b uvicorn app.main:app --host 127.0.0.1 --port 8000
cd ..

echo [2/3] Auto-provisioning Telegram, Discord, and WhatsApp dependencies...
powershell -ExecutionPolicy Bypass -File .\install_bots.ps1

echo [3/3] Launching Telegram Storefront Bot...
cd telegram-bot
start /b python bot.py
cd ..

echo.
echo =========================================================================
echo  All Multi-Channel Services Live!
echo  Dashboard URL: http://127.0.0.1:8000/dashboard
echo  Active Channels: Telegram, Discord, WhatsApp
echo =========================================================================
echo.
echo Press any key to stop all ZeroClaw Commerce bots...
pause >nul

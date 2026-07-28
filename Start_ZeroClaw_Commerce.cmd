@echo off
TITLE ZeroClaw Commerce Launcher
COLOR 0A
cls

echo =========================================================================
echo               ZEROCLAW COMMERCE AUTOMAGIC LAUNCHER
echo =========================================================================
echo.
echo [1/2] Starting FastAPI Commerce Gateway on port 8000...
cd fastapi-gateway
start /b uvicorn app.main:app --host 127.0.0.1 --port 8000
cd ..

echo [2/2] Opening First-Time Setup Wizard in your default browser...
timeout /t 2 >nul
start http://127.0.0.1:8000/setup

echo.
echo =========================================================================
echo  System is running! Keep this window open while using ZeroClaw Commerce.
echo  Dashboard URL: http://127.0.0.1:8000/dashboard
echo  Setup URL:     http://127.0.0.1:8000/setup
echo =========================================================================
echo.
echo Press any key to stop ZeroClaw Commerce...
pause >nul

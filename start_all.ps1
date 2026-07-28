# ZeroClaw Commerce - All-In-One Master Startup Script (PowerShell)

Write-Host "🛡️ Starting ZeroClaw Commerce Master Stack..." -ForegroundColor Cyan

# 1. Start FastAPI Gateway
Write-Host "1️⃣ Starting FastAPI Gateway..." -ForegroundColor Yellow
Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "$PSScriptRoot\fastapi-gateway" -NoNewWindow

# 2. Provision Multi-Channel Bot Dependencies
Write-Host "2️⃣ Provisioning Telegram, Discord, and WhatsApp dependencies..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\install_bots.ps1"

# 3. Start Telegram Storefront Bot
Write-Host "3️⃣ Starting Telegram Storefront Bot..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\telegram-bot\bot.py") {
    Start-Process -FilePath "python" -ArgumentList "bot.py" -WorkingDirectory "$PSScriptRoot\telegram-bot" -NoNewWindow
}

# 4. Open Setup Wizard in Default Browser
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8000/setup"

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " 🎉 ZeroClaw Commerce Master Stack is Live!" -ForegroundColor Green
Write-Host " 🌐 Dashboard: http://127.0.0.1:8000/dashboard" -ForegroundColor Yellow
Write-Host " ⚙️ Setup:     http://127.0.0.1:8000/setup" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan

# ZeroClaw Commerce - Automated Multi-Channel Bot Installer (Windows PowerShell)

Write-Host "🤖 Starting ZeroClaw Commerce Automated Multi-Channel Bot Installer..." -ForegroundColor Cyan

# 1. Telegram Bot Dependencies
Write-Host "1️⃣ Installing Telegram Bot dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\telegram-bot") {
    pip install -r "$PSScriptRoot\telegram-bot\requirements.txt" --quiet
    if (-not (Test-Path "$PSScriptRoot\telegram-bot\.env")) {
        Set-Content -Path "$PSScriptRoot\telegram-bot\.env" -Value "TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN`nGATEWAY_URL=http://localhost:8000`nMERCHANT_WALLET=DestWallet11111111111111111111111111111111"
    }
    Write-Host "   ✅ Telegram Bot provisioned." -ForegroundColor Green
}

# 2. Discord Bot Dependencies
Write-Host "2️⃣ Installing Discord Bot dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\multi_channel_bots.md") {
    pip install discord.py httpx python-dotenv --quiet
    Write-Host "   ✅ Discord Bot dependencies provisioned." -ForegroundColor Green
}

# 3. WhatsApp Webhook Dependencies
Write-Host "3️⃣ Installing WhatsApp Webhook Gateway dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn httpx python-dotenv --quiet
Write-Host "   ✅ WhatsApp Webhook Gateway provisioned." -ForegroundColor Green

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " 🎉 Multi-Channel Bot Installation Complete!" -ForegroundColor Green
Write-Host " Launch all bots with: .\Start_MultiChannel_Bots.cmd" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan

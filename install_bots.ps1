# ZeroClaw Commerce - Automated Multi-Channel Bot Installer (Windows PowerShell)

Write-Host "🤖 Starting ZeroClaw Commerce Automated Multi-Channel Bot Installer..." -ForegroundColor Cyan

# Create venv if it doesn't exist
if (-not (Test-Path "$PSScriptRoot\.venv")) {
    Write-Host "Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv "$PSScriptRoot\.venv"
}

$pip = "$PSScriptRoot\.venv\Scripts\pip.exe"

# 1. FastAPI Gateway Dependencies
Write-Host "1️⃣ Installing FastAPI Gateway dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\fastapi-gateway") {
    & $pip install -r "$PSScriptRoot\fastapi-gateway\requirements.txt" --quiet
    Write-Host "   ✅ FastAPI Gateway provisioned." -ForegroundColor Green
}

# 2. Telegram Bot Dependencies
Write-Host "2️⃣ Installing Telegram Bot dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\telegram-bot") {
    & $pip install -r "$PSScriptRoot\telegram-bot\requirements.txt" --quiet
    if (-not (Test-Path "$PSScriptRoot\telegram-bot\.env")) {
        Set-Content -Path "$PSScriptRoot\telegram-bot\.env" -Value "TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN`nGATEWAY_URL=http://localhost:8000`nMERCHANT_WALLET=DestWallet11111111111111111111111111111111"
    }
    Write-Host "   ✅ Telegram Bot provisioned." -ForegroundColor Green
}

# 3. Discord Bot & WhatsApp Dependencies
Write-Host "3️⃣ Installing Discord & WhatsApp dependencies..." -ForegroundColor Yellow
& $pip install discord.py httpx python-dotenv fastapi uvicorn --quiet
Write-Host "   ✅ Discord & WhatsApp provisioned." -ForegroundColor Green

# 4. Kraken Bot dependencies
Write-Host "🐙 Installing Kraken Bot dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\kraken-bot") {
    & $pip install -r "$PSScriptRoot\kraken-bot\requirements.txt" --quiet
    Write-Host "   ✅ Kraken Bot provisioned." -ForegroundColor Green
}

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " 🎉 Multi-Channel Bot Installation Complete!" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Cyan


# Kraken AI Standalone - Automated Installer (Windows PowerShell)

Write-Host "🤖 Starting Kraken AI Setup..." -ForegroundColor Cyan

# Create venv if it doesn't exist
if (-not (Test-Path "$PSScriptRoot\.venv")) {
    Write-Host "Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv "$PSScriptRoot\.venv"
}

$pip = "$PSScriptRoot\.venv\Scripts\pip.exe"

# 1. Trading Dashboard Dependencies
Write-Host "1️⃣ Installing Trading Dashboard dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\trading-dashboard") {
    & $pip install -r "$PSScriptRoot\trading-dashboard\requirements.txt" --quiet
    Write-Host "   ✅ Trading Dashboard provisioned." -ForegroundColor Green
}

# 2. Kraken AI Bot Dependencies
Write-Host "🐙 Installing Kraken Bot dependencies..." -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\kraken-bot") {
    & $pip install -r "$PSScriptRoot\kraken-bot\requirements.txt" --quiet
    Write-Host "   ✅ Kraken Bot provisioned." -ForegroundColor Green
}

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host " 🎉 AI Bot Installation Complete!" -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Cyan

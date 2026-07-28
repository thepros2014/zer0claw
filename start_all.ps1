# ZeroClaw Commerce - Automagic One-Click Startup Script (Windows PowerShell)

Write-Host "🚀 Launching ZeroClaw Commerce System..." -ForegroundColor Cyan

# Step 1: Launch FastAPI Gateway in background job
Write-Host "1️⃣ Starting FastAPI Commerce Gateway on port 8000..." -ForegroundColor Yellow
$GatewayProcess = Start-Process -FilePath "uvicorn" -ArgumentList "app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "$PSScriptRoot\fastapi-gateway" -PassThru -NoNewWindow

# Step 2: Health Check Wait Loop (Wait until Gateway is ready)
$MaxRetries = 15
$Retries = 0
$GatewayReady = $false

Write-Host "⏳ Waiting for Gateway health check..." -ForegroundColor Yellow
while ($Retries -lt $MaxRetries -and -not $GatewayReady) {
    Start-Sleep -Seconds 1
    try {
        $Response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/docs" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($Response.StatusCode -eq 200) {
            $GatewayReady = $true
        }
    } catch {
        # Keep waiting
    }
    $Retries++
}

if ($GatewayReady) {
    Write-Host "✅ FastAPI Gateway is ONLINE at http://127.0.0.1:8000" -ForegroundColor Green
} else {
    Write-Host "⚠️ Gateway taking longer than expected to start, proceeding anyway..." -ForegroundColor Orange
}

# Step 3: Launch Telegram Bot
Write-Host "2️⃣ Starting Telegram Bot..." -ForegroundColor Cyan
if (Test-Path "$PSScriptRoot\telegram-bot\.env") {
    Set-Location "$PSScriptRoot\telegram-bot"
    python bot.py
} else {
    Write-Host "⚠️ Notice: telegram-bot\.env file missing. Please ensure TELEGRAM_BOT_TOKEN is configured." -ForegroundColor Red
    Set-Location "$PSScriptRoot\telegram-bot"
    python bot.py
}

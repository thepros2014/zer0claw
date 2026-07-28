#!/usr/bin/env bash
# ZeroClaw Commerce - Automagic One-Click Startup Script (Mac/Linux Bash)

echo "🚀 Launching ZeroClaw Commerce System..."

# Step 1: Launch FastAPI Gateway in background
echo "1️⃣ Starting FastAPI Commerce Gateway on port 8000..."
cd fastapi-gateway
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
GATEWAY_PID=$!
cd ..

# Step 2: Health Check Wait Loop
echo "⏳ Waiting for Gateway health check..."
for i in {1..15}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null; then
        echo "✅ FastAPI Gateway is ONLINE at http://127.0.0.1:8000"
        break
    fi
    sleep 1
done

# Step 3: Launch Telegram Bot
echo "2️⃣ Starting Telegram Bot..."
cd telegram-bot
python3 bot.py

# Cleanup Gateway on exit
kill $GATEWAY_PID

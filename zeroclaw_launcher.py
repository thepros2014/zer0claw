"""
ZeroClaw Commerce Unified Single-File Standalone Launcher.
Combines FastAPI Commerce Gateway, Telegram Cashier Bot, and Auto-Dashboard launch.
"""

import sys
import os
import time
import json
import asyncio
import threading
import webbrowser
from dotenv import load_dotenv

# Ensure root, gateway, and telegram bot directories are in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, 'frozen', False):
    # Running inside PyInstaller bundle
    BUNDLE_DIR = sys._MEIPASS
    sys.path.insert(0, os.path.join(BUNDLE_DIR, "fastapi-gateway"))
    sys.path.insert(0, os.path.join(BUNDLE_DIR, "telegram-bot"))
    sys.path.insert(0, BUNDLE_DIR)
else:
    sys.path.insert(0, os.path.join(BASE_DIR, "fastapi-gateway"))
    sys.path.insert(0, os.path.join(BASE_DIR, "telegram-bot"))
    sys.path.insert(0, BASE_DIR)

load_dotenv()


def run_gateway():
    """Runs the FastAPI Commerce Gateway server on port 8000."""
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


def run_telegram_bot():
    """Runs the Telegram cashier bot if token is configured."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        for cfg_path in ["config.json", os.path.join("fastapi-gateway", "config.json")]:
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        token = data.get("telegram_token")
                        if token and token != "YOUR_TELEGRAM_BOT_TOKEN":
                            os.environ["TELEGRAM_BOT_TOKEN"] = token
                            break
                except Exception:
                    pass

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token and token != "YOUR_TELEGRAM_BOT_TOKEN":
        print("🤖 [ZeroClaw] Starting Telegram Cashier Bot...")
        try:
            from bot import main as bot_main
            bot_main()
        except Exception as e:
            print(f"⚠️ [ZeroClaw] Telegram Bot error: {e}")
    else:
        print("ℹ️ [ZeroClaw] TELEGRAM_BOT_TOKEN not configured yet. Complete setup at http://127.0.0.1:8000/setup to enable Telegram cashier.")


def main():
    print("=" * 75)
    print("        ZEROCLAW COMMERCE SINGLE-FILE STANDALONE RUNTIME")
    print("=========================================================================")
    print("🚀 [1/3] Launching FastAPI Commerce Gateway (http://127.0.0.1:8000)...")

    gateway_thread = threading.Thread(target=run_gateway, daemon=True)
    gateway_thread.start()

    time.sleep(2)

    print("🤖 [2/3] Initializing Telegram Storefront Cashier...")
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    print("🌐 [3/3] Opening Merchant Dashboard / Setup Wizard...")
    has_config = os.path.exists("config.json") or os.path.exists(os.path.join("fastapi-gateway", "config.json"))
    target_url = "http://127.0.0.1:8000/dashboard" if has_config else "http://127.0.0.1:8000/setup"
    
    try:
        webbrowser.open(target_url)
    except Exception:
        pass

    print("\n" + "=" * 75)
    print(" System is Live!")
    print(f" Dashboard URL: {target_url}")
    print(" Press Ctrl+C to terminate ZeroClaw Commerce.")
    print("=" * 75 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ZeroClaw Commerce runtime...")
        sys.exit(0)


if __name__ == "__main__":
    main()

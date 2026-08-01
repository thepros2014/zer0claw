import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

def load_master_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

master_cfg = load_master_config()

# Kraken API Credentials
KRAKEN_API_KEY = master_cfg.get("kraken_api_key") or os.getenv("KRAKEN_API_KEY", "")
KRAKEN_API_SECRET = master_cfg.get("kraken_api_secret") or os.getenv("KRAKEN_API_SECRET", "")

# AI Margin Bot Settings
MAX_LEVERAGE = int(master_cfg.get("kraken_max_leverage", os.getenv("KRAKEN_MAX_LEVERAGE", "5")))
TARGET_PAIR = master_cfg.get("kraken_trading_pair", os.getenv("KRAKEN_TRADING_PAIR", "BTC/USD"))

TRADE_AMOUNT_USD = float(os.getenv("TRADE_AMOUNT_USD", "10.0")) # Dollar value per trade for testing

TIMEFRAME = "15m"
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300")) # 5 minutes

channels = master_cfg.get("channels", {})
KRAKEN_ENABLED = channels.get("kraken") == "configure" or (bool(KRAKEN_API_KEY) and bool(KRAKEN_API_SECRET))

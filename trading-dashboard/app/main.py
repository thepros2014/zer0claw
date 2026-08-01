import json
import logging
import time
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# Structured logging baseline
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kraken-ai-gateway")

app = FastAPI(
    title="Kraken AI Trading Gateway API",
    description="Dedicated dashboard API for managing the Kraken RL Trading Bot.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))
ROOT_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "config.json"))

def mask_secret(val: Any) -> str:
    if not val or not isinstance(val, str):
        return "[HIDDEN]"
    if len(val) <= 6:
        return "******"
    return f"{val[:3]}...{val[-3:]}"

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "kraken-ai-gateway",
        "timestamp": int(time.time()),
    }

@app.get("/", tags=["Dashboard"])
@app.get("/dashboard", tags=["Dashboard"])
async def serve_dashboard():
    static_html = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")
    if os.path.exists(static_html):
        return FileResponse(static_html)
    return {"message": "Kraken AI Gateway API v1.0.0"}

@app.get("/setup", tags=["Setup"])
async def serve_setup_wizard():
    static_setup = os.path.join(os.path.dirname(__file__), "static", "setup.html")
    if os.path.exists(static_setup):
        return FileResponse(static_setup)
    return {"message": "Setup Wizard unavailable"}

@app.get("/api/v1/setup/status", tags=["Setup"])
async def get_setup_status():
    for cfg in [CONFIG_FILE, ROOT_CONFIG_FILE]:
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {"setup_completed": data.get("setup_completed", True), "config": data}
            except Exception:
                pass
    return {"setup_completed": False}

@app.post("/api/v1/setup/save", tags=["Setup"])
async def save_setup(config: Dict[str, Any]):
    config["setup_completed"] = True
    config["updated_at"] = int(time.time())

    for cfg in [CONFIG_FILE, ROOT_CONFIG_FILE]:
        try:
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error({"event": "config_save_error", "file": cfg, "error": str(e)})

    sanitized_config = {
        k: (mask_secret(v) if any(s in k.lower() for s in ["token", "pin", "key", "secret"]) else v)
        for k, v in config.items()
    }
    logger.info({"event": "ai_setup_saved", "config": sanitized_config})
    return {"status": "success", "message": "Kraken AI configuration saved successfully!"}

@app.get("/api/v1/dashboard/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    # Placeholder for real trading stats from bot
    return {
        "status": "active",
        "learning_rate": "0.0003",
        "open_positions": 1,
        "total_trades": 12,
        "pnl_usd": 45.20
    }

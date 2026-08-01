import json
import logging
import time
from typing import Any, Dict
import re
import httpx

from fastapi import FastAPI
from pydantic import BaseModel
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
    state_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kraken-bot", "state.json"))
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading bot state: {e}")
            
    return {
        "status": "offline",
        "learning_rate": "-",
        "open_positions": 0,
        "total_trades": 0,
        "pnl_usd": 0.0,
        "signals": []
    }

class ChatMessage(BaseModel):
    message: str

@app.post("/api/v1/chat", tags=["Dashboard"])
async def handle_chat(payload: ChatMessage):
    msg = payload.message.lower().strip()
    
    state_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kraken-bot", "state.json"))
    bot_state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                bot_state = json.load(f)
        except Exception:
            pass

    # Attempt to use local Ollama if available
    ollama_url = "http://127.0.0.1:11434"
    try:
        async with httpx.AsyncClient() as client:
            tags_res = await client.get(f"{ollama_url}/api/tags", timeout=2.0)
            if tags_res.status_code == 200:
                models = tags_res.json().get("models", [])
                if models:
                    model_name = models[0]["name"]
                    context_str = f"Current Portfolio Value: ${bot_state.get('portfolio_value', 0):.2f}, Open Positions: {bot_state.get('open_positions', 0)}, Status: {bot_state.get('status', 'offline')}."
                    if bot_state.get("signals"):
                        recent = ", ".join([f"{s['action']} on {s['symbol']}" for s in bot_state["signals"]])
                        context_str += f" Recent Signals: {recent}."
                        
                    prompt = f"""You are the ZeroClaw Kraken AI Trading Assistant. Be concise (1-3 sentences max).
System context: {context_str}
If the user gives a command to control the bot (e.g. 'pause', 'resume', 'liquidate'/'sell all'), you MUST include a JSON block at the very end of your response exactly like this: [COMMAND: {{"intent": "pause"}}] or [COMMAND: {{"intent": "liquidate", "symbol": "ALL"}}].

User: {payload.message}
Assistant:"""
                    
                    chat_res = await client.post(f"{ollama_url}/api/generate", json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False
                    }, timeout=30.0)
                    
                    if chat_res.status_code == 200:
                        full_reply = chat_res.json().get("response", "...")
                        
                        # Intercept commands
                        cmd_match = re.search(r'\[COMMAND:\s*(\{.*?\})\s*\]', full_reply)
                        if cmd_match:
                            try:
                                cmd_json = json.loads(cmd_match.group(1))
                                cmds_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "kraken-bot", "commands.json"))
                                with open(cmds_file, "w") as cf:
                                    json.dump(cmd_json, cf)
                                full_reply = full_reply.replace(cmd_match.group(0), "").strip()
                            except Exception as e:
                                logger.error(f"Failed to parse command JSON: {e}")
                                
                        return {"reply": full_reply}
    except Exception as e:
        logger.warning(f"Ollama local LLM not reachable, falling back to basic rules: {e}")

    # Fallback basic rule-based logic
    response_text = "I am your Kraken AI Trading Assistant. Try asking me for 'status', 'portfolio', 'profit', or 'signals'."
    
    if "status" in msg or "running" in msg:
        status = bot_state.get("status", "offline")
        response_text = f"The trading engine is currently {status.upper()}."
    elif "portfolio" in msg or "value" in msg or "balance" in msg:
        val = bot_state.get("portfolio_value", 0.0)
        response_text = f"Your current estimated portfolio value is ${val:.2f}."
    elif "profit" in msg or "pnl" in msg:
        pnl = bot_state.get("pnl_usd", 0.0)
        response_text = f"Your estimated PnL since start is ${pnl:.2f}."
    elif "signal" in msg or "trades" in msg or "position" in msg:
        signals = bot_state.get("signals", [])
        if not signals:
            response_text = "No recent signals generated."
        else:
            recent = ", ".join([f"{s['action']} on {s['symbol']}" for s in signals])
            response_text = f"Recent AI signals: {recent}."
            
    return {"reply": response_text}


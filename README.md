# ZeroClaw Commerce 🛡️

![ZeroClaw Framework](https://img.shields.io/badge/Framework-ZeroClaw-blue)
![Solana](https://img.shields.io/badge/Blockchain-Solana-14F195?logo=solana&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-wasm32--wasip2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

Welcome to **ZeroClaw Commerce** — the zero-key payment, tax accounting, and digital fulfillment platform for the ZeroClaw agent ecosystem.

ZeroClaw Commerce provides `wasm32-wasip2` plugins, an async FastAPI Gateway, and multi-channel bots (Telegram, WhatsApp, Discord), turning standard agent bots into Tier-1 secure payment processors with dual-currency (BRL/USD) tax reporting and instant digital asset delivery.

---

## ⚡ Automagic One-Click Startup (No Manual Setup Required)

Launch the entire stack (FastAPI Gateway + Telegram Bot) with a single command:

### Windows:
```powershell
.\start_all.ps1
```

### Mac / Linux:
```bash
chmod +x start_all.sh
./start_all.sh
```

The script will automatically:
1. Start the **FastAPI Commerce Gateway** on `http://127.0.0.1:8000` in the background.
2. Poll the health-check endpoint until the gateway is 100% online.
3. Automatically launch the **Telegram Bot**!

---

## 🏆 The Superteam Submission
**Judges:** See [SUBMISSION.md](./SUBMISSION.md) for a technical breakdown of how this architecture meets the rubric requirements, including the **Brazil-First Flow** and resolving the **Blockhash Expiry** issue.

---

## 📦 Core Architecture
- `fastapi-gateway`: Async Python REST gateway with replay protection (`VERIFIED_SIGNATURES`), invoice expiration, and digital goods delivery.
- `telegram-bot`: Production-ready Telegram bot (`bot.py`) for merchant storefronts.
- `zeroclaw-solana`: WASM plugin providing live RPC token risk-checks and Solana Pay URI generation.
- `zeroclaw-accounting`: WASM plugin providing live USD/BRL fiat price fetching and CSV tax generation.
- `zeroclaw-memory`: A flat-file JSONL durable memory backend for WASM compatibility without C-toolchain dependencies.

---

## 🔒 Custody Tier: 1 (Proposer-Only)
This framework explicitly operates in **Tier 1**. The LLM and the server process hold **zero** private keys. The agent acts strictly as a transaction proposer, returning a Solana Pay URI for human authorization via Phantom, Solflare, or Ledger.

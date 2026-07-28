# ZeroClaw Commerce 🛡️

![ZeroClaw Framework](https://img.shields.io/badge/Framework-ZeroClaw-blue)
![Solana](https://img.shields.io/badge/Blockchain-Solana-14F195?logo=solana&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-wasm32--wasip2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

Welcome to **ZeroClaw Commerce** — the zero-key payment, tax accounting, and digital fulfillment platform for the ZeroClaw agent ecosystem.

ZeroClaw Commerce provides `wasm32-wasip2` plugins, an async FastAPI Gateway, and multi-channel bots (Telegram, WhatsApp, Discord), turning standard agent bots into Tier-1 secure payment processors with dual-currency (BRL/USD) tax reporting and instant digital asset delivery.

---

## 📚 Documentation Index (`docs/`)

| Document | Description |
| :--- | :--- |
| **[🏆 SUBMISSION.md](./docs/SUBMISSION.md)** | Official Superteam Bounty Submission Breakdown & Rubric Alignment. |
| **[🛡️ ARCHITECTURE.md](./docs/ARCHITECTURE.md)** | Technical Architecture, WASM Plugins, & 6-Layer Security Model. |
| **[🔮 VISION.md](./docs/VISION.md)** | Strategic Expansion Roadmap & Institutional Squads Multisig Bridge. |
| **[🤖 TELEGRAM_BOT.md](./docs/TELEGRAM_BOT.md)** | Telegram Storefront Bot Setup, Commands, & Multi-Wallet Specs. |
| **[🌐 MULTI_CHANNEL.md](./docs/MULTI_CHANNEL.md)** | Discord Slash Commands & WhatsApp Cloud API Webhook Guide. |

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

---

## 📦 Core Architecture
- `fastapi-gateway`: Async Python REST gateway with replay protection (`VERIFIED_SIGNATURES`), invoice expiration, and digital goods delivery.
- `telegram-bot`: Production-ready Telegram bot (`bot.py`) for merchant storefronts.
- `zeroclaw-solana`: WASM plugin providing live RPC token risk-checks and Solana Pay URI generation.
- `zeroclaw-accounting`: WASM plugin providing live USD/BRL fiat price fetching and CSV tax generation.
- `zeroclaw-memory`: A flat-file JSONL durable memory backend for WASM compatibility without C-toolchain dependencies.

---

## 🔒 Custody Tier: 1 (Proposer-Only)
This framework explicitly operates in **Tier 1**. The LLM and the server process hold **zero** private keys. The agent acts strictly as a transaction proposer, returning a Solana Pay URI for human authorization via Phantom, Solflare, Backpack, or Ledger.

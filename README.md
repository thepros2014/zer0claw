# ZeroClaw Commerce 🛡️

![ZeroClaw Framework](https://img.shields.io/badge/Framework-ZeroClaw-blue)
![Solana](https://img.shields.io/badge/Blockchain-Solana-14F195?logo=solana&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-wasm32--wasip2-orange)
![Release](https://img.shields.io/badge/Release-v1.1.0-green)
![License](https://img.shields.io/badge/License-MIT-green)

Welcome to **ZeroClaw Commerce** — the zero-key payment, tax accounting, and digital fulfillment platform for the ZeroClaw agent ecosystem.

ZeroClaw Commerce provides `wasm32-wasip2` plugins, an async FastAPI Gateway, multi-channel bots (Telegram, WhatsApp, Discord), double-clickable launchers, and a real-time **Merchant Sales & Security Dashboard** with 6-digit PIN protection.

---

## 📂 Repository Directory Structure

```text
zer0claw/
├── docs/                       <-- Consolidated Documentation
│   ├── SUBMISSION.md           <-- Official Superteam Bounty Submission
│   ├── ARCHITECTURE.md         <-- Technical Architecture & 6-Layer Security
│   ├── VISION.md               <-- Strategic Roadmap & Enterprise Vision
│   ├── TELEGRAM_BOT.md         <-- Telegram Storefront Setup & Commands
│   └── MULTI_CHANNEL.md        <-- Discord Slash Commands & WhatsApp Webhook
├── fastapi-gateway/            <-- Async REST Gateway (Replay Protection & Fulfillment)
│   ├── app/
│   │   ├── main.py             <-- FastAPI Endpoints & In-Memory Store
│   │   ├── models.py           <-- Pydantic V2 Schemas & Hashes
│   │   ├── solana.py           <-- Multi-RPC Solana Client & Reference Generator
│   │   └── static/
│   │       ├── index.html      <-- Merchant Dashboard (PIN Modal & Sales Stats)
│   │       └── setup.html      <-- First-Time Setup Wizard (Per-Channel Controls)
│   └── requirements.txt
├── telegram-bot/               <-- Telegram Storefront Bot Application
│   ├── bot.py                  <-- Async Bot, Multi-Wallet Deep Links & Catalog
│   └── requirements.txt
├── skills/                     <-- Official Zer0claw Skill Manifest
│   └── solana-commerce/
│       └── SKILL.md            <-- Skill Manifest & Standard Operating Procedure (SOP)
├── zeroclaw-solana/            <-- WASM Risk Engine & Solana Pay Crate (Rust)
├── zeroclaw-accounting/        <-- WASM Dual-Currency Tax Accounting Crate (Rust)
├── zeroclaw-memory/            <-- Flat-file Durable Memory Crate (Rust)
├── zeroclaw-api/               <-- Core Plugin WIT Interfaces (Rust)
├── mock-cli/                   <-- Interactive Developer Demo CLI (Rust)
├── Start_ZeroClaw_Commerce.cmd <-- Double-Click Launcher (Gateway + Browser Setup)
├── Start_MultiChannel_Bots.cmd <-- Double-Click Launcher (Gateway + All 3 Bots)
├── install_bots.ps1            <-- Automated Bot Dependency Installer (Windows)
├── install_bots.sh             <-- Automated Bot Dependency Installer (Mac/Linux)
└── README.md                   <-- Front Page Overview & Repository Sitemap
```

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

## ⚡ Double-Clickable Automagic Startup (Zero Technical Friction)

Simply **double-click** the launcher file in Windows File Explorer:

### 🖱️ Windows (Double-Click):
Double-click **`Start_ZeroClaw_Commerce.cmd`** in your root folder!

Alternatively for all 3 bots (Telegram, Discord, WhatsApp):
Double-click **`Start_MultiChannel_Bots.cmd`**!

### 💻 Mac / Linux:
```bash
chmod +x install_bots.sh start_all.sh
./start_all.sh
```

---

## 🔒 Custody Tier: 1 (Proposer-Only)
This framework explicitly operates in **Tier 1**. The LLM and the server process hold **zero** private keys. The agent acts strictly as a transaction proposer, returning a Solana Pay URI for human authorization via Phantom, Solflare, Backpack, or Ledger.

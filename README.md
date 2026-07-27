# Zero-Trust Solana Payment & Tax Terminal 🛡️

![ZeroClaw Framework](https://img.shields.io/badge/Framework-ZeroClaw-blue)
![Solana](https://img.shields.io/badge/Blockchain-Solana-14F195?logo=solana&logoColor=black)
![Architecture](https://img.shields.io/badge/Architecture-wasm32--wasip2-orange)
![License](https://img.shields.io/badge/License-MIT-green)

Welcome to the **Zero-Trust Solana Tax Accounting Payment Terminal**. This repository is a submission for the Superteam ZeroClaw Hackathon Bounty. 

It provides production-ready, `wasm32-wasip2` plugins for the ZeroClaw runtime, turning any WhatsApp, Telegram, or Terminal agent into a fully autonomous, hyper-secure payment processor with dual-currency (BRL/USD) IRS tax reporting.

## 🏆 The Superteam Submission 
**Judges:** Please read our official [SUBMISSION.md](./SUBMISSION.md) for the complete breakdown of how this architecture flawlessly addresses every single rubric requirement, including the **Brazil-First Flow** and **Blockhash Expiry Trap**.

---

## ⚡ What it Does
When a customer interacts with the merchant's ZeroClaw agent (e.g., via WhatsApp), the agent can generate Zero-Key Solana Transactions. Before any transaction is proposed, the WASM Risk Engine dynamically queries the Solana blockchain to assess the token for Mint/Freeze Authority risks. 

If it passes, the agent outputs a **Solana Pay URI** for the user to scan and approve with their Phantom mobile wallet (Tier 1 Proposer Custody - Zero Keys). Once settled, the plugin securely queries CoinGecko and automatically logs the transaction's cost-basis in both **USD** and **BRL (Brazilian Real)** to an immutable flat-file ledger for tax reporting.

## 🚀 One-Click Enterprise Deployment
We have built cross-platform deployment scripts to instantly spin up the plugins.
```bash
# Mac / Linux
./enterprise_install.sh

# Windows
.\enterprise_install.ps1
```
This script will cross-compile the plugins to WebAssembly, create a deployment directory (`dist/`), and auto-generate the secure `zeroclaw.toml` configurations required to securely sandbox the agent's RPC network access.

## 📦 Architecture
- `zeroclaw-solana`: WASM plugin providing live RPC token risk-checks and Solana Pay URI generation.
- `zeroclaw-accounting`: WASM plugin providing live USD/BRL fiat price fetching and CSV tax generation.
- `zeroclaw-memory`: A flat-file JSONL durable memory backend for WASM compatibility without C-toolchain dependencies (No SQLite).

## 🔒 Custody Tier: 1 (Build)
This framework explicitly operates in **Tier 1**. The LLM and the agent process hold absolutely **zero** private keys. The agent is strictly a transaction proposer, bouncing the unsigned Solana Pay URI back to a human with a mobile wallet or Ledger hardware device for final cryptographic authorization. 

If the agent is prompt-injected or suffers an RPC failure, the physical hardware approval checkpoint catches it, ensuring a 100% fail-closed system.

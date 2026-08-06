# Technical Architecture & Security Model 🛡️

**System Architecture, WASM Sandboxing, Dashboard Security & 6-Layer Threat Mitigation.**

---

## 1. Architectural Overview

```text
       [ Customer (Telegram / WhatsApp / Discord / CLI) ]
                               │
                               ▼
        [ ZeroClaw Agent & FastAPI Gateway (v1.1.0) ]
                               │
        ├──( GET /setup )──────► [ First-Time Setup Wizard ]
        ├──( GET /dashboard )──► [ Merchant Sales & Security Dashboard ]
        │                             └─► [ 6-Digit PIN Security Keypad ]
        │
        └───────┬───────────────────────────────┬───────────────────────┐
                ▼                               ▼                       ▼
    ┌───────────────────────┐       ┌───────────────────────┐   ┌───────────────┐
    │ zeroclaw-solana WASM  │       │ zeroclaw-accounting   │   │ Multi-Wallet  │
    │ (Risk Check Engine)   │       │ (IRS / BRL Tax Log)   │   │ Deep Links    │
    └───────────┬───────────┘       └───────────┬───────────┘   └───────────────┘
                │                               │
                ▼ (WAKI HTTP RPC)               ▼ (CoinGecko Feed)
       [ Solana Blockchain ]          [ Cost-Basis CSV Ledger ]

---

## 2. Security Defense Layers

1. **Tier 1 Zero-Key Custody**: Server process holds zero private keys.
2. **WASM Sandbox Isolation**: Strict capabilities defined in `zeroclaw.toml`.
3. **Policy-as-Code**: Programmatic limits like `MAX_SPEND` evaluated inside Rust.
4. **Fail-Closed Risk Engine**: Malformed RPC responses default to `Critical Risk`.
5. **Cryptographic Replay Protection**: Signature store invalidates duplicate transactions (`VERIFIED_SIGNATURES`).
6. **Dashboard PIN & Role Security**:
   - 6-Digit Admin Security PIN keypad modal protecting tax CSV exports.
   - Employee RBAC (`👑 Admin Mode` vs `👤 Employee / Cashier Mode`).

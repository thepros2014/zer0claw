# Technical Architecture & Security Model 🛡️

**System Architecture, WASM Sandboxing, and 6-Layer Threat Mitigation.**

---

## 1. Architectural Diagram

```text
               [ Customer (Telegram / WhatsApp / Discord / CLI) ]
                                      │
                                      ▼
                      [ ZeroClaw Agent & FastAPI Gateway ]
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
  ┌─────────────────────────┐                     ┌─────────────────────────┐
  │  zeroclaw-solana WASM   │                     │  zeroclaw-accounting    │
  │  (Risk Engine & Payload)│                     │  (Dual IRS/BRL Logging) │
  └───────────┬─────────────┘                     └───────────┬─────────────┘
              │                                               │
              ▼ (WAKI HTTP RPC)                               ▼ (CoinGecko Feed)
     [ Solana Blockchain ]                          [ Cost-Basis Ledger ]
```

---

## 2. The 6 Security Defense Layers

1. **Zero-Key Custody (Tier 1)**: Agent process holds ZERO private keys.
2. **WASM Sandbox Isolation (`wasm32-wasip2`)**: Strict capabilities defined in `zeroclaw.toml`.
3. **Policy-as-Code**: Limits like `MAX_SPEND` evaluated inside compiled Rust.
4. **Fail-Closed Risk Engine**: Malformed RPC responses default to `Critical Risk`.
5. **Cryptographic Replay Protection**: Gateway invalidates duplicate transaction signatures (`VERIFIED_SIGNATURES`).
6. **On-Chain Semantic Receipts**: SHA-256 intent binding stored in Solana Pay URIs.

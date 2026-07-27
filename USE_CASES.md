# ZeroClaw Agentic Framework: Core Use Cases

The ZeroClaw framework is designed as a foundational infrastructure layer for building secure, autonomous AI agents on Solana. Unlike general-purpose chatbots, ZeroClaw enforces strict cryptographic audit trails and fail-closed logic.

Below are the primary use cases this framework unlocks for developers building in the Superteam Solana ecosystem.

---

## 1. Autonomous DeFi Trading Bots (The "Set and Forget" Agent)
Currently, users rely on limit orders or manually monitoring charts. By integrating a `JupiterSwapTool` into the ZeroClaw framework, developers can build Air-Gapped Trading Agents. 

**How it works:**
- A user provides a natural language prompt: *"Monitor my wallet. If SOL drops below $140, automatically swap 500 USDC for SOL to catch the dip."*
- The ZeroClaw agent runs continuously (e.g., in a cron loop) locally on a secure machine.
- It parses market conditions. If conditions are met, the agent securely calls the Swap tool. 
- **Security Edge:** If the LLM hallucinates and tries to swap 500,000 USDC instead, the tool's fail-closed boundary instantly rejects it.

## 2. "Intent-Based" Consumer Wallets
Mainstream users find the current Solana UX confusing (managing private keys, clicking through complex dApps, signing opaque transactions). ZeroClaw can power the backend of a new breed of "Intent Wallets."

**How it works:**
- The user opens their wallet app and simply types their intent: *"Stake half my SOL and buy a Mad Lads NFT with whatever is left."*
- The ZeroClaw agent parses this natural language into a sequence of rigid Solana Tool calls (e.g., `StakeTool` -> `TensorBuyTool`).
- ZeroClaw generates the unsigned transactions, and presents them to the user for a single, easy signature.

## 3. Cryptographically Auditable Corporate Accounting
DAOs and web3 corporations struggle with transparent accounting for automated payouts (like payroll or recurring bounties). Because ZeroClaw requires a cryptographic HMAC-SHA256 receipt for *every* tool call, it acts as an immutable accountant.

**How it works:**
- A DAO manager types: *"Pay out the monthly 50 USDC retainers to all moderators listed in the Discord."*
- ZeroClaw scrapes the Discord via a tool, formats the Solana transfers, and logs the execution.
- If an auditor later asks *why* the wallet drained 500 USDC, they can query the ZeroClaw SQLite database. The cryptographic receipt proves exactly which LLM prompt and tool logic executed the transfers.

## 4. On-Chain Social Tipping Bots (Discord / Telegram)
Existing tipping bots require users to remember complex slash commands. ZeroClaw enables completely fluid conversational commerce.

**How it works:**
- A user in a Discord channel says: *"Hey ZeroClaw, tip @Alice 5 USDC for fixing my code, and grab 1 USDC for yourself for the gas fees."*
- ZeroClaw understands the conversational context, maps @Alice to her registered Solana address, and generates the exact SPL Token transfer transaction instantly.
- The fail-closed loop ensures the bot never accidentally tips the wrong token.

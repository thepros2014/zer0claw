# Telegram Storefront Integration Guide 🤖

**Deploying an Autonomous Telegram Payment & Digital Goods Cashier.**

---

## 🚀 Quick Setup

### 1. Obtain Bot Token
1. Message `@BotFather` on Telegram.
2. Run `/newbot` and follow prompts.
3. Save the HTTP API token to `telegram-bot/.env`:
   ```env
   TELEGRAM_BOT_TOKEN="your_bot_token"
   GATEWAY_URL="http://localhost:8000"
   MERCHANT_WALLET="DestWallet11111111111111111111111111111111"
   ```

### 2. Available Commands
- `/start` - Welcome message & bot overview.
- `/catalog` - View template storefront catalog.
- `/buy <SKU>` - Generate a zero-key Solana Pay invoice.
- `/verify <invoice_id> <signature>` - Verify payment on-chain & claim digital license key.
- `/help` - Security architecture & Tier 1 zero-key custody model explanation.

### 3. Multi-Wallet Options Rendered
- 🟣 Phantom Wallet
- 🟠 Solflare Wallet
- 🎒 Backpack Wallet
- Raw `solana:` payload for Ledger & Exodus.

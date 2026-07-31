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

### 2. Direct Conversational AI Chat (Buyer-Side Interaction) 💬
Buyers can send natural text messages directly to the bot without typing slash commands:
- *"Hi, what do you sell?"* -> Bot presents current catalog and prices.
- *"I want to buy the eBook"* -> Bot identifies product and generates Solana Pay invoice + QR code image + multi-wallet links automatically.
- *"How does payment work?"* -> Bot explains zero-key Solana Pay and accepted mobile wallets.

### 3. Available Commands
- `/start` - Welcome message & bot overview.
- `/catalog` - View template storefront catalog.
- `/buy <SKU>` - Generate a zero-key Solana Pay invoice.
- `/verify <invoice_id> <signature>` - Verify payment on-chain & claim digital license key.
- `/help` - Security architecture & Tier 1 zero-key custody model explanation.

### 4. Multi-Wallet & QR Code Options Rendered (100% Wallet Support)
- 📷 High-resolution Solana Pay QR Code Image (Scan with ANY phone camera or wallet)
- 🟣 Phantom Wallet Deep Link
- 🟠 Solflare Wallet Deep Link
- 🎒 Backpack Wallet Deep Link
- 🔵 Coinbase Wallet Deep Link
- 🛡️ Trust Wallet Deep Link
- 🌐 Universal `solana:` payload for **Exodus, Ultimate, Brave, OKX, MathWallet, Ledger, & ALL Solana wallets**.

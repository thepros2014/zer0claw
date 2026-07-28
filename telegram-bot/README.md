# ZeroClaw Commerce: Telegram Bot Integration

This module connects Telegram users directly with the ZeroClaw Commerce FastAPI Gateway for zero-key Solana Pay payments, tax accounting, and digital goods delivery.

## 🚀 Quick Setup Instructions

### 1. Create a Telegram Bot Token
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot` and follow the prompts to name your bot.
3. Copy the HTTP API token provided by BotFather.

### 2. Configure Environment Variables
Create a `.env` file in `telegram-bot/`:
```env
TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"
GATEWAY_URL="http://localhost:8000"
MERCHANT_WALLET="DestWallet11111111111111111111111111111111"
```

### 3. Install & Run
```bash
# Navigate to telegram-bot directory
cd telegram-bot

# Install requirements
pip install -r requirements.txt

# Start the bot (ensure FastAPI gateway is running on port 8000)
python bot.py
```

### 4. Available Telegram Commands
- `/start` - Welcome message & bot overview.
- `/catalog` - View digital products for sale.
- `/buy <SKU>` - Generate a zero-key Solana Pay invoice.
- `/verify <invoice_id> <signature>` - Confirm payment on-chain & claim your digital fulfillment token.
- `/help` - Security architecture & Tier 1 zero-key custody model explanation.

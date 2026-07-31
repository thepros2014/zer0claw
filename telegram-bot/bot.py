"""
ZeroClaw Commerce Telegram Bot.
Production-ready async Telegram bot connecting users to the FastAPI Gateway for
zero-key Solana Pay invoices, tax logging, and digital goods delivery.
"""

import os
import logging
import urllib.parse
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET", "FWuAvPKkLxzG47Rygu19NAHLNjUt3y65xyH3NHBwKZUM")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("solona-telegram-bot")

# Digital Product Catalog & Developer Support Donations
CATALOG = {
    "SKU_EBOOK_PDF": {
        "name": "Mastering Solana Dev (eBook PDF)",
        "amount_crypto": 25.0,
        "crypto_symbol": "usd-coin",
        "description": "Comprehensive guide to building high-throughput Solana dApps.",
        "max_spend_policy": 50.0,
    },
    "SKU_SAAS_KEY": {
        "name": "Merchant API License Key",
        "amount_crypto": 49.0,
        "crypto_symbol": "usd-coin",
        "description": "Access key for 10,000 monthly API calls.",
        "max_spend_policy": 100.0,
    },
    "SKU_COMMUNITY_PASS": {
        "name": "VIP Mastermind Access Pass",
        "amount_crypto": 0.5,
        "crypto_symbol": "solana",
        "description": "Exclusive 30-day Discord access token.",
        "max_spend_policy": 2.0,
    },
    "DONATE_KEEP_WORKING": {
        "name": "Developer Keep Working Donation 💻",
        "amount_crypto": 0.2,
        "crypto_symbol": "solana",
        "description": "Support continuous open-source development and maintenance (0.2 SOL).",
        "max_spend_policy": 1.0,
    },
    "DONATE_STAY_AWAKE_COFFEE": {
        "name": "Developer Stay Awake Coffee Donation ☕",
        "amount_crypto": 0.05,
        "crypto_symbol": "solana",
        "description": "Buy the developer a cup of coffee to fuel late-night coding sessions (0.05 SOL).",
        "max_spend_policy": 0.5,
    },
    "DONATE_NEW_FEATURE_5000USD": {
        "name": "Sponsor New Custom Feature 🚀",
        "amount_crypto": 33.0,
        "crypto_symbol": "solana",
        "description": "Sponsor a brand new custom feature build (33.0 SOL).",
        "max_spend_policy": 50.0,
    },
}


async def fn_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command."""
    welcome_text = (
        "🛡️ <b>Welcome to ZeroClaw Commerce Demo Storefront</b>\n"
        "<i>(Template Storefront — Replace with your own digital goods or services)</i>\n\n"
        "I am an autonomous, zero-key payment & digital fulfillment cashier.\n"
        "All transactions are secured via <b>Tier 1 Solana Pay</b> (zero private key risk).\n\n"
        "<b>Available Commands:</b>\n"
        "/catalog - View digital products for sale\n"
        "/buy &lt;SKU&gt; - Generate a Solana Pay invoice\n"
        "/verify &lt;invoice_id&gt; &lt;signature&gt; - Confirm payment & claim item\n"
        "/help - How it works & security model"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)


async def fn_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /catalog command."""
    text = (
        "📦 <b>ZeroClaw Commerce Demo Storefront Catalog:</b>\n"
        "<i>(Template Storefront — Replace with your own digital goods or services)</i>\n\n"
    )
    for sku, item in CATALOG.items():
        symbol = "USDC" if item["crypto_symbol"] == "usd-coin" else "SOL"
        text += (
            f"🔹 <b>{item['name']}</b> (<code>{sku}</code>)\n"
            f"   Price: <b>{item['amount_crypto']} {symbol}</b>\n"
            f"   Description: {item['description']}\n"
            f"   Command: <code>/buy {sku}</code>\n\n"
        )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def fn_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /buy <SKU> command."""
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please specify a product SKU.\nExample: <code>/buy SKU_PRO_KEY</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    sku = context.args[0].upper()
    product = CATALOG.get(sku)

    if not product:
        await update.message.reply_text(
            f"❌ Unknown SKU <code>{sku}</code>. Type /catalog to view valid products.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Extract optional order instructions for store owner
    customer_instructions = " ".join(context.args[1:]) if len(context.args) > 1 else None

    user_id = str(update.effective_user.id)
    intent = f"Purchase {product['name']} for user {user_id}"

    payload = {
        "merchant_wallet": MERCHANT_WALLET,
        "amount_crypto": product["amount_crypto"],
        "crypto_symbol": product["crypto_symbol"],
        "semantic_intent": intent,
        "customer_instructions": customer_instructions,
        "max_spend_policy": product["max_spend_policy"],
        "expires_in_seconds": 900,
    }

    await update.message.reply_text("⏳ Requesting zero-key invoice from Gateway...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{GATEWAY_URL}/api/v1/invoices/create", json=payload)
            if resp.status_code == 201:
                data = resp.json()
                solana_pay_url = data["solana_pay_url"]
                invoice_id = data["invoice_id"]
                symbol = "USDC" if product["crypto_symbol"] == "usd-coin" else "SOL"

                # Multi-Wallet Deep Links & QR Code URL
                encoded_url = urllib.parse.quote(solana_pay_url)
                phantom_link = f"https://phantom.app/ul/browse/{encoded_url}?ref=zeroclaw"
                solflare_link = f"https://solflare.com/ul/v1/browse/{encoded_url}?ref=zeroclaw"
                backpack_link = f"https://backpack.app/ul/browse/{encoded_url}?ref=zeroclaw"
                coinbase_link = f"https://go.cb-w.com/browse/{encoded_url}"
                trust_link = f"https://link.trustwallet.com/open_url?coin_id=501&url={encoded_url}"
                qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}"

                msg = (
                    f"✅ <b>Invoice Created:</b> <code>{invoice_id}</code>\n\n"
                    f"Item: <b>{product['name']}</b>\n"
                    f"Amount Due: <b>{product['amount_crypto']} {symbol}</b>\n"
                    f"Expires in: <b>15 minutes</b>\n\n"
                    f"📷 <b>Scan the QR Code image above with your phone camera or mobile wallet!</b>\n\n"
                    f"🌐 <b>Universal Solana Pay Payload (Supports 100% of Wallets):</b>\n"
                    f"<code>{solana_pay_url}</code>\n"
                    f"<i>(Works with Exodus, Ultimate, Brave, OKX, MathWallet, Ledger & ALL Solana wallets)</i>\n\n"
                    f"<b>Or Tap Your Wallet Below:</b>\n"
                    f"1. Tap your wallet button below.\n"
                    f"2. Authorize payment in your mobile wallet.\n"
                    f"3. Copy your transaction signature and run:\n"
                    f"<code>/verify {invoice_id} &lt;YOUR_TX_SIGNATURE&gt;</code>"
                )

                keyboard = [
                    [
                        InlineKeyboardButton("🟣 Phantom", url=phantom_link),
                        InlineKeyboardButton("🟠 Solflare", url=solflare_link),
                    ],
                    [
                        InlineKeyboardButton("🎒 Backpack", url=backpack_link),
                        InlineKeyboardButton("🔵 Coinbase", url=coinbase_link),
                    ],
                    [
                        InlineKeyboardButton("🛡️ Trust Wallet", url=trust_link),
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Send QR Code photo directly into chat
                await update.message.reply_photo(
                    photo=qr_code_url,
                    caption=msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            else:
                err_detail = resp.json().get("detail", "Gateway error")
                await update.message.reply_text(f"❌ Failed to create invoice: {err_detail}")
        except Exception as e:
            logger.error(f"Error contacting gateway: {e}")
            await update.message.reply_text(
                "❌ Error contacting ZeroClaw Commerce Gateway.\n"
                "Please ensure the Gateway server is running: <code>uvicorn app.main:app --port 8000</code>",
                parse_mode=ParseMode.HTML,
            )


async def fn_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /verify <invoice_id> <signature> command."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: <code>/verify &lt;invoice_id&gt; &lt;signature&gt;</code>\n"
            "Example: <code>/verify inv_123abc sig_mock_solana_signature_9999</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    invoice_id = context.args[0]
    signature = context.args[1]
    user_id = str(update.effective_user.id)

    await update.message.reply_text("⏳ Verifying transaction on Solana blockchain...")

    verify_payload = {
        "invoice_id": invoice_id,
        "signature": signature,
        "merchant_wallet": MERCHANT_WALLET,
        "amount_crypto": 50.0,
        "crypto_symbol": "usd-coin",
        "tax_category": "Service Revenue",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            v_resp = await client.post(f"{GATEWAY_URL}/api/v1/payments/verify", json=verify_payload)
            if v_resp.status_code != 200:
                err_msg = v_resp.json().get("detail", "Verification failed")
                await update.message.reply_text(f"❌ Payment Verification Failed: {err_msg}")
                return

            v_data = v_resp.json()

            fulfill_payload = {
                "invoice_id": invoice_id,
                "customer_id": user_id,
                "channel": "telegram",
                "digital_item_sku": "SKU_PRO_KEY",
            }

            f_resp = await client.post(f"{GATEWAY_URL}/api/v1/fulfillment/deliver", json=fulfill_payload)
            if f_resp.status_code == 200:
                f_data = f_resp.json()
                success_msg = (
                    f"🎉 <b>Payment Confirmed & Item Delivered!</b>\n\n"
                    f"Tx Signature: <code>{signature[:16]}...</code>\n"
                    f"IRS Accounting: <b>${v_data['amount_usd']:.2f} USD</b>\n"
                    f"Receita Federal Accounting: <b>R${v_data['amount_brl']:.2f} BRL</b>\n"
                    f"Receipt Hash: <code>{v_data['receipt_signature'][:16]}...</code>\n\n"
                    f"🔑 <b>Your Digital Fulfillment Token:</b>\n"
                    f"<code>{f_data['fulfillment_token']}</code>\n\n"
                    f"💬 <b>Store Owner Feedback:</b>\n"
                    f"How was your checkout experience? Reply here or type:\n"
                    f"<code>/feedback &lt;your message or concern&gt;</code>\n"
                    f"<i>(Your note will be sent directly to the owner's Private Dashboard Inbox!)</i>"
                )
                await update.message.reply_text(success_msg, parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("⚠️ Payment verified, but fulfillment delivery hit an error.")

        except Exception as e:
            logger.error(f"Error during verification: {e}")
            await update.message.reply_text("❌ Error processing verification with Gateway.")


async def fn_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command."""
    help_text = (
        "🔒 <b>ZeroClaw Commerce Security Architecture</b>\n\n"
        "• <b>Tier 1 Zero-Key Custody:</b> The bot and agent never touch private keys.\n"
        "• <b>Policy-as-Code:</b> Spending limits are enforced inside the WASM sandbox.\n"
        "• <b>Semantic Receipts:</b> Payment intent is embedded into Solana Pay URIs.\n"
        "• <b>Dual-Currency Tax Accounting:</b> Real-time IRS ($USD) and Receita Federal (R$BRL) cost-basis logging.\n"
        "• <b>Replay Protection:</b> On-chain transaction signatures are uniquely verified."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)


async def fn_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /feedback <message> command."""
    if not context.args:
        await update.message.reply_text(
            "⚠️ Please include a feedback message or concern.\n"
            "Example: <code>/feedback Great service! Instant token delivery.</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    msg = " ".join(context.args)
    user_id = f"user_{update.effective_user.id}"

    payload = {
        "customer_id": user_id,
        "channel": "Telegram",
        "message": msg,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{GATEWAY_URL}/api/v1/feedback/submit", json=payload)
            if resp.status_code == 200:
                await update.message.reply_text(
                    "📬 <b>Thank you!</b> Your message has been sent directly to the store owner's Private Dashboard Inbox for review.",
                    parse_mode=ParseMode.HTML,
                )
            else:
                await update.message.reply_text("❌ Failed to submit feedback to store owner.")
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            await update.message.reply_text("❌ Error contacting Gateway.")


async def fn_conversational_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct Conversational AI Cashier Handler for buyer-side natural language chat."""
    if not update or not update.message or not update.message.text:
        return
    user_msg = update.message.text.strip()
    user_msg_lower = user_msg.lower()
    
    # 1. Natural Language Product Matcher & Auto Checkout
    matched_sku = None
    if any(w in user_msg_lower for w in ["ebook", "book", "pdf", "solana dev", "solana course", "rust", "tutorial", "guide"]):
        matched_sku = "SKU_EBOOK_PDF"
    elif any(w in user_msg_lower for w in ["api", "key", "license", "saas", "developer key", "integration"]):
        matched_sku = "SKU_SAAS_KEY"
    elif any(w in user_msg_lower for w in ["vip", "mastermind", "pass", "community", "discord", "access", "membership"]):
        matched_sku = "SKU_COMMUNITY_PASS"

    if matched_sku:
        context.args = [matched_sku]
        product = CATALOG[matched_sku]
        symbol = "USDC" if product["crypto_symbol"] == "usd-coin" else "SOL"
        await update.message.reply_text(
            f"🤖 <b>AI Store Cashier:</b> Absolutely! I can help you purchase <b>{product['name']}</b> ({product['amount_crypto']} {symbol}).\n\n"
            f"<i>{product['description']}</i>\n\n"
            f"Generating your zero-key Solana Pay invoice and QR Code...",
            parse_mode=ParseMode.HTML,
        )
        await fn_buy(update, context)
        return

    # 2. Natural Feedback / Concern Submission
    if any(w in user_msg_lower for w in ["feedback", "concern", "issue", "problem", "review", "complaint", "owner", "admin"]):
        context.args = user_msg.split()
        await fn_feedback(update, context)
        return

    # 3. Discount / Pricing Inquiry
    if any(w in user_msg_lower for w in ["discount", "cheap", "price", "cost", "how much", "deal", "offer", "usd", "usdc", "sol"]):
        await update.message.reply_text(
            "🤖 <b>AI Store Cashier:</b> Here is our store pricing catalog:\n\n"
            "• <b>Mastering Solana Dev (eBook PDF)</b> — <code>25.0 USDC</code>\n"
            "• <b>Merchant API License Key</b> — <code>49.0 USDC</code>\n"
            "• <b>VIP Mastermind Access Pass</b> — <code>0.5 SOL</code>\n\n"
            "Prices are fixed in USDC & SOL on-chain. To purchase, just say <i>'I want the eBook'</i> or <i>'Buy API key'</i>!",
            parse_mode=ParseMode.HTML,
        )
        return

    # 4. Payment Method & Wallet Safety Inquiry
    if any(w in user_msg_lower for w in ["how to pay", "how do i pay", "wallet", "phantom", "solflare", "backpack", "coinbase", "trust", "exodus", "safe", "secure", "privacy"]):
        await update.message.reply_text(
            "🤖 <b>AI Store Cashier:</b> Paying is instant & 100% safe!\n\n"
            "• <b>Zero-Key Custody:</b> We never hold or request your private keys.\n"
            "• <b>100% Wallet Compatible:</b> Scan our QR code or tap your wallet (Phantom, Solflare, Backpack, Coinbase, Trust Wallet, Exodus, Ledger, etc.).\n"
            "• <b>Instant Settlement:</b> Verified on the Solana blockchain in under 2 seconds.\n\n"
            "Say <i>'Show catalog'</i> or <i>'I want to buy...'</i> to get started!",
            parse_mode=ParseMode.HTML,
        )
        return

    # 5. Order Support / Verification Inquiry
    if any(w in user_msg_lower for w in ["verify", "signature", "paid", "confirm", "receipt", "where is my item", "token"]):
        await update.message.reply_text(
            "🤖 <b>AI Store Cashier:</b> Got your transaction signature?\n\n"
            "To verify your payment on-chain and claim your digital asset token, type:\n"
            "<code>/verify &lt;invoice_id&gt; &lt;YOUR_TX_SIGNATURE&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # 6. Catalog / Store Inquiry
    if any(w in user_msg_lower for w in ["catalog", "product", "sell", "buy", "store", "item", "available", "what do you have", "hello", "hi", "hey"]):
        await update.message.reply_text(
            "🤖 <b>AI Store Cashier:</b> Hello! Welcome to our store.\n\n"
            "Here are our available digital goods:\n"
            "1. <b>Mastering Solana Dev (eBook PDF)</b> — 25.0 USDC\n"
            "2. <b>Merchant API License Key</b> — 49.0 USDC\n"
            "3. <b>VIP Mastermind Access Pass</b> — 0.5 SOL\n\n"
            "💬 You can talk to me naturally! Try saying:\n"
            "• <i>'I want to buy the eBook'</i>\n"
            "• <i>'Can I get an API key?'</i>\n"
            "• <i>'How does payment work?'</i>",
            parse_mode=ParseMode.HTML,
        )
        return

    # 7. Intelligent Fallback Assistant
    reply_text = (
        f"🤖 <b>AI Store Cashier:</b> I understood your message: <i>\"{user_msg}\"</i>\n\n"
        f"I am your store cashier! Here is how I can assist you:\n"
        f"• Type or say <i>'catalog'</i> to view all products.\n"
        f"• Mention any item (e.g. <i>'eBook'</i>, <i>'API Key'</i>, <i>'VIP Pass'</i>) to generate a Solana Pay QR invoice instantly.\n"
        f"• Send feedback to the store owner using <code>/feedback &lt;message&gt;</code>."
    )
    await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)


def main():
    """Starts the Telegram bot."""
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("ERROR: Please set TELEGRAM_BOT_TOKEN in your environment or .env file.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", fn_start))
    app.add_handler(CommandHandler("catalog", fn_catalog))
    app.add_handler(CommandHandler("buy", fn_buy))
    app.add_handler(CommandHandler("verify", fn_verify))
    app.add_handler(CommandHandler("feedback", fn_feedback))
    app.add_handler(CommandHandler("help", fn_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fn_conversational_chat))

    masked_token = f"{TELEGRAM_BOT_TOKEN[:3]}...{TELEGRAM_BOT_TOKEN[-3:]}" if len(TELEGRAM_BOT_TOKEN) > 6 else "******"
    logger.info(f"ZeroClaw Commerce Telegram Bot is running with token [{masked_token}]...")
    app.run_polling()


if __name__ == "__main__":
    main()

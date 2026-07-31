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
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET", "DestWallet11111111111111111111111111111111")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("solona-telegram-bot")

# Digital Product Catalog (Merchant Sample Inventory)
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

    user_id = str(update.effective_user.id)
    intent = f"Purchase {product['name']} for user {user_id}"

    payload = {
        "merchant_wallet": MERCHANT_WALLET,
        "amount_crypto": product["amount_crypto"],
        "crypto_symbol": product["crypto_symbol"],
        "semantic_intent": intent,
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
                qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}"

                msg = (
                    f"✅ <b>Invoice Created:</b> <code>{invoice_id}</code>\n\n"
                    f"Item: <b>{product['name']}</b>\n"
                    f"Amount Due: <b>{product['amount_crypto']} {symbol}</b>\n"
                    f"Expires in: <b>15 minutes</b>\n\n"
                    f"📷 <b>Scan the QR Code image above with your phone camera or mobile wallet!</b>\n\n"
                    f"📱 <b>Solana Pay Payload:</b>\n"
                    f"<code>{solana_pay_url}</code>\n\n"
                    f"<b>Or Select Your Mobile Wallet Below:</b>\n"
                    f"1. Tap Phantom, Solflare, or Backpack below.\n"
                    f"2. Authorize the transaction in your wallet.\n"
                    f"3. Copy your transaction signature and run:\n"
                    f"<code>/verify {invoice_id} &lt;YOUR_TX_SIGNATURE&gt;</code>"
                )

                keyboard = [
                    [
                        InlineKeyboardButton("🟣 Phantom", url=phantom_link),
                        InlineKeyboardButton("🟠 Solflare", url=solflare_link),
                    ],
                    [
                        InlineKeyboardButton("🎒 Backpack Wallet", url=backpack_link),
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
                    f"<code>{f_data['fulfillment_token']}</code>"
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


async def fn_conversational_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct Conversational AI Cashier Handler for buyer-side natural language chat."""
    user_msg = update.message.text.strip()
    user_msg_lower = user_msg.lower()
    
    # 1. Product Matcher / Auto Checkout
    matched_sku = None
    if any(w in user_msg_lower for w in ["ebook", "book", "pdf", "solana dev", "solana course"]):
        matched_sku = "SKU_EBOOK_PDF"
    elif any(w in user_msg_lower for w in ["api", "key", "license", "saas"]):
        matched_sku = "SKU_SAAS_KEY"
    elif any(w in user_msg_lower for w in ["vip", "mastermind", "pass", "community", "discord"]):
        matched_sku = "SKU_COMMUNITY_PASS"

    if matched_sku:
        context.args = [matched_sku]
        product = CATALOG[matched_sku]
        await update.message.reply_text(
            f"🤖 <b>AI Cashier Assistant:</b> I'd be happy to help you purchase <b>{product['name']}</b>!\n"
            f"Generating your secure Solana Pay invoice now...",
            parse_mode=ParseMode.HTML,
        )
        await fn_buy(update, context)
        return

    # 2. Catalog / Store Inquiry
    if any(w in user_msg_lower for w in ["catalog", "product", "sell", "buy", "store", "item", "available", "what do you have"]):
        await update.message.reply_text(
            "🤖 <b>AI Cashier Assistant:</b> Welcome! Here is our current digital goods catalog:\n\n"
            "• <b>Mastering Solana Dev (eBook PDF)</b> — 25.0 USDC\n"
            "• <b>Merchant API License Key</b> — 49.0 USDC\n"
            "• <b>VIP Mastermind Access Pass</b> — 0.5 SOL\n\n"
            "Simply tell me which item you'd like (e.g. <i>'I want to buy the eBook'</i>) or type <code>/buy &lt;SKU&gt;</code>!",
            parse_mode=ParseMode.HTML,
        )
        return

    # 3. Payment Verification Inquiry
    if any(w in user_msg_lower for w in ["verify", "signature", "paid", "confirm"]):
        await update.message.reply_text(
            "🤖 <b>AI Cashier Assistant:</b> To confirm your payment and receive your digital item token, run:\n"
            "<code>/verify &lt;invoice_id&gt; &lt;YOUR_TX_SIGNATURE&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    # 4. General Conversational Assistant
    reply_text = (
        f"🤖 <b>AI Cashier Assistant:</b> Hello! I am your autonomous AI Store Cashier.\n\n"
        f"I can help you purchase digital goods with <b>Tier 1 Zero-Key Solana Pay</b> (using Phantom, Solflare, Backpack, or Ledger).\n\n"
        f"💬 <b>You can ask me anything naturally!</b> Try saying:\n"
        f"• <i>'Show me the store catalog'</i>\n"
        f"• <i>'I want to buy the Solana dev ebook'</i>\n"
        f"• <i>'How does payment work?'</i>"
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
    app.add_handler(CommandHandler("help", fn_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fn_conversational_chat))

    masked_token = f"{TELEGRAM_BOT_TOKEN[:3]}...{TELEGRAM_BOT_TOKEN[-3:]}" if len(TELEGRAM_BOT_TOKEN) > 6 else "******"
    logger.info(f"ZeroClaw Commerce Telegram Bot is running with token [{masked_token}]...")
    app.run_polling()


if __name__ == "__main__":
    main()

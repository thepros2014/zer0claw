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

                # Encode Phantom deep link
                phantom_deep_link = f"https://phantom.app/ul/browse/{urllib.parse.quote(solana_pay_url)}?ref=solona"

                msg = (
                    f"✅ <b>Invoice Created:</b> <code>{invoice_id}</code>\n\n"
                    f"Item: <b>{product['name']}</b>\n"
                    f"Amount Due: <b>{product['amount_crypto']} {symbol}</b>\n"
                    f"Expires in: <b>15 minutes</b>\n\n"
                    f"📱 <b>Solana Pay Payload:</b>\n"
                    f"<code>{solana_pay_url}</code>\n\n"
                    f"<b>How to Pay:</b>\n"
                    f"1. Copy the payload above or click Phantom button below.\n"
                    f"2. Sign & broadcast the transaction in Phantom/Solflare.\n"
                    f"3. Copy your transaction signature and run:\n"
                    f"<code>/verify {invoice_id} &lt;YOUR_TX_SIGNATURE&gt;</code>"
                )

                keyboard = [
                    [InlineKeyboardButton("📱 Pay via Phantom Wallet", url=phantom_deep_link)],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                )
            else:
                err_detail = resp.json().get("detail", "Gateway error")
                await update.message.reply_text(f"❌ Failed to create invoice: {err_detail}")
        except Exception as e:
            logger.error(f"Error contacting gateway: {e}")
            await update.message.reply_text("❌ Error contacting ZeroClaw Commerce Gateway.")


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

    logger.info("ZeroClaw Commerce Telegram Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

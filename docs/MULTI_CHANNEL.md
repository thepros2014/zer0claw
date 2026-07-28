# Multi-Channel Storefront Integration Guide 🌐

**Discord Slash Commands & WhatsApp Cloud API Webhook Integration.**

---

## 🎮 Discord Bot (`discord-bot/`)

### Features
- Native Slash Commands (`/catalog`, `/buy <sku>`, `/verify <invoice_id> <signature>`).
- Styled Discord Embeds with action buttons for Phantom wallet.
- Private Direct Message (DM) delivery for digital goods.

---

## 📱 WhatsApp Webhook (`whatsapp-bot/`)

### Features
- FastAPI Webhook service (`POST /webhook/whatsapp`).
- Meta WhatsApp Cloud API verification handshake.
- Command parser handling `catalog`, `buy <sku>`, and `verify <invoice_id> <signature>`.

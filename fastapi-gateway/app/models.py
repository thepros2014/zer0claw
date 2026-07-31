"""Pydantic V2 Models for Solona Commerce Gateway."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaxCategory(str, Enum):
    SERVICE_REVENUE = "Service Revenue"
    MERCHANDISE = "Merchandise"
    DONATION = "Donation"
    CAPITAL_GAIN = "Capital Gain"


class CryptoSymbol(str, Enum):
    USDC = "usd-coin"
    SOL = "solana"


class InvoiceCreateRequest(BaseModel):
    merchant_wallet: str = Field(
        ...,
        description="Destination Solana wallet address",
        min_length=32,
        max_length=64,
    )
    amount_crypto: float = Field(
        ...,
        gt=0,
        description="Amount of crypto to request",
    )
    crypto_symbol: CryptoSymbol = Field(
        CryptoSymbol.USDC,
        description="Cryptocurrency identifier",
    )
    semantic_intent: str = Field(
        ...,
        description="Human-readable reason for the payment (Semantic Receipt)",
        min_length=3,
    )
    max_spend_policy: Optional[float] = Field(
        None,
        description="Optional Policy-as-Code spend limit",
    )
    confirmations_required: int = Field(
        1,
        ge=1,
        le=32,
        description="Minimum confirmation depth required for settlement.",
    )
    customer_instructions: Optional[str] = Field(
        None,
        description="Optional customer instructions or notes for the store owner",
    )
    expires_in_seconds: int = Field(
        900,
        ge=60,
        le=86400,
        description="Invoice expiration window in seconds (default 15 minutes).",
    )


class InvoiceResponse(BaseModel):
    success: bool
    invoice_id: str
    solana_pay_url: str
    amount_crypto: float
    crypto_symbol: str
    merchant_wallet: str
    semantic_intent: str
    reference: str
    expires_at: int
    invoice_hash: str
    confirmations_required: int


class PaymentVerifyRequest(BaseModel):
    invoice_id: str = Field(
        ...,
        description="Unique invoice ID",
    )
    signature: str = Field(
        ...,
        description="Solana transaction signature",
        min_length=32,
    )
    merchant_wallet: str = Field(
        ...,
        description="Merchant wallet address",
        min_length=32,
        max_length=64,
    )
    amount_crypto: float = Field(
        ...,
        gt=0,
        description="Expected crypto amount",
    )
    crypto_symbol: CryptoSymbol = Field(
        CryptoSymbol.USDC,
        description="Crypto symbol",
    )
    tax_category: TaxCategory = Field(
        TaxCategory.SERVICE_REVENUE,
        description="IRS Tax Category",
    )


class PaymentVerifyResponse(BaseModel):
    success: bool
    confirmed: bool
    signature: str
    amount_usd: float
    amount_brl: float
    tax_category: str
    receipt_signature: str
    invoice_hash: str
    reference: str
    message: str


class DigitalFulfillmentRequest(BaseModel):
    invoice_id: str = Field(
        ...,
        description="Invoice ID of confirmed payment",
    )
    customer_id: str = Field(
        ...,
        description="Telegram/WhatsApp/Discord user ID",
    )
    channel: str = Field(
        ...,
        description="Communication channel name (e.g. telegram, whatsapp, discord)",
    )
    digital_item_sku: str = Field(
        ...,
        description="SKU or product key of the digital asset",
    )


class DigitalFulfillmentResponse(BaseModel):
    success: bool
    customer_id: str
    channel: str
    digital_item_sku: str
    fulfillment_token: str
    delivered_at: int


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

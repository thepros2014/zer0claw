"""Async Pytest Suite for FastAPI Commerce Gateway."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_invoice_success():
    payload = {
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 50.0,
        "crypto_symbol": "usd-coin",
        "semantic_intent": "Paying for Pro License Key",
        "max_spend_policy": 100.0,
    }
    response = client.post("/api/v1/invoices/create", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "solana:DestWallet11111111111111111111111111111111?amount=50.0" in data["solana_pay_url"]
    assert "message=Paying%20for%20Pro%20License%20Key" in data["solana_pay_url"]


def test_create_invoice_policy_violation():
    payload = {
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 500.0,
        "crypto_symbol": "usd-coin",
        "semantic_intent": "Attempting over-limit purchase",
        "max_spend_policy": 100.0,
    }
    response = client.post("/api/v1/invoices/create", json=payload)
    assert response.status_code == 400
    assert "Policy Violation" in response.json()["detail"]


def test_verify_payment_success():
    payload = {
        "invoice_id": "inv_test123",
        "signature": "sig_mock_solana_signature_9999",
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 2.0,
        "crypto_symbol": "solana",
        "tax_category": "Service Revenue",
    }
    response = client.post("/api/v1/payments/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["confirmed"] is True
    assert data["amount_usd"] == 300.0  # 2 SOL * 150 USD
    assert data["amount_brl"] == 1680.0  # 2 SOL * 840 BRL
    assert len(data["receipt_signature"]) == 64


def test_digital_fulfillment_success():
    payload = {
        "invoice_id": "inv_test123",
        "customer_id": "user_telegram_445921",
        "channel": "telegram",
        "digital_item_sku": "SKU_PRO_LICENSE_2026",
    }
    response = client.post("/api/v1/fulfillment/deliver", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["customer_id"] == "user_telegram_445921"
    assert data["fulfillment_token"].startswith("SOLONA_DELIVERY_")

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
    # First create a real invoice so it exists in the store
    create_payload = {
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 2.0,
        "crypto_symbol": "solana",
        "semantic_intent": "Paying for SOL service",
    }
    create_resp = client.post("/api/v1/invoices/create", json=create_payload)
    assert create_resp.status_code == 201
    invoice_id = create_resp.json()["invoice_id"]

    payload = {
        "invoice_id": invoice_id,
        "signature": "sig_mock_solana_signature_999900aa",  # ≥32 chars, starts with sig_
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
    # Create and pay an invoice so fulfillment can proceed
    create_payload = {
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 1.0,
        "crypto_symbol": "usd-coin",
        "semantic_intent": "Paying for digital license",
    }
    create_resp = client.post("/api/v1/invoices/create", json=create_payload)
    assert create_resp.status_code == 201
    invoice_id = create_resp.json()["invoice_id"]

    verify_payload = {
        "invoice_id": invoice_id,
        "signature": "sig_fulfill_test_signature_00aa00",  # ≥32 chars, starts with sig_
        "merchant_wallet": "DestWallet11111111111111111111111111111111",
        "amount_crypto": 1.0,
        "crypto_symbol": "usd-coin",
        "tax_category": "Service Revenue",
    }
    verify_resp = client.post("/api/v1/payments/verify", json=verify_payload)
    assert verify_resp.status_code == 200

    payload = {
        "invoice_id": invoice_id,
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

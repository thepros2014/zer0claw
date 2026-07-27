#!/bin/bash
set -e

echo "============================================================"
echo " ZeroClaw Enterprise Drop-in Installer (Solana Tax Terminal)"
echo "============================================================"
echo ""

echo "[1/4] Compiling WASM Plugins in Release Mode..."
cargo build --release --target wasm32-wasip2

echo "[2/4] Setting up deployment directory: dist/enterprise_zeroclaw_node/plugins"
mkdir -p dist/enterprise_zeroclaw_node/plugins

echo "[3/4] Copying WASM binaries to deployment directory..."
cp target/wasm32-wasip2/release/zeroclaw_solana.wasm dist/enterprise_zeroclaw_node/plugins/
cp target/wasm32-wasip2/release/zeroclaw_accounting.wasm dist/enterprise_zeroclaw_node/plugins/

echo "[4/4] Generating Enterprise Config (zeroclaw.toml)..."
cat << EOF > dist/enterprise_zeroclaw_node/zeroclaw.toml
[node]
name = "ZeroClaw Tax Terminal"
version = "1.0.0"

[plugins]
dir = "plugins"

[[plugins.permissions]]
plugin = "zeroclaw_solana"
allow = ["http_client"]

[[plugins.permissions]]
plugin = "zeroclaw_accounting"
allow = ["http_client"]

[enterprise_settings]
# Mock configuration for Tier 2 Bulk Queue / Multisig Architecture
squads_vault_address = "SQDS4ep65T869zXYMM2dCbxtBG65zBma5p8m3dKqJ7T"
require_hardware_wallet_interceptor = true
tax_reporting_currency = "USD,BRL"
EOF

echo ""
echo "============================================================"
echo " Success! Enterprise Node Deployment Ready."
echo " Location: dist/enterprise_zeroclaw_node"
echo " Run your ZeroClaw agent pointing to this configuration to start."
echo "============================================================"

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " ZeroClaw Enterprise Drop-in Installer (Solana Tax Terminal)"
Write-Host "============================================================"
Write-Host ""

Write-Host "[1/4] Compiling WASM Plugins in Release Mode..."
cargo build --release --target wasm32-wasip2

Write-Host "[2/4] Setting up deployment directory: dist/enterprise_zeroclaw_node/plugins"
$PluginDir = "dist/enterprise_zeroclaw_node/plugins"
if (!(Test-Path -Path $PluginDir)) {
    New-Item -ItemType Directory -Force -Path $PluginDir | Out-Null
}

Write-Host "[3/4] Copying WASM binaries to deployment directory..."
Copy-Item -Path "target/wasm32-wasip2/release/zeroclaw_solana.wasm" -Destination $PluginDir -Force
Copy-Item -Path "target/wasm32-wasip2/release/zeroclaw_accounting.wasm" -Destination $PluginDir -Force

Write-Host "[4/4] Generating Enterprise Config (zeroclaw.toml)..."
$ConfigContent = @"
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
"@

Set-Content -Path "dist/enterprise_zeroclaw_node/zeroclaw.toml" -Value $ConfigContent

Write-Host ""
Write-Host "============================================================"
Write-Host " Success! Enterprise Node Deployment Ready."
Write-Host " Location: dist/enterprise_zeroclaw_node"
Write-Host " Run your ZeroClaw agent pointing to this configuration to start."
Write-Host "============================================================"

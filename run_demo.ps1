$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host " Building Seamless Mock CLI Demo..."
Write-Host "============================================================"
cargo build -p mock-cli --release

Write-Host "`nLaunching ZeroClaw Tier 1 Mock Agent..."
Write-Host "============================================================"
Start-Sleep -Seconds 1

cargo run -p mock-cli --release

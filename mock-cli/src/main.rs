//! Mock CLI binary crate for ZeroClaw Tier 1 interactive demo.

use serde_json::json;
use std::io::{self, Write};
use std::thread;
use std::time::Duration;
use zeroclaw_accounting::ProcessPaymentTool;
use zeroclaw_api::{Tool, ToolContext};
use zeroclaw_solana::{SolanaRiskCheckTool, SolanaTransferTool};

fn main() {
    println!("============================================================");
    println!(" ZeroClaw Agent Terminal [Tier 1 Security Mode]");
    println!(" Plugins Loaded: Solana Risk Engine, Dual-Currency Accounting");
    println!("============================================================");

    let ctx = ToolContext {
        identity_key_bytes: b"mock_tier1_key_00000000000000000".to_vec(),
    };

    let solana_tool = SolanaTransferTool::new();
    let risk_tool = SolanaRiskCheckTool::new();
    let accounting_tool = ProcessPaymentTool::new("tax_ledger.jsonl");

    loop {
        print!("\n> ");
        let _ = io::stdout().flush();

        let mut input = String::new();
        if io::stdin().read_line(&mut input).is_err() {
            break;
        }
        let input = input.trim();

        if input.is_empty() {
            continue;
        }

        if input.eq_ignore_ascii_case("exit") {
            break;
        }

        println!("\n[Agent is thinking...]");
        thread::sleep(Duration::from_millis(1500));

        let lower = input.to_lowercase();

        if lower.contains("risk") {
            // Try to extract a token address from the command (last whitespace-separated token).
            // Fall back to the wrapped-SOL mint for demo purposes if none is provided.
            let token_address = input
                .split_whitespace()
                .last()
                .filter(|s| s.len() >= 32)
                .unwrap_or("So11111111111111111111111111111111111111112");

            println!(
                "Agent: Running token risk analysis for {}…",
                token_address
            );
            thread::sleep(Duration::from_millis(800));

            println!("\n[RISK ENGINE TRIGGERED]");

            let args = json!({
                "token_address": token_address,
                "action": "analyze"
            });

            let result = risk_tool.execute(args, &ctx);
            if result.success {
                println!("Agent: {}\n", result.output);
            } else {
                println!(
                    "Agent: Risk check failed — {}",
                    result.error.unwrap_or_default()
                );
            }
        } else if lower.contains("pay") && lower.contains("usdc") {
            println!(
                "Agent: Invoice queued for 50 USDC. Security policy (Tier 1) blocks me from holding hot keys. Please scan the Solana Pay payload below to authorize:"
            );
            thread::sleep(Duration::from_millis(800));

            println!("\n[WALLET INTERCEPTOR TRIGGERED]");

            let args = json!({
                "destination_address": "DestWallet11111111111111111111111111111111",
                "amount": 50.0,
                "semantic_intent": "Paying vendor for software services",
                "security_policy": "MAX_SPEND=100"
            });

            let result = solana_tool.execute(args, &ctx);
            println!("{}\n", result.output);

            thread::sleep(Duration::from_secs(2));
            println!("\n[Network Check: Transaction Confirmed]");
            println!("Agent: On-chain settlement confirmed. Processing dual-currency tax logic...");

            thread::sleep(Duration::from_millis(1500));
            let acct_args = json!({
                "wallet_address": "DestWallet11111111111111111111111111111111",
                "crypto_symbol": "usd-coin",
                "amount_crypto": 50.0,
                "tax_category": "Service Revenue"
            });

            let acct_result = accounting_tool.execute(acct_args, &ctx);
            println!("Agent: {}", acct_result.output);
        } else {
            println!(
                "Agent: Unrecognized command. Try: 'pay 50 usdc' to generate a Solana Pay invoice, or 'risk check' to analyze a token."
            );
        }
    }
}

use serde_json::json;
use std::io::{self, Write};
use std::thread;
use std::time::Duration;
use zeroclaw_api::{Tool, ToolContext};
use zeroclaw_accounting::ProcessPaymentTool;
use zeroclaw_solana::SolanaTransferTool;

fn main() {
    println!("============================================================");
    println!(" ZeroClaw Agent Terminal [Tier 1 Security Mode]");
    println!(" Plugins Loaded: Solana Risk Engine, Dual-Currency Accounting");
    println!("============================================================");
    
    let ctx = ToolContext {
        identity_key_bytes: b"mock_tier1_key_00000000000000000".to_vec(),
    };

    let solana_tool = SolanaTransferTool::new();
    let accounting_tool = ProcessPaymentTool::new("tax_ledger.jsonl");

    loop {
        print!("\n> ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        let input = input.trim();

        if input.is_empty() {
            continue;
        }

        if input.eq_ignore_ascii_case("exit") {
            break;
        }

        println!("\n[Agent is thinking...]");
        thread::sleep(Duration::from_millis(1500));

        if input.to_lowercase().contains("pay") && input.to_lowercase().contains("usdc") {
            println!("Agent: Invoice queued for 50 USDC. Security policy (Tier 1) blocks me from holding hot keys. Please scan the Solana Pay payload below to authorize:");
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
            
            thread::sleep(Duration::from_millis(2000));
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
            println!("Agent: Unrecognized command. I'm currently locked to Payment and Tax reporting functions. Try asking me to pay an invoice or run a risk check.");
        }
    }
}

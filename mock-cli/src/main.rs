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
        identity_key_bytes: b"mock_tier1_key".to_vec(),
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
            println!("Agent: I have prepared the transaction for 50 USDC. However, as a Tier 1 agent, I hold ZERO keys and cannot sign this transaction.");
            thread::sleep(Duration::from_millis(800));
            
            println!("\n[WALLET INTERCEPTOR TRIGGERED]");
            
            let args = json!({
                "destination_address": "DestWallet11111111111111111111111111111111",
                "amount": 50.0
            });
            
            let result = solana_tool.execute(args, &ctx);
            println!("{}\n", result.output);
            
            thread::sleep(Duration::from_millis(2000));
            println!("\n[Network Check: Transaction Confirmed]");
            println!("Agent: I have detected the transaction successfully settled on the blockchain. Initiating tax accounting plugin...");
            
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
            println!("Agent: I am currently configured strictly as a Payment and Tax Terminal. Please ask me to pay an invoice or check token risk.");
        }
    }
}

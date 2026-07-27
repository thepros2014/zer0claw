use rusqlite::Connection;
use std::collections::HashMap;
use zeroclaw_api::{Memory, Provider, Tool, ToolContext};
use zeroclaw_llamacpp::LlamaCppProvider;
use zeroclaw_memory::SqliteMemory;
use zeroclaw_solana::{SolanaRiskCheckTool, SolanaTransferTool};
use zeroclaw_accounting::{ProcessPaymentTool, GenerateTaxReportTool};
fn run_agent_loop(
    prompt: &str,
    provider: &dyn Provider,
    tool_registry: &HashMap<String, Box<dyn Tool>>,
    available_tools: &[(&str, serde_json::Value)],
    ctx: &ToolContext,
    memory: &SqliteMemory,
) {
    println!("\n  USER: \"{}\"", prompt);
    let mut current_prompt = prompt.to_string();
    let max_retries = 3;
    let mut attempt = 0;

    while attempt < max_retries {
        attempt += 1;
        match provider.generate_tool_call(&current_prompt, available_tools) {
            Ok(Some(tool_call)) => {
                println!("  [Attempt {}] LLM Decided to call: {}", attempt, tool_call.tool_name);
                
                if let Some(tool) = tool_registry.get(&tool_call.tool_name) {
                    let result = tool.execute(tool_call.args.clone(), ctx);
                    
                    // Log to Memory
                    memory.log_tool_execution(tool.name(), &tool_call.args, &result)
                        .expect("Failed to log execution");
                    
                    if result.success {
                        println!("  LLM successfully executed tool! Output: {}", result.output);
                        
                        // Wallet Interceptor Logic
                        if result.output.contains("Unsigned transaction") || result.output.contains("Unsigned transfer") {
                            println!("\n  ========================================================");
                            println!("  ⚠️ [WALLET INTERCEPTOR] Unsigned Transaction Detected.");
                            println!("  ========================================================");
                            println!("  The AI has prepared an action that mutates state, but it lacks private keys.");
                            println!("  Please plug in your Ledger Hardware Wallet via USB to sign the payload.");
                            print!("  Press ENTER once the device is connected and unlocked...");
                            std::io::stdout().flush().unwrap();
                            
                            let mut dummy = String::new();
                            std::io::stdin().read_line(&mut dummy).unwrap();
                            
                            println!("  [Ledger Simulator] Handshake successful.");
                            println!("  [Ledger Simulator] Transaction signed and broadcast to mainnet.");
                            println!("  ========================================================\n");
                        }

                        break; // Success, exit loop
                    } else {
                        let error_msg = result.error.unwrap_or_else(|| "Unknown security error".to_string());
                        println!("  SECURITY BLOCKED! Reason: {}", error_msg);
                        
                        // Agentic Loop: Feed error back into prompt for retry
                        current_prompt = format!(
                            "{}\nSystem: The tool call failed with error: {}. Please apologize or retry with correct parameters.",
                            current_prompt, error_msg
                        );
                        println!("  Looping back to LLM with error feedback...");
                    }
                } else {
                    println!("  LLM attempted to call an unknown tool.");
                    break;
                }
            },
            Ok(None) => {
                println!("  LLM decided not to call any tools.");
                break;
            },
            Err(e) => {
                println!("  Provider Error: {}", e);
                break;
            },
        }
    }

    if attempt >= max_retries {
        println!("  Agent loop terminated after reaching max retries.");
    }
}

fn main() {
    println!("🚀 Starting ZeroClaw CLI Runtime (Air-Gapped LLM Vertical Slice)...\n");

    // 1. Initialize Backend Infrastructure
    println!("[1/5] Initializing durable memory backend...");
    let conn = Connection::open_in_memory().expect("Failed to open in-memory SQLite DB");
    let memory = SqliteMemory::new(conn).expect("Failed to initialize SqliteMemory");

    // 2. Load Tools
    println!("[2/5] Loading Solana plugin tools...");
    let risk_tool = SolanaRiskCheckTool::new();
    let transfer_tool = SolanaTransferTool::new();
    let process_payment_tool = ProcessPaymentTool::new("ledger.db");
    let tax_report_tool = GenerateTaxReportTool::new("ledger.db");
    
    let mut tool_registry: HashMap<String, Box<dyn Tool>> = HashMap::new();
    tool_registry.insert(risk_tool.name().to_string(), Box::new(risk_tool));
    tool_registry.insert(transfer_tool.name().to_string(), Box::new(transfer_tool));
    tool_registry.insert(process_payment_tool.name().to_string(), Box::new(process_payment_tool));
    tool_registry.insert(tax_report_tool.name().to_string(), Box::new(tax_report_tool));
    
    let available_tools: Vec<(&str, serde_json::Value)> = tool_registry.iter()
        .map(|(name, tool)| (name.as_str(), tool.parameters_schema()))
        .collect();

    // 3. Load Air-Gapped Llama.cpp Provider
    println!("[3/5] Loading Air-Gapped LLM Provider...");
    let provider = Box::new(LlamaCppProvider::new("C:/Users/plumb/models/llama3-8b.gguf").expect("Failed to init LlamaCppProvider"));

    // 4. Establish Session Context
    println!("[4/5] Loading Persistent Identity (Ed25519)...");
    
    let identity_file = ".zeroclaw_identity";
    let identity_key_bytes = if std::path::Path::new(identity_file).exists() {
        std::fs::read(identity_file).expect("Failed to read identity file")
    } else {
        use ed25519_dalek::SigningKey;
        use rand::rngs::OsRng;
        
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        let secret_bytes = signing_key.to_bytes().to_vec();
        
        std::fs::write(identity_file, &secret_bytes).expect("Failed to write identity file");
        println!("      Generated new Persistent Identity key and saved to {}", identity_file);
        secret_bytes
    };

    let ctx = ToolContext {
        identity_key_bytes,
    };

    // 5. Autonomous Executions with Agentic Loop
    println!("\n[5/5] Running Autonomous Agentic Loop...");

    let _simulation_prompts = vec![
        "Hey AI, I need a transaction but I forgot the token.",
        "Please send 50 tokens to address MockDestinationWallet1111111111111111111111.",
        "A customer just bought a T-Shirt for 25.5 solana from wallet CustomerWalletABCD. Please process the payment under Merchandise.",
        "Please generate my end-of-year tax report for 2026 so I can send it to the IRS."
    ];

    use std::io::{self, Write};
    println!("ZeroClaw Interactive Mode Started. Type 'exit' to quit.");
    
    let mut session_count = 1;
    loop {
        print!("\n[Session {}] USER> ", session_count);
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        let prompt = input.trim();

        if prompt.eq_ignore_ascii_case("exit") {
            break;
        }

        if prompt.is_empty() {
            continue;
        }

        run_agent_loop(
            prompt,
            provider.as_ref(),
            &tool_registry,
            &available_tools,
            &ctx,
            &memory
        );
        session_count += 1;
    }

    // 6. Dump Audit Trail
    println!("\n--- Dumping Cryptographic Audit Trail from Memory ---");
    let trail = memory.get_audit_trail().expect("Failed to fetch audit trail");
    
    for (i, (t_name, t_args, t_res)) in trail.iter().enumerate() {
        println!("  Execution #{}", i + 1);
        println!("  Tool: {}", t_name);
        println!("  Args: {}", t_args);
        println!("  Success: {}", t_res.success);
        
        if let Some(receipt) = &t_res.receipt {
            println!("  Receipt Signature (Ed25519): {}", receipt.signature);
            println!("  Timestamp: {}", receipt.timestamp);
        } else {
            println!("  Receipt: NONE");
        }
        println!();
    }

    println!("✅ Air-Gapped Vertical Slice completed successfully!");
}

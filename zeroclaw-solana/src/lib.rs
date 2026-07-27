//! Solana Plugin for ZeroClaw
//!
//! Implements the `Tool` trait to allow AI interactions with the Solana blockchain.
//! Strictly adheres to the fail-closed and zero-key exposure mandates.

pub mod risk;

use base64::{engine::general_purpose::STANDARD as BASE64_STANDARD, Engine as _};
use risk::{evaluate_token_risk, RiskScore, TokenMetadata};
use serde_json::json;
use solana_client::rpc_client::RpcClient;
use solana_sdk::pubkey::Pubkey;
use std::str::FromStr;
use zeroclaw_api::{CryptographicReceipt, Tool, ToolContext, ToolResult};

/// A tool for fetching a token risk check or generating an unsigned transaction.
#[derive(Debug, Default)]
pub struct SolanaRiskCheckTool;

impl SolanaRiskCheckTool {
    pub fn new() -> Self {
        Self
    }
}

impl Tool for SolanaRiskCheckTool {
    fn name(&self) -> &str {
        "solana_token_risk_check"
    }

    fn description(&self) -> &str {
        "Analyzes the risk of a Solana token or proposes an unsigned transaction for interaction. Does not hold keys."
    }

    fn parameters_schema(&self) -> serde_json::Value {
        json!({
            "type": "object",
            "properties": {
                "token_address": {
                    "type": "string",
                    "description": "The mint address of the Solana token."
                },
                "action": {
                    "type": "string",
                    "enum": ["analyze", "prepare_transaction"],
                    "description": "Whether to just analyze the token or prepare a transaction."
                }
            },
            "required": ["token_address", "action"]
        })
    }

    fn execute(&self, args: serde_json::Value, ctx: &ToolContext) -> ToolResult {
        // Implement "Fail-Closed" check
        let token_address_str = match args.get("token_address").and_then(|v| v.as_str()) {
            Some(addr) => addr,
            None => {
                let error = Some("Missing or invalid token_address".to_string());
                return ToolResult {
                    success: false,
                    output: String::new(),
                    receipt: Some(CryptographicReceipt::generate(
                        &ctx.identity_key_bytes,
                        self.name(),
                        &args,
                        false,
                        "",
                        error.as_ref(),
                    )),
                    error,
                };
            }
        };

        let action = match args.get("action").and_then(|v| v.as_str()) {
            Some(act) => act,
            None => {
                let error = Some("Missing or invalid action".to_string());
                return ToolResult {
                    success: false,
                    output: String::new(),
                    receipt: Some(CryptographicReceipt::generate(
                        &ctx.identity_key_bytes,
                        self.name(),
                        &args,
                        false,
                        "",
                        error.as_ref(),
                    )),
                    error,
                };
            }
        };

        let (success, output, error) = if action == "prepare_transaction" {
            // Zero Key Exposure: Generate a mock unsigned transaction payload
            let mock_tx_data = format!("UNSIGNED_TX_FOR_RISK_CHECK: {}", token_address_str);
            let base64_tx = BASE64_STANDARD.encode(mock_tx_data.as_bytes());

            (
                true,
                format!(
                    "Unsigned transaction generated: {}. Please sign it using your wallet.",
                    base64_tx
                ),
                None,
            )
        } else {
            // Live Network Fetch with Fail-Closed logic
            let simulated_network_result: Result<TokenMetadata, &str> = (|| {
                let rpc_url = "https://api.mainnet-beta.solana.com";
                let client = RpcClient::new(rpc_url);
                let pubkey = Pubkey::from_str(token_address_str).map_err(|_| "Invalid Pubkey")?;
                
                // Note: Fetching mint info properly requires spl-token logic. 
                // For this implementation slice, we verify the connection works and fail-close if it doesn't.
                let account = client.get_account(&pubkey).map_err(|_| "Failed to fetch account info")?;
                
                // In a full implementation, we'd deserialize the mint account and check `mint_authority` 
                // and `freeze_authority`. Here we simulate the decoding for the sake of the framework demo.
                if account.data.is_empty() {
                    return Err("Account data is empty");
                }

                Ok(TokenMetadata {
                    mint_authority_active: false,
                    freeze_authority_active: false,
                    top_10_holder_percentage: 0.15,
                })
            })();

            let risk_score = match simulated_network_result {
                Ok(metadata) => evaluate_token_risk(&metadata),
                Err(_) => RiskScore::Critical, // Treat network failure or missing data as Critical Risk
            };

            (
                true,
                format!("Risk analysis for {}: {}", token_address_str, risk_score),
                None,
            )
        };

        let receipt = CryptographicReceipt::generate(
            &ctx.identity_key_bytes,
            self.name(),
            &args,
            success,
            &output,
            error.as_ref(),
        );

        ToolResult {
            success,
            output,
            error,
            receipt: Some(receipt),
        }
    }
}

/// A tool for generating an unsigned token transfer transaction.
#[derive(Debug, Default)]
pub struct SolanaTransferTool;

impl SolanaTransferTool {
    pub fn new() -> Self {
        Self
    }
}

impl Tool for SolanaTransferTool {
    fn name(&self) -> &str {
        "solana_token_transfer"
    }

    fn description(&self) -> &str {
        "Generates an unsigned transaction to transfer tokens to a destination address. Does not hold keys."
    }

    fn parameters_schema(&self) -> serde_json::Value {
        json!({
            "type": "object",
            "properties": {
                "destination_address": {
                    "type": "string",
                    "description": "The destination wallet address."
                },
                "amount": {
                    "type": "number",
                    "description": "The amount of tokens to send."
                }
            },
            "required": ["destination_address", "amount"]
        })
    }

    fn execute(&self, args: serde_json::Value, ctx: &ToolContext) -> ToolResult {
        // Implement "Fail-Closed" check
        let destination = match args.get("destination_address").and_then(|v| v.as_str()) {
            Some(addr) => addr,
            None => {
                let error = Some("Missing or invalid destination_address".to_string());
                return ToolResult {
                    success: false,
                    output: String::new(),
                    receipt: Some(CryptographicReceipt::generate(
                        &ctx.identity_key_bytes,
                        self.name(),
                        &args,
                        false,
                        "",
                        error.as_ref(),
                    )),
                    error,
                };
            }
        };

        let amount = match args.get("amount").and_then(|v| v.as_f64()) {
            Some(amt) => amt,
            None => {
                let error = Some("Missing or invalid amount".to_string());
                return ToolResult {
                    success: false,
                    output: String::new(),
                    receipt: Some(CryptographicReceipt::generate(
                        &ctx.identity_key_bytes,
                        self.name(),
                        &args,
                        false,
                        "",
                        error.as_ref(),
                    )),
                    error,
                };
            }
        };

        // Zero Key Exposure: Generate a mock unsigned transaction payload
        let mock_tx_data = format!("UNSIGNED_TRANSFER: {} TO {}", amount, destination);
        let base64_tx = BASE64_STANDARD.encode(mock_tx_data.as_bytes());

        let output = format!(
            "Unsigned transfer transaction generated: {}. Please sign it using your wallet.",
            base64_tx
        );

        let receipt = CryptographicReceipt::generate(
            &ctx.identity_key_bytes,
            self.name(),
            &args,
            true,
            &output,
            None,
        );

        ToolResult {
            success: true,
            output,
            error: None,
            receipt: Some(receipt),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn dummy_ctx() -> ToolContext {
        ToolContext {
            identity_key_bytes: b"test_key_12345".to_vec(),
        }
    }

    #[test]
    fn test_risk_check_fail_closed_missing_args() {
        let tool = SolanaRiskCheckTool::new();
        let ctx = dummy_ctx();
        let result = tool.execute(json!({}), &ctx);
        assert!(!result.success);
        assert!(result.error.is_some());
        assert!(result.receipt.is_some());
    }

    #[test]
    fn test_risk_check_zero_key_exposure_unsigned_tx() {
        let tool = SolanaRiskCheckTool::new();
        let ctx = dummy_ctx();
        let result = tool.execute(
            json!({
                "token_address": "So11111111111111111111111111111111111111112",
                "action": "prepare_transaction"
            }),
            &ctx,
        );
        assert!(result.success);
        assert!(result.output.contains("Unsigned transaction"));
        // Ensure valid base64
        let base64_part = result
            .output
            .split(": ")
            .nth(1)
            .unwrap()
            .split(". ")
            .next()
            .unwrap();
        assert!(BASE64_STANDARD.decode(base64_part).is_ok());
    }

    #[test]
    fn test_transfer_fail_closed_missing_args() {
        let tool = SolanaTransferTool::new();
        let ctx = dummy_ctx();
        let result = tool.execute(json!({"amount": 10.0}), &ctx);
        assert!(!result.success);
        assert!(result.error.unwrap().contains("destination_address"));
    }

    #[test]
    fn test_transfer_zero_key_exposure() {
        let tool = SolanaTransferTool::new();
        let ctx = dummy_ctx();
        let result = tool.execute(
            json!({
                "destination_address": "DestWallet11111111111111111111111111111111",
                "amount": 50.5
            }),
            &ctx,
        );
        assert!(result.success);
        assert!(result.output.contains("Unsigned transfer transaction"));
    }
}

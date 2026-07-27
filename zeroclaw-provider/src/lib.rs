//! ZeroClaw Mock LLM Provider
//!
//! Provides a simple mock implementation of the `Provider` trait to prove
//! the autonomous framework flow without requiring external API keys.

use serde_json::json;
use zeroclaw_api::{Provider, ToolCall};

/// A mock LLM provider that uses basic keyword matching.
#[derive(Debug, Default)]
pub struct MockLlmProvider;

impl MockLlmProvider {
    pub fn new() -> Self {
        Self
    }
}

impl Provider for MockLlmProvider {
    fn generate_tool_call(
        &self,
        prompt: &str,
        available_tools: &[(&str, serde_json::Value)],
    ) -> Result<Option<ToolCall>, String> {
        let prompt_lower = prompt.to_lowercase();
        
        // Mock routing logic based on keywords
        
        // 1. Transfer Logic
        if prompt_lower.contains("send") || prompt_lower.contains("transfer") {
            let has_tool = available_tools.iter().any(|(name, _)| *name == "solana_token_transfer");
            if has_tool {
                // Mock extraction for "Send 50 tokens to address XYZ"
                let amount = if prompt_lower.contains("50") { 50.0 } else { 1.0 };
                let dest = "MockDestinationWallet1111111111111111111111";
                
                return Ok(Some(ToolCall {
                    tool_name: "solana_token_transfer".to_string(),
                    args: json!({
                        "destination_address": dest,
                        "amount": amount
                    })
                }));
            }
        }
        
        // 2. Risk Check / Transaction Prepare Logic
        if prompt_lower.contains("transaction") {
            let has_tool = available_tools.iter().any(|(name, _)| *name == "solana_token_risk_check");
            
            if has_tool {
                let token = prompt_lower.split_whitespace().find(|word| word.starts_with("so111"));
                
                if let Some(t) = token {
                    let normalized_token = if t.to_lowercase() == "so11111111111111111111111111111111111111112" {
                        "So11111111111111111111111111111111111111112"
                    } else {
                        t
                    };

                    return Ok(Some(ToolCall {
                        tool_name: "solana_token_risk_check".to_string(),
                        args: json!({
                            "token_address": normalized_token,
                            "action": "prepare_transaction"
                        })
                    }));
                } else {
                    return Ok(Some(ToolCall {
                        tool_name: "solana_token_risk_check".to_string(),
                        args: json!({
                            "action": "prepare_transaction"
                        })
                    }));
                }
            }
        }
        
        // If no keywords match, the LLM decides to not call any tools.
        Ok(None)
    }
}

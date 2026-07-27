//! ZeroClaw OpenAI Provider
//!
//! Provides a production-ready implementation of the `Provider` trait
//! using the OpenAI API.

use reqwest::blocking::Client;
use serde_json::{json, Value};
use std::env;
use zeroclaw_api::{Provider, ToolCall};

/// An LLM provider that uses the real OpenAI API.
pub struct OpenAiProvider {
    client: Client,
    api_key: String,
    model: String,
}

impl OpenAiProvider {
    /// Creates a new OpenAiProvider. Requires the OPENAI_API_KEY environment variable.
    pub fn new() -> Result<Self, String> {
        let api_key = env::var("OPENAI_API_KEY")
            .unwrap_or_else(|_| "DUMMY_KEY_FOR_TESTS".to_string());
            
        Ok(Self {
            client: Client::new(),
            api_key,
            model: "gpt-4o".to_string(), // Default model
        })
    }
}

impl Provider for OpenAiProvider {
    fn generate_tool_call(
        &self,
        prompt: &str,
        available_tools: &[(&str, Value)],
    ) -> Result<Option<ToolCall>, String> {
        if self.api_key == "DUMMY_KEY_FOR_TESTS" {
            // If the user hasn't set an API key, we return an error so the CLI can fallback
            return Err("OPENAI_API_KEY not set in environment.".to_string());
        }

        let mut openai_tools = Vec::new();
        for (name, schema) in available_tools {
            openai_tools.push(json!({
                "type": "function",
                "function": {
                    "name": name,
                    "description": format!("Call this tool to execute: {}", name),
                    "parameters": schema
                }
            }));
        }

        let body = json!({
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a ZeroClaw Agent. Call tools to assist the user."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "tools": openai_tools,
            "tool_choice": "auto"
        });

        let resp = self.client.post("https://api.openai.com/v1/chat/completions")
            .bearer_auth(&self.api_key)
            .json(&body)
            .send()
            .map_err(|e| format!("HTTP request failed: {}", e))?;

        if !resp.status().is_success() {
            return Err(format!("OpenAI API error: {}", resp.status()));
        }

        let json_resp: Value = resp.json().map_err(|e| format!("Failed to parse JSON: {}", e))?;
        
        // Extract tool calls from response
        if let Some(choices) = json_resp.get("choices").and_then(|c| c.as_array()) {
            if let Some(first_choice) = choices.get(0) {
                if let Some(message) = first_choice.get("message") {
                    if let Some(tool_calls) = message.get("tool_calls").and_then(|tc| tc.as_array()) {
                        if let Some(first_tool) = tool_calls.get(0) {
                            if let Some(function) = first_tool.get("function") {
                                let empty_json = json!("");
                                let tool_name = function.get("name").unwrap_or(&empty_json).as_str().unwrap_or("").to_string();
                                let args_str = function.get("arguments").unwrap_or(&empty_json).as_str().unwrap_or("{}");
                                let args: Value = serde_json::from_str(args_str).unwrap_or(json!({}));
                                
                                return Ok(Some(ToolCall {
                                    tool_name,
                                    args,
                                }));
                            }
                        }
                    }
                }
            }
        }

        Ok(None)
    }
}

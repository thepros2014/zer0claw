//! ZeroClaw Ollama Provider
//!
//! Provides a local, out-of-the-box implementation of the `Provider` trait
//! using Ollama's OpenAI-compatible API on localhost.

use reqwest::blocking::Client;
use serde_json::{json, Value};
use zeroclaw_api::{Provider, ToolCall};
use std::time::Duration;

/// An LLM provider that uses a local Ollama server.
pub struct OllamaProvider {
    client: Client,
    endpoint: String,
    model: String,
}

impl OllamaProvider {
    /// Creates a new OllamaProvider pointing to localhost:11434 by default.
    pub fn new() -> Result<Self, String> {
        let endpoint = "http://localhost:11434/v1/chat/completions".to_string();
        
        // Use a short timeout so the CLI gracefully falls back if Ollama isn't running
        let client = Client::builder()
            .timeout(Duration::from_secs(3))
            .build()
            .map_err(|e| format!("Failed to build reqwest client: {}", e))?;

        Ok(Self {
            client,
            endpoint,
            model: "llama3".to_string(), // Default Ollama model
        })
    }
}

impl Provider for OllamaProvider {
    fn generate_tool_call(
        &self,
        prompt: &str,
        available_tools: &[(&str, Value)],
    ) -> Result<Option<ToolCall>, String> {
        let mut ollama_tools = Vec::new();
        for (name, schema) in available_tools {
            ollama_tools.push(json!({
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
            "tools": ollama_tools,
            "tool_choice": "auto"
        });

        let resp = self.client.post(&self.endpoint)
            .json(&body)
            .send()
            .map_err(|e| format!("Connection to Ollama failed (Make sure `ollama serve` is running): {}", e))?;

        if !resp.status().is_success() {
            return Err(format!("Ollama API error: {}", resp.status()));
        }

        let json_resp: Value = resp.json().map_err(|e| format!("Failed to parse JSON: {}", e))?;
        
        // Extract tool calls from response (Ollama API matches OpenAI's format exactly here)
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

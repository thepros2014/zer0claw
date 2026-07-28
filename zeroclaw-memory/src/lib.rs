//! ZeroClaw Durable Memory Backend
//!
//! Provides a JSONL flat-file implementation of the `Memory` trait to ensure
//! complete auditability and transparency of the agent's actions within WASM.

use serde_json::json;
use std::fs::OpenOptions;
use std::io::{BufRead, BufReader, Write};
use std::sync::{Arc, Mutex};
use zeroclaw_api::{Memory, ToolResult};

/// A JSONL-backed implementation of the `Memory` trait.
pub struct FileMemory {
    file_path: Arc<Mutex<String>>,
}

impl FileMemory {
    /// Creates a new FileMemory instance using a flat file.
    pub fn new(path: &str) -> Result<Self, String> {
        let actual_path = if path.ends_with(".db") {
            path.replace(".db", ".jsonl")
        } else {
            path.to_string()
        };

        // Ensure file exists
        OpenOptions::new()
            .create(true)
            .append(true)
            .open(&actual_path)
            .map_err(|e| e.to_string())?;

        Ok(Self {
            file_path: Arc::new(Mutex::new(actual_path)),
        })
    }
}

impl Memory for FileMemory {
    fn log_tool_execution(
        &self,
        tool_name: &str,
        args: &serde_json::Value,
        result: &ToolResult,
    ) -> Result<(), String> {
        let path = self.file_path.lock().unwrap();

        let (signature, timestamp) = match &result.receipt {
            Some(receipt) => (Some(receipt.signature.clone()), Some(receipt.timestamp)),
            None => (None, None),
        };

        let record = json!({
            "tool_name": tool_name,
            "args": args.to_string(),
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "receipt_signature": signature,
            "receipt_timestamp": timestamp
        });

        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&*path)
            .map_err(|e| e.to_string())?;

        writeln!(file, "{}", record.to_string()).map_err(|e| e.to_string())?;

        Ok(())
    }

    fn get_audit_trail(&self) -> Result<Vec<(String, String, ToolResult)>, String> {
        let path = self.file_path.lock().unwrap();
        let file = std::fs::File::open(&*path).map_err(|e| e.to_string())?;
        let reader = BufReader::new(file);

        let mut results = Vec::new();

        for line in reader.lines().flatten() {
            if let Ok(record) = serde_json::from_str::<serde_json::Value>(&line) {
                let tool_name = record["tool_name"].as_str().unwrap_or("").to_string();
                let args_str = record["args"].as_str().unwrap_or("").to_string();
                let success = record["success"].as_bool().unwrap_or(false);
                let output = record["output"].as_str().unwrap_or("").to_string();
                let error = record["error"].as_str().map(|s| s.to_string());

                let signature = record["receipt_signature"].as_str().map(|s| s.to_string());
                let timestamp = record["receipt_timestamp"].as_u64();

                let receipt = match (signature, timestamp) {
                    (Some(sig), Some(ts)) => Some(zeroclaw_api::CryptographicReceipt {
                        signature: sig,
                        timestamp: ts,
                    }),
                    _ => None,
                };

                results.push((
                    tool_name,
                    args_str,
                    ToolResult {
                        success,
                        output,
                        error,
                        receipt,
                    },
                ));
            }
        }

        Ok(results)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::fs;
    use zeroclaw_api::CryptographicReceipt;

    #[test]
    fn test_file_memory_log_and_retrieve() {
        let path = "test_memory.jsonl";
        let _ = fs::remove_file(path); // clean start

        let memory = FileMemory::new(path).unwrap();

        let tool_name = "test_tool";
        let args = json!({"param": "value"});
        let result = ToolResult {
            success: true,
            output: "Success!".to_string(),
            error: None,
            receipt: Some(CryptographicReceipt {
                signature: "fake_digest_hex".to_string(),
                timestamp: 123456789,
            }),
        };

        // Log it
        memory
            .log_tool_execution(tool_name, &args, &result)
            .unwrap();

        // Retrieve it
        let trail = memory.get_audit_trail().unwrap();
        assert_eq!(trail.len(), 1);

        let (ret_name, ret_args, ret_result) = &trail[0];
        assert_eq!(ret_name, tool_name);
        assert_eq!(ret_args, &args.to_string());
        assert!(ret_result.success);
        assert_eq!(ret_result.output, "Success!");
        assert!(ret_result.receipt.is_some());

        let retrieved_receipt = ret_result.receipt.as_ref().unwrap();
        assert_eq!(retrieved_receipt.signature, "fake_digest_hex");
        assert_eq!(retrieved_receipt.timestamp, 123456789);

        let _ = fs::remove_file(path);
    }
}

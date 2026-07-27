//! ZeroClaw Durable Memory Backend
//!
//! Provides a SQLite implementation of the `Memory` trait to ensure
//! complete auditability and transparency of the agent's actions.

use rusqlite::{params, Connection};
use std::sync::{Arc, Mutex};
use zeroclaw_api::{Memory, ToolResult};

/// A SQLite-backed implementation of the `Memory` trait.
pub struct SqliteMemory {
    conn: Arc<Mutex<Connection>>,
}

impl SqliteMemory {
    /// Creates a new SqliteMemory instance using an in-memory database or a file.
    pub fn new(conn: Connection) -> Result<Self, rusqlite::Error> {
        let memory = Self {
            conn: Arc::new(Mutex::new(conn)),
        };
        memory.initialize()?;
        Ok(memory)
    }

    fn initialize(&self) -> Result<(), rusqlite::Error> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                args TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                output TEXT NOT NULL,
                error TEXT,
                receipt_digest TEXT,
                receipt_timestamp INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )",
            [],
        )?;
        Ok(())
    }
}

impl Memory for SqliteMemory {
    fn log_tool_execution(
        &self,
        tool_name: &str,
        args: &serde_json::Value,
        result: &ToolResult,
    ) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        
        let (digest, timestamp) = match &result.receipt {
            Some(receipt) => (Some(receipt.digest.clone()), Some(receipt.timestamp)),
            None => (None, None),
        };

        conn.execute(
            "INSERT INTO audit_log (
                tool_name, args, success, output, error, receipt_digest, receipt_timestamp
            ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![
                tool_name,
                args.to_string(),
                result.success,
                result.output,
                result.error,
                digest,
                timestamp,
            ],
        ).map_err(|e| e.to_string())?;

        Ok(())
    }

    fn get_audit_trail(&self) -> Result<Vec<(String, String, ToolResult)>, String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn
            .prepare("SELECT tool_name, args, success, output, error, receipt_digest, receipt_timestamp FROM audit_log ORDER BY id ASC")
            .map_err(|e| e.to_string())?;

        let iter = stmt.query_map([], |row| {
            let tool_name: String = row.get(0)?;
            let args_str: String = row.get(1)?;
            let success: bool = row.get(2)?;
            let output: String = row.get(3)?;
            let error: Option<String> = row.get(4)?;
            let receipt_digest: Option<String> = row.get(5)?;
            let receipt_timestamp: Option<u64> = row.get(6)?;

            let receipt = match (receipt_digest, receipt_timestamp) {
                (Some(digest), Some(timestamp)) => Some(zeroclaw_api::CryptographicReceipt {
                    digest,
                    timestamp,
                }),
                _ => None,
            };

            let tool_result = ToolResult {
                success,
                output,
                error,
                receipt,
            };

            Ok((tool_name, args_str, tool_result))
        }).map_err(|e| e.to_string())?;

        let mut results = Vec::new();
        for item in iter {
            results.push(item.map_err(|e| e.to_string())?);
        }

        Ok(results)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use zeroclaw_api::CryptographicReceipt;

    #[test]
    fn test_sqlite_memory_log_and_retrieve() {
        let conn = Connection::open_in_memory().unwrap();
        let memory = SqliteMemory::new(conn).unwrap();

        let tool_name = "test_tool";
        let args = json!({"param": "value"});
        let result = ToolResult {
            success: true,
            output: "Success!".to_string(),
            error: None,
            receipt: Some(CryptographicReceipt {
                digest: "fake_digest_hex".to_string(),
                timestamp: 123456789,
            }),
        };

        // Log it
        memory.log_tool_execution(tool_name, &args, &result).unwrap();

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
        assert_eq!(retrieved_receipt.digest, "fake_digest_hex");
        assert_eq!(retrieved_receipt.timestamp, 123456789);
    }
}

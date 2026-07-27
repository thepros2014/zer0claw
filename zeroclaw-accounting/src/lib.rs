use rusqlite::Connection;
use serde_json::{json, Value};
use std::time::{SystemTime, UNIX_EPOCH};
use zeroclaw_api::{CryptographicReceipt, Tool, ToolContext, ToolResult};

/// Tool to process a payment and record it as a taxable event in the SQLite ledger.
pub struct ProcessPaymentTool {
    db_path: String,
}

impl ProcessPaymentTool {
    pub fn new(db_path: &str) -> Self {
        // Initialize the tax ledger table if it doesn't exist
        let conn = Connection::open(db_path).unwrap();
        conn.execute(
            "CREATE TABLE IF NOT EXISTS taxable_events (
                id INTEGER PRIMARY KEY,
                timestamp INTEGER NOT NULL,
                wallet_address TEXT NOT NULL,
                amount_usd REAL NOT NULL,
                tax_category TEXT NOT NULL,
                receipt_digest TEXT NOT NULL
            )",
            [],
        ).unwrap();

        Self {
            db_path: db_path.to_string(),
        }
    }

    fn fail(&self, msg: String, args: &Value, ctx: &ToolContext) -> ToolResult {
        let error = Some(msg);
        let receipt = CryptographicReceipt::generate(&ctx.ephemeral_session_key, self.name(), args, false, "", error.as_ref());
        ToolResult { success: false, output: String::new(), error, receipt: Some(receipt) }
    }
}

impl Tool for ProcessPaymentTool {
    fn name(&self) -> &str {
        "solana_process_payment"
    }

    fn description(&self) -> &str {
        "Process an incoming Solana payment and automatically record the income for tax accounting."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "wallet_address": {
                    "type": "string",
                    "description": "The Solana wallet address making the payment"
                },
                "amount_usd": {
                    "type": "number",
                    "description": "The equivalent USD amount of the payment"
                },
                "tax_category": {
                    "type": "string",
                    "enum": ["Service Revenue", "Merchandise", "Donation", "Capital Gain"],
                    "description": "The IRS tax category for this payment"
                }
            },
            "required": ["wallet_address", "amount_usd", "tax_category"]
        })
    }

    fn execute(&self, args: Value, ctx: &ToolContext) -> ToolResult {
        let wallet = match args.get("wallet_address").and_then(|v| v.as_str()) {
            Some(w) => w.to_string(),
            None => return self.fail("Missing or invalid wallet_address".to_string(), &args, ctx),
        };

        let amount = match args.get("amount_usd").and_then(|v| v.as_f64()) {
            Some(a) if a > 0.0 => a,
            _ => return self.fail("Amount must be greater than 0".to_string(), &args, ctx),
        };

        let category = match args.get("tax_category").and_then(|v| v.as_str()) {
            Some(c) => c.to_string(),
            None => return self.fail("Missing tax_category".to_string(), &args, ctx),
        };

        let output = format!("Payment of ${} processed and securely logged to tax ledger under category: {}", amount, category);
        let receipt = CryptographicReceipt::generate(&ctx.ephemeral_session_key, self.name(), &args, true, &output, None);
        let receipt_digest = receipt.digest.clone();
        
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

        let conn = Connection::open(&self.db_path).unwrap();
        conn.execute(
            "INSERT INTO taxable_events (timestamp, wallet_address, amount_usd, tax_category, receipt_digest)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![timestamp, wallet, amount, category, receipt_digest],
        ).unwrap();

        ToolResult {
            success: true,
            output,
            error: None,
            receipt: Some(receipt),
        }
    }
}

/// Tool to generate an IRS-ready CSV report from the SQLite ledger.
pub struct GenerateTaxReportTool {
    db_path: String,
}

impl GenerateTaxReportTool {
    pub fn new(db_path: &str) -> Self {
        Self {
            db_path: db_path.to_string(),
        }
    }

    fn fail(&self, msg: String, args: &Value, ctx: &ToolContext) -> ToolResult {
        let error = Some(msg);
        let receipt = CryptographicReceipt::generate(&ctx.ephemeral_session_key, self.name(), args, false, "", error.as_ref());
        ToolResult { success: false, output: String::new(), error, receipt: Some(receipt) }
    }
}

impl Tool for GenerateTaxReportTool {
    fn name(&self) -> &str {
        "generate_tax_report"
    }

    fn description(&self) -> &str {
        "Aggregates all taxable events from the database and generates an IRS-ready CSV report."
    }

    fn parameters_schema(&self) -> Value {
        json!({
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "The tax year to generate the report for"
                }
            },
            "required": ["year"]
        })
    }

    fn execute(&self, args: Value, ctx: &ToolContext) -> ToolResult {
        let year = match args.get("year").and_then(|v| v.as_i64()) {
            Some(y) => y,
            None => return self.fail("Missing tax year".to_string(), &args, ctx),
        };

        let conn = Connection::open(&self.db_path).unwrap();
        let mut stmt = conn.prepare("SELECT timestamp, wallet_address, amount_usd, tax_category, receipt_digest FROM taxable_events").unwrap();
        
        let event_iter = stmt.query_map([], |row| {
            Ok((
                row.get::<_, i64>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, f64>(2)?,
                row.get::<_, String>(3)?,
                row.get::<_, String>(4)?,
            ))
        }).unwrap();

        let filename = format!("tax_report_{}.csv", year);
        let mut wtr = csv::Writer::from_path(&filename).unwrap();
        wtr.write_record(&["Timestamp", "Wallet Address", "Amount (USD)", "Tax Category", "Cryptographic Receipt Hash"]).unwrap();

        let mut total_revenue = 0.0;
        let mut count = 0;

        for event in event_iter {
            let (ts, wallet, amount, category, hash) = event.unwrap();
            total_revenue += amount;
            count += 1;
            wtr.write_record(&[
                ts.to_string(),
                wallet,
                format!("{:.2}", amount),
                category,
                hash
            ]).unwrap();
        }
        wtr.flush().unwrap();

        let output = format!("Successfully aggregated {} taxable events. Total Revenue: ${:.2}. Report saved to '{}'.", count, total_revenue, filename);
        let receipt = CryptographicReceipt::generate(&ctx.ephemeral_session_key, self.name(), &args, true, &output, None);

        ToolResult {
            success: true,
            output,
            error: None,
            receipt: Some(receipt),
        }
    }
}

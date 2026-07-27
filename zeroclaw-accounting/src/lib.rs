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
                receipt_signature TEXT NOT NULL
            )",
            [],
        ).unwrap();

        Self {
            db_path: db_path.to_string(),
        }
    }

    fn fail(&self, msg: String, args: &Value, ctx: &ToolContext) -> ToolResult {
        let error = Some(msg);
        let receipt = CryptographicReceipt::generate(&ctx.identity_key_bytes, self.name(), args, false, "", error.as_ref());
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
                "crypto_symbol": {
                    "type": "string",
                    "enum": ["solana", "usd-coin"],
                    "description": "The CoinGecko ID for the cryptocurrency (e.g., 'solana', 'usd-coin')"
                },
                "amount_crypto": {
                    "type": "number",
                    "description": "The amount of crypto paid"
                },
                "tax_category": {
                    "type": "string",
                    "enum": ["Service Revenue", "Merchandise", "Donation", "Capital Gain"],
                    "description": "The IRS tax category for this payment"
                }
            },
            "required": ["wallet_address", "crypto_symbol", "amount_crypto", "tax_category"]
        })
    }

    fn execute(&self, args: Value, ctx: &ToolContext) -> ToolResult {
        let wallet = match args.get("wallet_address").and_then(|v| v.as_str()) {
            Some(w) => w.to_string(),
            None => return self.fail("Missing or invalid wallet_address".to_string(), &args, ctx),
        };

        let crypto_amount = match args.get("amount_crypto").and_then(|v| v.as_f64()) {
            Some(a) if a > 0.0 => a,
            _ => return self.fail("Amount must be greater than 0".to_string(), &args, ctx),
        };

        let crypto_id = match args.get("crypto_symbol").and_then(|v| v.as_str()) {
            Some(c) => c.to_string(),
            None => return self.fail("Missing crypto_symbol".to_string(), &args, ctx),
        };

        let category = match args.get("tax_category").and_then(|v| v.as_str()) {
            Some(c) => c.to_string(),
            None => return self.fail("Missing tax_category".to_string(), &args, ctx),
        };

        // Live USD Conversion via CoinGecko
        let url = format!("https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd", crypto_id);
        let resp = match reqwest::blocking::get(&url) {
            Ok(r) => r,
            Err(_) => return self.fail("Failed to fetch live price data from CoinGecko API".to_string(), &args, ctx),
        };

        let price_json: Value = match resp.json() {
            Ok(j) => j,
            Err(_) => return self.fail("Failed to parse live price data".to_string(), &args, ctx),
        };

        let price_usd = match price_json.get(&crypto_id).and_then(|obj| obj.get("usd")).and_then(|usd| usd.as_f64()) {
            Some(p) => p,
            None => return self.fail("Could not determine live USD price for crypto".to_string(), &args, ctx),
        };

        let amount_usd = crypto_amount * price_usd;

        let output = format!("Payment of {} {} processed at ${:.2}/each and securely logged to tax ledger under category: {} (Total: ${:.2} USD)", crypto_amount, crypto_id, price_usd, category, amount_usd);
        let receipt = CryptographicReceipt::generate(&ctx.identity_key_bytes, self.name(), &args, true, &output, None);
        let receipt_signature = receipt.signature.clone();
        
        let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();

        let conn = Connection::open(&self.db_path).unwrap();
        conn.execute(
            "INSERT INTO taxable_events (timestamp, wallet_address, amount_usd, tax_category, receipt_signature)
             VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![timestamp, wallet, amount_usd, category, receipt_signature],
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
        let receipt = CryptographicReceipt::generate(&ctx.identity_key_bytes, self.name(), args, false, "", error.as_ref());
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
        let mut stmt = conn.prepare("SELECT timestamp, wallet_address, amount_usd, tax_category, receipt_signature FROM taxable_events").unwrap();
        
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
        let receipt = CryptographicReceipt::generate(&ctx.identity_key_bytes, self.name(), &args, true, &output, None);

        ToolResult {
            success: true,
            output,
            error: None,
            receipt: Some(receipt),
        }
    }
}

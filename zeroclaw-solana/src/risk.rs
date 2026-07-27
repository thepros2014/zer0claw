//! Zero-Trust pure-function risk engine for token analysis.
//!
//! This module handles the core mathematical evaluation of token risk,
//! divorced from any IO or network dependencies.

use std::fmt;

/// Represents the on-chain metadata state of a Solana token.
#[derive(Debug, Clone, PartialEq)]
pub struct TokenMetadata {
    pub mint_authority_active: bool,
    pub freeze_authority_active: bool,
    pub top_10_holder_percentage: f64,
}

/// The output of the risk evaluation engine.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RiskScore {
    Low,
    Medium,
    High,
    Critical,
}

impl fmt::Display for RiskScore {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            RiskScore::Low => write!(f, "LOW RISK"),
            RiskScore::Medium => write!(f, "MEDIUM RISK"),
            RiskScore::High => write!(f, "HIGH RISK"),
            RiskScore::Critical => write!(f, "CRITICAL RISK"),
        }
    }
}

/// Pure function to evaluate the risk of a token based on its on-chain metadata.
///
/// # Rules:
/// - Active Freeze Authority = Critical Risk
/// - Active Mint Authority = High Risk
/// - Top 10 holders control > 50% = High Risk
/// - Top 10 holders control > 20% = Medium Risk
/// - Otherwise = Low Risk
pub fn evaluate_token_risk(metadata: &TokenMetadata) -> RiskScore {
    if metadata.freeze_authority_active {
        return RiskScore::Critical;
    }

    if metadata.mint_authority_active || metadata.top_10_holder_percentage > 0.50 {
        return RiskScore::High;
    }

    if metadata.top_10_holder_percentage > 0.20 {
        return RiskScore::Medium;
    }

    RiskScore::Low
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_safe_pattern() {
        let meta = TokenMetadata {
            mint_authority_active: false,
            freeze_authority_active: false,
            top_10_holder_percentage: 0.15,
        };
        assert_eq!(evaluate_token_risk(&meta), RiskScore::Low);
    }

    #[test]
    fn test_malicious_freeze() {
        let meta = TokenMetadata {
            mint_authority_active: false,
            freeze_authority_active: true,
            top_10_holder_percentage: 0.05,
        };
        assert_eq!(evaluate_token_risk(&meta), RiskScore::Critical);
    }

    #[test]
    fn test_rug_pull_mint() {
        let meta = TokenMetadata {
            mint_authority_active: true,
            freeze_authority_active: false,
            top_10_holder_percentage: 0.10,
        };
        assert_eq!(evaluate_token_risk(&meta), RiskScore::High);
    }

    #[test]
    fn test_rug_pull_concentration() {
        let meta = TokenMetadata {
            mint_authority_active: false,
            freeze_authority_active: false,
            top_10_holder_percentage: 0.85,
        };
        assert_eq!(evaluate_token_risk(&meta), RiskScore::High);
    }

    #[test]
    fn test_medium_concentration() {
        let meta = TokenMetadata {
            mint_authority_active: false,
            freeze_authority_active: false,
            top_10_holder_percentage: 0.25,
        };
        assert_eq!(evaluate_token_risk(&meta), RiskScore::Medium);
    }
}

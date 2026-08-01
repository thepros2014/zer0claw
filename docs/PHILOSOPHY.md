# ZeroClaw Solana Plugin: Architectural Philosophy

Welcome to the ZeroClaw Solana Plugin project. This document outlines the fundamental principles that govern our design and implementation. If a proposed design conflicts with these rules, the design must be revised.

## 1. Local-First and Zero Overhead
- **100% Rust:** The framework and plugins are built exclusively in Rust for safety and performance.
- **Ultra-Lightweight:** Target minimal RAM footprint (< 5MB) and ultra-fast cold starts (< 10ms) for edge deployment.

## 2. Fail-Closed Security Mandate
Because AI agents interacting with financial systems introduce massive risks, our system **cannot assume execution is allowed by default**.
- **Explicit Authorization:** Execution is categorically denied unless authorization conditions, policies, and identities are explicitly verified.
- **Infrastructure over LLM:** The AI model's judgment is not a security boundary. Infrastructure-level controls block unauthorized actions to protect against prompt injection and hallucinations.
- **Clear Error Feedback:** Blocked commands must return explicit errors to the LLM to allow for recovery, retry, or escalation.

## 3. Zero Key Exposure
- The agent must **never** hold a user's private keys.
- Any tool invocation requiring an on-chain transaction must generate and return an **unsigned transaction** (e.g., base64 serialized transaction) that a human user or external signer can review and approve.

## 4. Cryptographic Transparency and Auditability
- **Cryptographic Receipts:** Every tool invocation must generate a cryptographic receipt (HMAC-SHA256 digest) combining the ephemeral session key, tool name, arguments, result, and timestamp.
- **Immutable Audit Log:** Conversations, tool calls, and receipts are recorded to a durable memory backend (e.g., embedded SQLite) ensuring complete transparency.

## 5. Trait-Driven Architecture
- Utilize a microkernel architecture where subsystems (Providers, Channels, Tools, Memory) are defined by strict trait interfaces.

***
*Adhere strictly to these rules to build robust infrastructure for agentic commerce.*

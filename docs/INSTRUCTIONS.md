# ZeroClaw Agentic Framework: Setup Instructions

Welcome to the ZeroClaw repository! This guide will show you how to compile and run the local, secure, fail-closed Solana AI agent framework.

## Prerequisites
1. **Rust & Cargo:** You must have the Rust toolchain installed. If you don't, install it from [rustup.rs](https://rustup.rs/).
2. **Python:** Required only if you want to use the included script to robustly download the Air-Gapped Llama.cpp model.

---

## Running the Framework

The framework is hosted by the `zeroclaw-cli` crate. By default, it is configured to use the **Air-Gapped Llama.cpp Provider**, but it gracefully falls back to the **MockLlmProvider** if you haven't downloaded the massive 4.9 GB model file.

### Option 1: The Fast Mock Simulation (Recommended for Testing)
To instantly see the framework's architecture, fail-closed boundaries, and cryptographic SQLite receipts in action without downloading huge AI models:

```bash
cargo run -p zeroclaw-cli
```
*If it doesn't find the real Llama weights on your hard drive, it will fall back to a mock simulation and run perfectly.*

### Option 2: The Ultimate Air-Gapped Setup (Real AI)
To run the framework exactly as intended—completely off-grid with zero network sockets using a real AI model:

**Step 1: Download the Model**
We have included a robust python script to download the optimized `Llama-3.1-8B-Instruct-Q4_K_M.gguf` file directly from HuggingFace to your `C:\Users\plumb\models` directory. Make sure you have at least 5 GB of free space!

```bash
pip install huggingface_hub
python download_model.py
```

**Step 2: Run the Air-Gapped CLI**
Once the download is complete, run the CLI. It will detect the `.gguf` file, load it directly into RAM, and execute the autonomous loop locally.

```bash
cargo run -p zeroclaw-cli
```

### Option 3: The Ollama Setup (Fast Real AI)
If you already have [Ollama](https://ollama.com/) installed and running locally, you can modify `zeroclaw-cli/src/main.rs` to load the `OllamaProvider` instead of the `LlamaCppProvider`.

1. Start your local Ollama server: `ollama run llama3.1`
2. Run the CLI: `cargo run -p zeroclaw-cli`

---

## Project Structure
- `zeroclaw-api/`: Contains the rigid `Tool`, `Provider`, and `Memory` kernel traits.
- `zeroclaw-cli/`: The host runtime executing the autonomous Agentic Loop.
- `zeroclaw-memory/`: The SQLite backend managing the HMAC-SHA256 cryptographic audit logs.
- `zeroclaw-solana/`: The core plugin containing fail-closed Solana Risk Check and Transfer tools.
- `zeroclaw-openai/`: A cloud-based LLM provider implementation.
- `zeroclaw-ollama/`: A local-network LLM provider implementation.
- `zeroclaw-llamacpp/`: The Air-Gapped LLM provider implementation.

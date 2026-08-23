# 🛋️ Demo Shopper Agent (HomeStyle Furnishings)

A lightweight, open-source conversational shopping assistant agent with tool calling and zero heavy ML dependencies.

Built for seamless developer onboarding, instant multi-turn testing, and agent evaluations with [Halios](https://halios.ai).

---

## ✨ Features

- **⚡ Zero Heavy ML Dependencies**: Replaces multi-gigabyte vector databases (like ChromaDB/PyTorch) with an ultra-fast, pure-Python in-memory search engine (<2ms latency over 800+ products).
- **📂 Clean CSV Product Catalog**: All products are stored in a human-readable, transparent [`products.csv`](products.csv) file that can be easily edited or swapped with your own data.
- **🛡️ Brand-Neutral & Sanitized**: Free of proprietary brand names, raw SKUs, and scraper noise.
- **🔌 Multi-LLM Provider Support**:
  - **Google Gemini** (default: `gemini-2.5-flash-lite`)
  - **OpenAI** (e.g. `gpt-4.1-mini`)
  - **Ollama / Local LLMs** (e.g. `gemma4`, `llama3`)
  - **Custom OpenAI-compatible endpoints**
- **🛠️ Standardized Function Calling**: Implements tool calling for customer verification, contact validation, session management, and catalog search.

---

## 🚀 Quickstart

### 1. Clone & Setup Environment

```bash
cd halios_opensource/demo_shopper_agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (takes ~5 seconds)
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Agent

```bash
python agent.py
```

Or run with specific providers and models:

```bash
# Using Google Gemini
python agent.py --provider gemini --model gemini-2.5-flash-lite

# Using OpenAI
python agent.py --provider openai --model gpt-4.1-mini

# Using Local Ollama
python agent.py --provider ollama --model gemma4:latest
```

---

## 📁 Repository Structure

```
demo_shopper_agent/
├── agent.py                 # Interactive shopping assistant CLI and agent runner
├── search_engine.py         # Pure-Python BM25 + keyword relevance search engine
├── products.csv             # Sanitized ~830+ furniture & home decor catalog
├── prompt.md                # System instructions & business logic rules
├── export_sanitized_csv.py  # Data extraction & sanitization script
├── requirements.txt         # Lightweight dependencies (openai, python-dotenv)
├── .env.example             # Environment variable template
└── README.md                # Project documentation
```

---

## 🔍 Customizing the Product Catalog

To use your own product catalog, simply replace [`products.csv`](products.csv) with your own CSV file matching these column headers:

| Column | Description | Example |
| :--- | :--- | :--- |
| `product_id` | Unique identifier | `prod_0001` |
| `product_name` | Title of the product | `Simon Club Chair Black` |
| `category` | Comma-separated categories | `Furniture, Upholstery, Living Room` |
| `description` | Full product description | `Retro-modern chair with durable faux leather...` |
| `wood_finish` | Wood finish / color (optional) | `Black` |
| `material` | Material composition | `Vinyl / Polyurethane (Faux Leather)` |
| `product_link` | URL to product details page | `https://example.com/products/simon-club-chair-black` |

---

## 🧪 Testing with Halios

This agent can be directly evaluated and tested using **Halios AI Agent Evaluation Harness**:

```bash
# Example evaluation simulation
python run_eval_simulation.py
```

---

## 📄 License

MIT License. Free to use and modify for demos, evaluations, and production agent workflows.

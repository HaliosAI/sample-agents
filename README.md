# 🤖 HaliosAI Sample Agents

A curated collection of production-grade, open-source sample agents designed for benchmarking, multi-turn testing, and evaluation with [Halios](https://halios.ai).

Each sample agent in this repository is self-contained, brand-sanitized, and comes with zero-friction setup instructions, mock business tools, and reproducible datasets.

---

## 📂 Available Agents

| Agent | Category | Description | Search / Data Backend | Quickstart |
| :--- | :--- | :--- | :--- | :--- |
| [**`demo-shopper-agent`**](./demo-shopper-agent) | E-commerce / Sales | Conversational furniture sales assistant with tool calling for customer verification, session tracking, and catalog search. | In-memory BM25 over sanitized `products.csv` | [`demo-shopper-agent/README.md`](./demo-shopper-agent/README.md) |

---

## 🚀 General Quickstart

Navigate to any agent subdirectory to get started:

```bash
cd demo-shopper-agent

# Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env

# Run the agent
python agent.py
```

---

## 🧪 Evaluating Agents with Halios

All sample agents in this repository can be instrumented and evaluated using the **Halios SDK** and **Halios Agent Evaluation Harness**:

* Multi-turn conversational simulation
* Business rule adherence and guardrail verification
* Tool calling accuracy and session lifecycle validation
* Latency, cost, and hallucination metrics

---

## 📄 License

MIT License. Free to use, adapt, and benchmark.

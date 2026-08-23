# 🤖 HaliosAI Sample Agents

A curated collection of production-grade, open-source sample agents designed for benchmarking, multi-turn testing, and evaluation with [Halios](https://halios.ai).

Each sample agent in this repository is self-contained and comes with complete setup instructions, mock business tools, and reproducible datasets.

---

## 📂 Available Agents

| Agent | Category | Description | Data Backend | Quickstart |
| :--- | :--- | :--- | :--- | :--- |
| [**`demo-shopper-agent`**](./demo-shopper-agent) | E-commerce / Sales | Conversational furniture sales assistant with tool calling for customer verification, session tracking, and catalog search. | In-memory BM25 over `products.csv` | [`demo-shopper-agent/README.md`](./demo-shopper-agent/README.md) |

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

## 🧪 Get Started with Agent Evaluation

Evaluate any sample agent in this repository using **Halios**:

1. **Clone this repository / agent folder** to your workspace.
2. **Open the agent in your AI coding agent** (Claude Code, Cursor, Copilot, Antigravity, etc.) and paste this prompt:
   ```text
   Run npx skills add HaliosAI/halios --skill halios, then use the Halios skill to set up evals for this agent.
   ```
3. **Learn about evaluation concepts**: [Halios Evaluation Concepts](https://docs.halios.ai/concepts/evaluation-concepts)
4. **Prompting & Eval Cookbook**: Explore what you can test and build with the [Halios Prompting Guide & Cookbook](https://docs.halios.ai/prompts/prompting-guide).
5. **Evaluation Scenarios & Checks**: Learn how to design multi-turn simulation scenarios and rubric checks: [Halios Evaluation Types](https://docs.halios.ai/evaluation/eval-types).
6. **Further Reading**: [Demystifying Evals for AI Agents (Anthropic Engineering)](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

---

## 📄 License

MIT License. Free to use, adapt, and benchmark.

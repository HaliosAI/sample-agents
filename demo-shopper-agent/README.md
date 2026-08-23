# 🛋️ Demo Shopper Agent

A multi-turn conversational shopping and product recommendation assistant built with function calling and lightweight in-memory catalog search.

This sample agent serves as a reference application for building and evaluating customer-facing sales agents with [Halios](https://halios.ai).

---

## 🎯 What This Agent Does

The Demo Shopper Agent acts as "Sarah", an online shopping specialist for HomeStyle Furnishings. It handles realistic, multi-turn sales and support workflows:

* **Customer Identification & Onboarding**: Guides customers through a friendly intake flow, verifying user details and initiating secure shopping sessions.
* **Intelligent Product Search**: Interprets natural language requests and queries an internal catalog of 800+ home furniture items.
* **Business Rule Enforcement**: Applies strict domain guidelines (e.g., distinguishing indoor vs outdoor sets, offering leather alternatives, handling competitor inquiries, filtering requested colors).
* **Tool Calling**: Calls tools to verify customer records, validate emails/phones, dispatch confirmation emails/SMS, and manage session lifecycles.

---

## 🔌 Supported LLM Providers

The agent connects to any OpenAI-compatible completions endpoint:

* **Google Gemini** (default: `gemini-2.5-flash-lite`)
* **OpenAI** (e.g. `gpt-4.1-mini`, `gpt-4o`)
* **Local Ollama** (e.g. `gemma4`, `llama3`)
* **Custom Endpoints** (vLLM, LiteLLM, Groq, etc.)

---

## 🚀 Quickstart

### 1. Setup Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set the required environment variables:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | Active LLM provider (`gemini`, `openai`, `ollama`, `custom`) | `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key (required if using Gemini) | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model ID | `gemini-2.5-flash-lite` |
| `OPENAI_API_KEY` | OpenAI API key (required if using OpenAI) | `sk-...` |
| `OPENAI_MODEL` | OpenAI model ID | `gpt-4.1-mini` |
| `OLLAMA_BASE_URL` | Base URL for local Ollama server | `http://localhost:11434/v1/` |
| `OLLAMA_MODEL` | Ollama model tag | `gemma4:latest` |

### 3. Run the Agent

```bash
# Run with default provider (Gemini)
python agent.py

# Or pass CLI overrides
python agent.py --provider openai --model gpt-4.1-mini
python agent.py --provider ollama --model gemma4:latest
```

---

## 📁 Repository Structure

```
demo-shopper-agent/
├── agent.py          # Interactive CLI and multi-turn agent runner
├── search_engine.py  # In-memory BM25 product catalog search
├── products.csv      # Home furniture product catalog (800+ items)
├── prompt.md         # System instructions, behavior tree, and business rules
├── requirements.txt  # Project dependencies (openai, python-dotenv)
├── .env.example      # Environment variable template
├── .gitignore        # Git ignore rules
└── README.md         # Documentation
```

---

## 🧪 Get Started with Agent Evaluation

Evaluate this agent's reliability, tool-calling precision, and guardrails using **Halios**:

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

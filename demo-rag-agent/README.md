# 📚 Demo Document Research & QA RAG Agent

A lightweight, production-grade **Knowledge Base RAG Agent** built for evaluating hybrid retrieval quality, citation attribution, needle-in-a-haystack recall, and temporal policy conflict resolution.

This sample agent serves as a reference application for building and evaluating grounded document QA agents with [Halios](https://halios.ai).

---

## 🎯 What This Agent Does

The Demo RAG Agent acts as a grounded Document Research & QA assistant. It handles realistic document search and question answering workflows:

* **Hybrid Retrieval (Semantic Vector + BM25 Keyword)**: Combines dense embeddings with BM25 sparse matching via Reciprocal Rank Fusion (RRF) for high-precision document chunk retrieval.
* **Tool Calling Architecture**: Leverages `retrieve_documents` and `get_full_document` tools to retrieve relevant sections or full documentation on demand.
* **Strict Grounding & Citation Attribution**: System prompt mandates `[Doc: <doc_id>, Section: <section_title>]` citations for every factual statement.
* **Honest Refusal Guardrails**: Gracefully refuses out-of-domain queries without hallucinating.
* **Policy Conflict Resolution**: Correctly distinguishes active policies from superseded historical versions (e.g. Refund Policy v2 vs v1).
* **Built-in Benchmark Suites**:
  - **Needle In A Haystack (NIAH)**: Synthetic needle injection at depths 10%, 50%, and 90% in distractor text.
  - **Grounded QA & Citation Evaluator**: Tests factual recall, citation presence, honest refusal, and policy conflict resolution.

---

## 🔌 Supported LLM Providers

The agent connects to any OpenAI-compatible endpoint:

* **OpenAI** (e.g. `gpt-4o-mini`, `gpt-4o`)
* **OpenRouter** / **Together** / **Groq**
* **Local Ollama** (with automatic TF-IDF fallback when embeddings endpoint is unavailable)

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

Set your API keys:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI or compatible API key | `your_api_key_here` |
| `OPENAI_MODEL` | Chat model ID | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model ID | `text-embedding-3-small` |
| `OPENAI_BASE_URL` | *(Optional)* Custom endpoint URL | `https://openrouter.ai/api/v1` |

### 3. Run Interactive RAG Chat

```bash
python agent.py
```

---

## 🧪 Running Built-in Benchmarks

### 1. Needle In A Haystack (NIAH)
Tests if the agent retrieves and extracts secret codes injected at 10%, 50%, and 90% depth:
```bash
python benchmarks/niah_runner.py
```

### 2. Grounded QA & Citation Attribution
Evaluates fact recall, citation presence, honest refusal, and policy conflict resolution:
```bash
python benchmarks/qa_evaluator.py
```

---

## 📁 Repository Structure

```
demo-rag-agent/
├── agent.py            # Main RAG Agent with function calling
├── rag_engine.py       # Hybrid retrieval engine (Vector + BM25 with RRF)
├── prompt.md           # Grounded system prompt (citations & anti-hallucination)
├── corpus/             # Sample knowledge documentation
│   ├── cloud_architecture.md
│   ├── security_compliance.md
│   ├── refund_policy_v1.md
│   └── refund_policy_v2_updated.md
├── benchmarks/         # Built-in benchmark runners
│   ├── niah_runner.py  # Needle In A Haystack benchmark runner
│   └── qa_evaluator.py # Grounded QA & citation evaluator
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore          # Git ignore rules
└── README.md           # Documentation
```

---

## 🧪 Get Started with Agent Evaluation

Evaluate this agent's retrieval accuracy, faithfulness, and citation adherence using **Halios**:

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

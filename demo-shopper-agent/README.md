# 🛋️ Demo Shopper Agent

A conversational shopping and product recommendation agent built with function calling and lightweight in-memory catalog search.

Use it to try Halios against an agent with customer verification, business rules, catalog search, and multi-step tool use.

## What the agent does

The agent acts as **Sarah**, a shopping specialist for HomeStyle Furnishings.

- **Customer verification** — identifies customers and starts shopping sessions.
- **Catalog search** — searches a catalog of 800+ furniture products from natural-language requests.
- **Business rules** — handles product constraints such as indoor vs. outdoor furniture, requested colors, alternatives, and competitor questions.
- **Tool use** — verifies customer data, searches products, sends confirmations, and manages session state.

## Model providers

The sample can run with Gemini, OpenAI, Ollama, or another OpenAI-compatible endpoint.

Gemini is configured as the default.

## Run the agent

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Configure one of the supported model providers in `.env`, then run:

```bash
python agent.py
```

You can also override the provider and model from the command line:

```bash
python agent.py --provider openai --model gpt-4.1-mini
```

## Evaluate it with Halios

Add the Halios skill:

```bash
npx skills add HaliosAI/halios --skill halios
```

Open this directory in Codex, Claude Code, Cursor, or another coding agent and prompt:

```text
Set up evals for this agent.
```

From there, try prompts such as:

```text
Add scenarios where customer verification fails.
```

```text
Check that the agent follows the indoor vs. outdoor furniture rules.
```

```text
Run the eval suite and investigate what failed.
```

See the [Halios documentation](https://docs.halios.ai) for additional workflows.

## License

MIT License. Free to use, adapt, and benchmark.

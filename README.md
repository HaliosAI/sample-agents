# Halios Sample Agents

Example AI agents for trying scenario-based, multi-turn evaluations with
[Halios](https://halios.ai).

Each example is self-contained and includes setup instructions, mock business tools, and local
data so you can inspect the agent, create realistic scenarios, and run fresh evaluation trials.

## Available Agents

| Agent | What it demonstrates |
| :--- | :--- |
| [**`demo-shopper-agent`**](./demo-shopper-agent) | A conversational furniture sales agent with customer verification, session tracking, catalog search, and tool calling. |
| [**`demo-rag-agent`**](./demo-rag-agent) | A grounded RAG assistant with hybrid retrieval, citation attribution, and anti-hallucination guardrails. |

## Try an Evaluation

1. Clone this repository and open an agent directory in Codex, Claude Code, Cursor, or another
   coding agent.
2. Give your coding agent this prompt:

   ```text
   Run npx skills add HaliosAI/halios --skill halios, then use the Halios skill to set up evals for this agent.
   ```

The Halios skill will inspect the agent and help you create scenarios and checks before running a
bounded smoke evaluation.

See each agent's README for local setup, or read the
[Halios documentation](https://docs.halios.ai) for evaluation concepts and workflows.

## License

MIT License. Free to use, adapt, and benchmark.

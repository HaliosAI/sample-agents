# Halios Sample Agents

Sample agents you can use to try [Halios](https://halios.ai).

Each example is a runnable agent with enough realistic behavior, tools, and failure modes to build a useful evaluation suite around it.

## Agents

| Agent | What it demonstrates |
| --- | --- |
| [`demo-shopper-agent`](./demo-shopper-agent) | A furniture sales agent with identity verification, catalog search, session state, and multi-step tool use. |
| [`demo-rag-agent`](./demo-rag-agent) | A RAG assistant with hybrid retrieval, citation attribution, and grounded-answer requirements. |

## Try Halios

Clone the repository:

```bash id="kw1uhm"
git clone https://github.com/HaliosAI/sample-agents.git
cd sample-agents/demo-shopper-agent
```

Follow the agent's README to install its dependencies and run it locally.

Then add the Halios skill:

```bash id="48ss0j"
npx skills add HaliosAI/halios --skill halios
```

Open the agent directory in Codex, Claude Code, Cursor, or another coding agent and prompt:

```text id="8ekn73"
Set up evals for this agent.
```

Your coding agent can use Halios to create scenarios and checks, run evaluations, and investigate failures based on the agent's actual behavior.

See the [Halios documentation](https://docs.halios.ai) for more examples and workflows.

## License

MIT License. Free to use, modify, and benchmark.

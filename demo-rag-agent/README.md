# 📚 Demo RAG Agent

A document QA agent with hybrid retrieval, citations, and conflicting policy versions.

Use it to try Halios against common RAG failure modes such as bad retrieval, unsupported answers, missing citations, and outdated evidence.

## What the agent does

- **Hybrid retrieval** — searches the corpus using semantic and keyword retrieval.
- **Grounded answers** — answers from retrieved documents and cites the supporting source.
- **Refusal** — declines questions that cannot be answered from the available documents.
- **Policy versioning** — distinguishes current policies from superseded versions.
- **Tool use** — retrieves relevant document sections or fetches the full source when needed.

The sample corpus includes architecture, security, and refund-policy documents, including multiple versions of the same policy.

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

Configure an OpenAI or compatible model endpoint, then run:

```bash
python agent.py
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

Then try prompts such as:

```text
Add scenarios where the relevant answer appears only in an older policy document.
```

```text
Check that factual claims are supported by the cited document.
```

```text
Add questions that cannot be answered from the corpus and verify that the agent refuses.
```

```text
Run the eval suite and investigate what failed.
```

See the [Halios documentation](https://docs.halios.ai) for additional workflows.

## License

MIT License. Free to use, adapt, and benchmark.

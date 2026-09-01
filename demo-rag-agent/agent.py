"""Document Research & QA RAG Agent.

Equipped with hybrid retrieval tools, strict citation generation,
and anti-hallucination guardrails.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

from rag_engine import RAGEngine

load_dotenv()

# Load prompt
PROMPT_PATH = Path(__file__).parent / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else (
    "You are a strict, grounded Document Research Assistant. Always cite sources."
)

# Tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_documents",
            "description": "Perform hybrid (semantic + keyword) search across the documentation knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or concept to look up.",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of top document sections to retrieve (default: 3).",
                        "default": 3,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_full_document",
            "description": "Fetch the full complete markdown document by its document ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document identifier (e.g. 'cloud_architecture', 'refund_policy_v2_updated').",
                    }
                },
                "required": ["doc_id"],
            },
        },
    },
]


class RAGAgent:
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required.")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.engine = RAGEngine(openai_api_key=self.api_key, base_url=self.base_url)

    def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        """Execute local RAG engine tools and return stringified result."""
        if name == "retrieve_documents":
            query = args.get("query", "")
            top_k = int(args.get("top_k", 3))
            chunks = self.engine.retrieve(query, top_k=top_k)
            if not chunks:
                return json.dumps({"status": "no_results", "message": "No matching documentation found."})
            
            formatted_chunks = [
                {
                    "doc_id": c["doc_id"],
                    "section": c["section_title"],
                    "doc_title": c["doc_title"],
                    "content": c["content"],
                }
                for c in chunks
            ]
            return json.dumps({"status": "success", "results": formatted_chunks})

        if name == "get_full_document":
            doc_id = args.get("doc_id", "")
            content = self.engine.get_document(doc_id)
            if content is None:
                return json.dumps({"status": "error", "message": f"Document '{doc_id}' not found."})
            return json.dumps({"status": "success", "doc_id": doc_id, "content": content})

        return json.dumps({"status": "error", "message": f"Unknown tool '{name}'."})

    def ask(self, question: str, chat_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Process a user question through multi-turn tool-calling loop."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": question})

        retrieved_evidence = []
        tool_call_history = []

        # Tool execution loop (max 4 turns)
        for _ in range(4):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                temperature=0.0,
            )
            choice = response.choices[0]
            message = choice.message

            if not message.tool_calls:
                return {
                    "answer": message.content or "",
                    "retrieved_evidence": retrieved_evidence,
                    "tool_calls": tool_call_history,
                }

            # Process tool calls
            messages.append(message)
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments or "{}")
                tool_call_history.append({"tool": fn_name, "args": fn_args})

                tool_output = self.execute_tool(fn_name, fn_args)
                parsed = json.loads(tool_output)
                if fn_name == "retrieve_documents" and parsed.get("status") == "success":
                    retrieved_evidence.extend(parsed.get("results", []))

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": fn_name,
                        "content": tool_output,
                    }
                )

        # Fallback return
        return {
            "answer": "Maximum tool execution turns exceeded.",
            "retrieved_evidence": retrieved_evidence,
            "tool_calls": tool_call_history,
        }


def main():
    print("==================================================")
    print("📚 Document Research & QA RAG Agent (Grounded Mode)")
    print("Type 'exit' to quit.\n==================================================")

    agent = RAGAgent()
    while True:
        try:
            query = input("\n🔍 Ask a question: ").strip()
            if not query or query.lower() in ("exit", "quit"):
                break

            print("\n⏳ Searching knowledge base...")
            result = agent.ask(query)

            print("\n--- Answer ---")
            print(result["answer"])

            if result["retrieved_evidence"]:
                print(f"\n--- Retrieved Sources ({len(result['retrieved_evidence'])}) ---")
                for src in result["retrieved_evidence"]:
                    print(f"• [Doc: {src['doc_id']}] {src['section']}")
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

"""
agent.py
Open-source Demo Shopper Agent for HomeStyle Furnishings.
Supports Google Gemini, OpenAI, Ollama (local), and custom OpenAI-compatible endpoints.
Uses a zero-dependency CSV-backed search engine over products.csv.
"""

import os
import sys
import asyncio
import argparse
import json
import random
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).resolve().parent / ".env")
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
except ImportError:
    pass

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from .search_engine import search_products
except (ImportError, ValueError):
    from search_engine import search_products

SCRIPT_DIR = Path(__file__).resolve().parent

# --- Mock Business Tools ---

def verify_customer(first_name: str, last_name: str, email: str) -> dict:
    """Verifies if the customer exists in the system."""
    print(f"\n[TOOL] Verifying customer: {first_name} {last_name}, {email}")
    return {
        "verified": True,
        "customer_id": f"cust_{random.randint(1000, 9999)}",
        "loyalty_tier": "Gold" if random.random() > 0.5 else "Silver"
    }

def validate_phone(phone: str) -> bool:
    """Validates the phone number format."""
    print(f"\n[TOOL] Validating phone: {phone}")
    cleaned = re_digits = "".join(c for c in phone if c.isdigit())
    return len(cleaned) >= 10

def validate_email(email: str) -> bool:
    """Validates the email format."""
    print(f"\n[TOOL] Validating email: {email}")
    return "@" in email and "." in email

def send_sms(phone: str, message: str) -> dict:
    """Sends an SMS to the customer."""
    print(f"\n[TOOL] Sending SMS to {phone}: {message}")
    return {"status": "sent", "message_id": f"sms_{random.randint(10000, 99999)}"}

def send_email(email: str, subject: str, body: str) -> dict:
    """Sends an email to the customer."""
    print(f"\n[TOOL] Sending Email to {email}: Subject: {subject}")
    return {"status": "sent", "message_id": f"email_{random.randint(10000, 99999)}"}

def start_session(email: str, first_name: str, last_name: str, phone: str, vendorId: str, assistantId: str) -> dict:
    """Starts a session for the verified customer."""
    print(f"\n[TOOL] Starting session for {first_name} {last_name} ({vendorId})")
    return {
        "session_id": f"sess_{vendorId}_{random.randint(1000, 9999)}",
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }

def close_session(session_id: str) -> dict:
    """Closes the customer session and sends a follow-up summary email."""
    print(f"\n[TOOL] Closing session: {session_id}")
    return {"status": "closed", "session_id": session_id, "summary_email_sent": True}

# --- Tool Registry ---
TOOL_REGISTRY = {
    "verify_customer": verify_customer,
    "validate_phone": validate_phone,
    "validate_email": validate_email,
    "send_sms": send_sms,
    "send_email": send_email,
    "start_session": start_session,
    "close_session": close_session,
    "search_products": search_products,
}

# --- Tool Definitions (OpenAI standard function calling schema) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "verify_customer",
            "description": "Verifies if the customer exists in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"}
                },
                "required": ["first_name", "last_name", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_phone",
            "description": "Validates the phone number format",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string"}
                },
                "required": ["phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_email",
            "description": "Validates the email format",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_sms",
            "description": "Sends an SMS to the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["phone", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email to the customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["email", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_session",
            "description": "Starts a session for the verified customer",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "phone": {"type": "string"},
                    "vendorId": {"type": "string"},
                    "assistantId": {"type": "string"}
                },
                "required": ["email", "first_name", "last_name", "phone", "vendorId", "assistantId"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Searches the catalog for products matching a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "n_results": {"type": "integer", "default": 3}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_session",
            "description": "Closes the customer session and sends a follow-up summary email with recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            }
        }
    }
]

# --- LLM Provider Setup ---

PROVIDER_ALIASES = {
    "google": "gemini",
    "google-gemini": "gemini",
    "local": "ollama",
}

PROVIDER_DEFAULTS = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-2.5-flash-lite",
    },
    "ollama": {
        "api_key_env": "OLLAMA_API_KEY",
        "api_key_default": "ollama",
        "base_url": "http://localhost:11434/v1/",
        "model": "gemma4:latest",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4.1-mini",
    },
    "custom": {
        "api_key_env": "LLM_API_KEY",
    },
}

def first_env(*names: str) -> str | None:
    for name in names:
        if not name:
            continue
        value = os.getenv(name)
        if value:
            return value
    return None

def configure_llm(provider: str | None = None, model: str | None = None, base_url: str | None = None):
    if AsyncOpenAI is None:
        raise ImportError("The 'openai' library is required to run the agent. Please run: pip install -r requirements.txt")

    provider_name = (provider or os.getenv("LLM_PROVIDER") or "gemini").lower()
    provider_name = PROVIDER_ALIASES.get(provider_name, provider_name)

    if provider_name not in PROVIDER_DEFAULTS:
        valid = ", ".join(sorted(PROVIDER_DEFAULTS))
        raise ValueError(f"Unknown LLM provider '{provider_name}'. Valid providers: {valid}")

    defaults = PROVIDER_DEFAULTS[provider_name]
    provider_env_prefix = provider_name.upper()

    configured_model = model or first_env(
        f"{provider_env_prefix}_MODEL",
        "MODEL_ID" if provider_name == "gemini" else "",
    ) or defaults.get("model")
    configured_base_url = base_url or first_env(
        f"{provider_env_prefix}_BASE_URL",
        "LLM_BASE_URL",
        "OPENAI_BASE_URL" if provider_name in {"openai", "custom"} else "",
    ) or defaults.get("base_url")
    api_key = first_env(defaults.get("api_key_env", ""), "OPENAI_API_KEY" if provider_name == "custom" else "")
    api_key = api_key or defaults.get("api_key_default")

    if not configured_model:
        raise ValueError(f"No model configured for provider '{provider_name}'.")
    if not api_key:
        raise ValueError(f"{defaults['api_key_env']} not found in environment.")
    if provider_name == "custom" and not configured_base_url:
        raise ValueError("LLM_BASE_URL or CUSTOM_BASE_URL is required for provider 'custom'.")

    client_kwargs = {"api_key": api_key}
    if configured_base_url:
        client_kwargs["base_url"] = configured_base_url

    return AsyncOpenAI(**client_kwargs), configured_model, provider_name, configured_base_url

def assistant_tool_message(response_message) -> dict:
    return {
        "role": "assistant",
        "content": response_message.content or "",
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in response_message.tool_calls
        ],
    }

async def run_chat(provider: str | None = None, model: str | None = None, base_url: str | None = None):
    """Run interactive terminal chat with the shopper agent."""
    try:
        client, model_id, provider_name, configured_base_url = configure_llm(provider, model, base_url)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    prompt_file = SCRIPT_DIR / "prompt.md"
    if not prompt_file.exists():
        print(f"Error: Prompt file '{prompt_file}' not found.")
        return

    system_prompt = prompt_file.read_text()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Hi"},
    ]

    print("==========================================================")
    print(" HomeStyle Furnishings - Open Source Demo Shopper Agent")
    print("==========================================================")
    print(f"Provider: {provider_name} | Model: {model_id}")
    if configured_base_url:
        print(f"Base URL: {configured_base_url}")
    print("Type 'quit' or 'exit' to end the conversation.\n")

    try:
        initial_response = await client.chat.completions.create(
            model=model_id,
            messages=messages,
        )
        greeting = initial_response.choices[0].message.content
        messages.append({"role": "assistant", "content": greeting})
        print(f"Agent: {greeting}")
    except Exception as e:
        print(f"Error starting chat: {e}")
        return

    while True:
        try:
            user_input = input("\nUser: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_input.strip().lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = await client.chat.completions.create(
                model=model_id,
                messages=messages,
                tools=tools,
            )
            response_message = response.choices[0].message

            if response_message.tool_calls:
                print(f"\n[DEBUG] Executing {len(response_message.tool_calls)} tool call(s)...")
                messages.append(assistant_tool_message(response_message))

                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"[TOOL] Calling {function_name}({json.dumps(function_args)})")
                    function_to_call = TOOL_REGISTRY.get(function_name)
                    if not function_to_call:
                        print(f"[ERROR] Tool {function_name} not found!")
                        continue

                    function_response = function_to_call(**function_args)
                    print(f"[TOOL] Result: {str(function_response)[:120]}...")

                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": json.dumps(function_response) if not isinstance(function_response, str) else function_response,
                        }
                    )

                second_response = await client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                )
                final_message = second_response.choices[0].message.content
                messages.append({"role": "assistant", "content": final_message})
                print(f"\nAgent: {final_message}")
            else:
                ai_text = response_message.content
                messages.append({"role": "assistant", "content": ai_text})
                print(f"\nAgent: {ai_text}")

        except Exception as e:
            print(f"Error during turn: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the HomeStyle Demo Shopper Chatbot")
    parser.add_argument(
        "--provider",
        choices=["gemini", "google", "ollama", "local", "openai", "custom"],
        help="LLM provider. Defaults to LLM_PROVIDER or gemini.",
    )
    parser.add_argument("--model", help="Override the provider model.")
    parser.add_argument("--base-url", help="Override the OpenAI-compatible base URL.")
    args = parser.parse_args()

    try:
        asyncio.run(run_chat(provider=args.provider, model=args.model, base_url=args.base_url))
    except KeyboardInterrupt:
        print("\nExiting...")

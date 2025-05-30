#!/usr/bin/env python3
"""Simple script to verify OpenAI ChatGPT API access.

This script sends a test prompt to the ChatGPT API using the ``openai``
package. Provide the API key via the ``--key`` argument or the
``OPENAI_API_KEY`` (preferred) or ``OPEN_AI_KEY`` environment variables.
The script prints the response from ChatGPT and exits with status 0 on
success or 1 on failure.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_a, **_k):
        return False

__test__ = False

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None


def call_chatgpt(api_key: str, prompt: str) -> int:
    """Send ``prompt`` to ChatGPT using ``api_key`` and return an exit code."""
    if OpenAI is None:
        print("openai package not available")
        return 1

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        print("✅ API call succeeded")
        print(response.choices[0].message.content.strip())
        return 0
    except Exception as exc:  # pragma: no cover - network dependent
        print("❌ API call failed")
        print(str(exc))
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Test ChatGPT API access")
    parser.add_argument(
        "--key",
        help=(
            "OpenAI API key (defaults to OPENAI_API_KEY or OPEN_AI_KEY environment" 
            " variables)"
        ),
    )
    parser.add_argument(
        "--prompt", default="Say hello", help="Prompt text to send to ChatGPT"
    )
    args = parser.parse_args(argv)


    # Load environment variables from project .env files
    base_dir = Path(__file__).resolve().parent.parent
    load_dotenv(base_dir / ".env")
    load_dotenv(base_dir / ".env.example")


    api_key = args.key or os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")
    if not api_key:
        print("OPENAI_API_KEY or OPEN_AI_KEY is required")
        return 1

    return call_chatgpt(api_key, args.prompt)


if __name__ == "__main__":
    sys.exit(main())


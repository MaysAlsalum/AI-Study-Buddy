"""
backend/core/llm.py
Shared LLM client used by all agents (Summarizer, Quiz Generator, Study Planner).
Talks to OpenRouter using the nvidia/nemotron-3-nano-30b-a3b:free model.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "nvidia/nemotron-3-nano-30b-a3b:free"


class LLMError(Exception):
    """Raised when the LLM call fails or returns something unusable."""
    pass


def call_llm(prompt: str, system_prompt: str = None, temperature: float = 0.4,
             max_tokens: int = 2000) -> str:
    """
    Sends a chat completion request to OpenRouter and returns the raw text response.
    Raises LLMError on network/API failure.
    """
    if not OPENROUTER_API_KEY:
        raise LLMError("OPENROUTER_API_KEY is not set. Check your .env file.")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # OpenRouter asks for these two headers for free-tier usage attribution
        "HTTP-Referer": "https://ai-study-buddy.local",
        "X-Title": "AI Study Buddy",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise LLMError(f"OpenRouter request failed: {e}")

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise LLMError(f"Unexpected response shape from OpenRouter: {json.dumps(data)[:500]}")
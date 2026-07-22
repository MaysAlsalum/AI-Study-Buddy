"""
Shared OpenRouter LLM client for AI Study Buddy.

Each agent can use its own API key and model.
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv


load_dotenv()


class LLMError(Exception):
    """Raised when an OpenRouter API request fails."""


OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_CHAT_URL = f"{OPENROUTER_BASE_URL}/chat/completions"


def call_llm(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    Send a prompt to OpenRouter and return the generated text.

    Args:
        prompt: User prompt sent to the model.
        system_prompt: System instruction for the model.
        temperature: Controls output randomness.
        api_key: Agent-specific OpenRouter API key.
        model: Agent-specific model identifier.

    Returns:
        Generated response text.

    Raises:
        LLMError: If configuration is missing or the API request fails.
    """

    if not api_key:
        raise LLMError(
            "OpenRouter API key is missing for this agent. "
            "Check the agent-specific key in the .env file."
        )

    if not model:
        raise LLMError(
            "OpenRouter model is missing for this agent. "
            "Check the agent-specific model in the .env file."
        )

    messages = []

    if system_prompt:
        messages.append(
            {
                "role": "system",
                "content": system_prompt,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-study-buddy.app",
        "X-Title": "AI Study Buddy",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        response = requests.post(
            OPENROUTER_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise LLMError(
            f"Could not connect to OpenRouter: {exc}"
        ) from exc

    if response.status_code != 200:
        try:
            error_data = response.json()
        except ValueError:
            error_data = response.text

        raise LLMError(
            f"OpenRouter request failed with status "
            f"{response.status_code}: {error_data}"
        )

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise LLMError(
            f"Unexpected OpenRouter response: {response.text[:1000]}"
        ) from exc
"""
backend/agents/summarizer.py

This file contains Agent 1: the Summarization Agent.

Responsibilities:
- Read the study material from StudyState.
- Generate a concise summary.
- Extract key topics.
- Extract important terms and definitions.
- Return data using the shared JSON contract.
"""

import json

from backend.core.llm import LLMError, call_llm
from backend.core.state import StudyState
import os


SUMMARIZER_API_KEY = os.getenv(
    "SUMMARIZER_OPENROUTER_API_KEY"
)

SUMMARIZER_MODEL = os.getenv(
    "SUMMARIZER_MODEL",
    "nvidia/nemotron-3-nano-30b-a3b:free",
)

SUMMARIZER_TEMPERATURE = float(
    os.getenv("SUMMARIZER_TEMPERATURE", "0.3")
)



SYSTEM_PROMPT = """
You are an educational summarization agent.

Your task is to analyze study material and return structured JSON only.

You must return exactly this structure:

{
  "summary": "A concise and clear summary of the study material.",
  "key_topics": [
    "Topic 1",
    "Topic 2"
  ],
  "definitions": [
    {
      "term": "Important term",
      "definition": "Clear definition"
    }
  ]
}

Rules:
- Return valid JSON only.
- Do not include Markdown code blocks.
- Do not include any text before or after the JSON.
- Keep the summary concise but informative.
- Extract only topics and definitions found in the provided material.
"""


def _parse_json_response(response_text: str) -> dict:
    """
    Converts the LLM response into a Python dictionary.

    Raises:
        ValueError: If the response is not valid JSON.
    """

    cleaned_response = response_text.strip()

    # Some models may wrap JSON in Markdown code blocks.
    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.removeprefix("```json")
        cleaned_response = cleaned_response.removeprefix("```")
        cleaned_response = cleaned_response.removesuffix("```")
        cleaned_response = cleaned_response.strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The Summarization Agent returned invalid JSON."
        ) from error


def _validate_summary_output(data: dict) -> None:
    """
    Validates that the LLM output follows the shared JSON contract.
    """

    required_fields = {
        "summary",
        "key_topics",
        "definitions",
    }

    missing_fields = required_fields - data.keys()

    if missing_fields:
        raise ValueError(
            f"Missing summarization fields: {sorted(missing_fields)}"
        )

    if not isinstance(data["summary"], str):
        raise ValueError("'summary' must be a string.")

    if not isinstance(data["key_topics"], list):
        raise ValueError("'key_topics' must be a list.")

    if not isinstance(data["definitions"], list):
        raise ValueError("'definitions' must be a list.")

    for topic in data["key_topics"]:
        if not isinstance(topic, str):
            raise ValueError(
                "Every item in 'key_topics' must be a string."
            )

    for item in data["definitions"]:
        if not isinstance(item, dict):
            raise ValueError(
                "Every item in 'definitions' must be an object."
            )

        if "term" not in item or "definition" not in item:
            raise ValueError(
                "Every definition must contain 'term' and 'definition'."
            )

        if not isinstance(item["term"], str):
            raise ValueError("'term' must be a string.")

        if not isinstance(item["definition"], str):
            raise ValueError("'definition' must be a string.")


def summarization_agent(state: StudyState) -> dict:
    """
    Runs the Summarization Agent.

    Reads:
        state["raw_text"]

    Returns:
        summary
        key_topics
        definitions
        execution_logs
    """

    raw_text = state["raw_text"].strip()

    if not raw_text:
        raise ValueError("Study material cannot be empty.")

    prompt = f"""
Analyze the following study material.

Study material:
{raw_text}
"""

    current_logs = list(state.get("execution_logs", []))
    current_logs.append("Summarization Agent started.")

    try:
        response_text = call_llm(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=SUMMARIZER_TEMPERATURE,
            api_key=SUMMARIZER_API_KEY,
            model=SUMMARIZER_MODEL,
        )
        parsed_response = _parse_json_response(response_text)
        _validate_summary_output(parsed_response)

    except (LLMError, ValueError) as error:
        current_logs.append(
            f"Summarization Agent failed: {error}"
        )
        raise

    current_logs.append("Summarization Agent completed.")

    return {
        "summary": parsed_response["summary"].strip(),
        "key_topics": [
            topic.strip()
            for topic in parsed_response["key_topics"]
            if topic.strip()
        ],
        "definitions": [
            {
                "term": item["term"].strip(),
                "definition": item["definition"].strip(),
            }
            for item in parsed_response["definitions"]
            if item["term"].strip() and item["definition"].strip()
        ],
        "execution_logs": current_logs,
    }
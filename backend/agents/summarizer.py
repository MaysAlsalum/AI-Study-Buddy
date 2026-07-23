"""
backend/agents/summarizer.py

This file contains Agent 1: the Summarization Agent.

Responsibilities:
- Read study material from plain text or PDF.
- Extract text from PDF files.
- Generate a concise summary.
- Extract key topics.
- Extract important terms and definitions.
- Return data using the shared JSON contract.
"""

import json
import os
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

from pypdf import PdfReader

from backend.core.llm import LLMError, call_llm
from backend.core.state import StudyState


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


def extract_text_from_pdf(
    pdf_source: Union[str, Path, bytes, BinaryIO],
) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_source:
            A file path, PDF bytes, or a binary file-like object.

    Returns:
        Extracted and cleaned text from all PDF pages.

    Raises:
        ValueError:
            If the PDF is invalid, encrypted, empty, or contains no
            extractable text.
    """

    try:
        if isinstance(pdf_source, bytes):
            reader = PdfReader(BytesIO(pdf_source))

        elif isinstance(pdf_source, (str, Path)):
            pdf_path = Path(pdf_source)

            if not pdf_path.exists():
                raise ValueError(
                    f"PDF file was not found: {pdf_path}"
                )

            if pdf_path.suffix.lower() != ".pdf":
                raise ValueError(
                    "The uploaded file must be a PDF."
                )

            reader = PdfReader(str(pdf_path))

        else:
            reader = PdfReader(pdf_source)

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            f"Unable to read the PDF file: {error}"
        ) from error

    if reader.is_encrypted:
        try:
            decrypt_result = reader.decrypt("")
        except Exception as error:
            raise ValueError(
                "The PDF is encrypted and cannot be read."
            ) from error

        if decrypt_result == 0:
            raise ValueError(
                "The PDF is encrypted and requires a password."
            )

    extracted_pages: list[str] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        try:
            page_text = page.extract_text() or ""
        except Exception as error:
            raise ValueError(
                f"Failed to extract text from page {page_number}."
            ) from error

        cleaned_page_text = page_text.strip()

        if cleaned_page_text:
            extracted_pages.append(cleaned_page_text)

    full_text = "\n\n".join(extracted_pages).strip()

    if not full_text:
        raise ValueError(
            "No readable text was found in the PDF. "
            "The file may be scanned and may require OCR."
        )

    return full_text


def _parse_json_response(response_text: str) -> dict:
    """
    Convert the LLM response into a Python dictionary.

    Raises:
        ValueError: If the response is not valid JSON.
    """

    cleaned_response = response_text.strip()

    if cleaned_response.startswith("```"):
        cleaned_response = cleaned_response.removeprefix(
            "```json"
        )
        cleaned_response = cleaned_response.removeprefix(
            "```"
        )
        cleaned_response = cleaned_response.removesuffix(
            "```"
        )
        cleaned_response = cleaned_response.strip()

    try:
        return json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            "The Summarization Agent returned invalid JSON."
        ) from error


def _validate_summary_output(data: dict) -> None:
    """
    Validate that the LLM output follows the shared JSON contract.
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
        raise ValueError(
            "'summary' must be a string."
        )

    if not isinstance(data["key_topics"], list):
        raise ValueError(
            "'key_topics' must be a list."
        )

    if not isinstance(data["definitions"], list):
        raise ValueError(
            "'definitions' must be a list."
        )

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
                "Every definition must contain "
                "'term' and 'definition'."
            )

        if not isinstance(item["term"], str):
            raise ValueError(
                "'term' must be a string."
            )

        if not isinstance(item["definition"], str):
            raise ValueError(
                "'definition' must be a string."
            )


def _get_study_text(state: StudyState) -> str:
    """
    Get study material from raw text or a PDF source.

    The function checks raw_text first. If raw_text is empty,
    it attempts to read pdf_bytes or pdf_path from the state.
    """

    raw_text = state.get("raw_text", "")

    if isinstance(raw_text, str) and raw_text.strip():
        return raw_text.strip()

    pdf_bytes = state.get("pdf_bytes")

    if pdf_bytes:
        return extract_text_from_pdf(pdf_bytes)

    pdf_path = state.get("pdf_path")

    if pdf_path:
        return extract_text_from_pdf(pdf_path)

    raise ValueError(
        "No study material was provided. "
        "Provide raw_text, pdf_bytes, or pdf_path."
    )


def summarization_agent(state: StudyState) -> dict:
    """
    Run the Summarization Agent.

    Reads:
        state["raw_text"], or
        state["pdf_bytes"], or
        state["pdf_path"]

    Returns:
        summary
        key_topics
        definitions
        raw_text
        execution_logs
    """

    current_logs = list(
        state.get("execution_logs", [])
    )

    current_logs.append(
        "Summarization Agent started."
    )

    try:
        study_text = _get_study_text(state)

        current_logs.append(
            "Study material text prepared."
        )

        prompt = f"""
Analyze the following study material.

Study material:
{study_text}
"""

        response_text = call_llm(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=SUMMARIZER_TEMPERATURE,
            api_key=SUMMARIZER_API_KEY,
            model=SUMMARIZER_MODEL,
        )

        parsed_response = _parse_json_response(
            response_text
        )

        _validate_summary_output(
            parsed_response
        )

    except (LLMError, ValueError) as error:
        current_logs.append(
            f"Summarization Agent failed: {error}"
        )
        raise

    current_logs.append(
        "Summarization Agent completed."
    )

    return {
        "raw_text": study_text,
        "summary": parsed_response["summary"].strip(),
        "key_topics": [
            topic.strip()
            for topic in parsed_response["key_topics"]
            if isinstance(topic, str) and topic.strip()
        ],
        "definitions": [
            {
                "term": item["term"].strip(),
                "definition": item["definition"].strip(),
            }
            for item in parsed_response["definitions"]
            if (
                item["term"].strip()
                and item["definition"].strip()
            )
        ],
        "execution_logs": current_logs,
    }
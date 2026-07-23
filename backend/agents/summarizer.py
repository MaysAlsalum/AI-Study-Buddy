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


import re
from dataclasses import dataclass
from typing import Pattern


# Security and prompt injection detection
MAX_INPUT_CHARACTERS = 5000
SECURITY_BLOCK_SCORE = 6


@dataclass(frozen=True)
class AttackPattern:
    name: str
    regex: Pattern[str]
    score: int
    description: str


ATTACK_PATTERNS = [
    # Instruction override attempts
    AttackPattern(
        name="instruction_override",
        regex=re.compile(
            r"\b("
            r"ignore|disregard|forget|override|bypass|cancel"
            r")\b.{0,50}\b("
            r"previous|prior|above|system|developer|original"
            r")\b.{0,30}\b("
            r"instructions?|prompts?|rules?|messages?"
            r")\b",
            re.IGNORECASE | re.DOTALL,
        ),
        score=5,
        description="Attempts to override previous or system instructions.",
    ),

    AttackPattern(
        name="new_instruction_claim",
        regex=re.compile(
            r"\b("
            r"these are your new instructions|"
            r"follow my instructions instead|"
            r"replace your instructions|"
            r"new system prompt|"
            r"updated developer message"
            r")\b",
            re.IGNORECASE,
        ),
        score=5,
        description="Claims that the input contains new trusted instructions.",
    ),

    # Role hijacking
    AttackPattern(
        name="role_hijacking",
        regex=re.compile(
            r"\b("
            r"act as|pretend to be|you are now|from now on|"
            r"assume the role of|switch roles?|enter .* mode"
            r")\b",
            re.IGNORECASE,
        ),
        score=3,
        description="Attempts to change the agent role or behavior.",
    ),

    AttackPattern(
        name="jailbreak_language",
        regex=re.compile(
            r"\b("
            r"jailbreak|developer mode|dan mode|unrestricted mode|"
            r"god mode|evil mode|no restrictions?|without limitations?"
            r")\b",
            re.IGNORECASE,
        ),
        score=5,
        description="Known jailbreak or unrestricted-mode language.",
    ),

    # Secret and prompt exfiltration
    AttackPattern(
        name="system_prompt_exfiltration",
        regex=re.compile(
            r"\b("
            r"reveal|show|print|display|repeat|leak|expose|return"
            r")\b.{0,50}\b("
            r"system prompt|developer message|hidden instructions?|"
            r"internal prompt|initial prompt|policy|configuration"
            r")\b",
            re.IGNORECASE | re.DOTALL,
        ),
        score=6,
        description="Attempts to reveal hidden prompts or internal instructions.",
    ),

    AttackPattern(
        name="secret_exfiltration",
        regex=re.compile(
            r"\b("
            r"reveal|show|print|send|return|extract|leak|expose"
            r")\b.{0,50}\b("
            r"api[_ -]?key|secret|token|password|credential|"
            r"environment variable|\.env|authorization header"
            r")\b",
            re.IGNORECASE | re.DOTALL,
        ),
        score=7,
        description="Attempts to obtain secrets, credentials, or API keys.",
    ),

    # Tool and code execution attempts
    AttackPattern(
        name="tool_execution",
        regex=re.compile(
            r"\b("
            r"execute|run|invoke|call|trigger|use"
            r")\b.{0,40}\b("
            r"shell|terminal|powershell|cmd|bash|python|tool|function|"
            r"browser|api|database|filesystem"
            r")\b",
            re.IGNORECASE | re.DOTALL,
        ),
        score=4,
        description="Attempts to make the agent invoke tools or execute commands.",
    ),

    AttackPattern(
        name="dangerous_shell_command",
        regex=re.compile(
            r"("
            r"rm\s+-rf|"
            r"del\s+/[fsq]|"
            r"format\s+[a-z]:|"
            r"shutdown\s+[-/]|"
            r"curl\s+.+\|\s*(bash|sh)|"
            r"wget\s+.+\|\s*(bash|sh)|"
            r"powershell\s+.*-enc|"
            r"invoke-expression|"
            r"eval\s*\(|"
            r"exec\s*\("
            r")",
            re.IGNORECASE,
        ),
        score=7,
        description="Contains potentially dangerous execution commands.",
    ),

    # Data exfiltration and external requests
    AttackPattern(
        name="external_exfiltration",
        regex=re.compile(
            r"\b("
            r"send|upload|post|forward|transmit|exfiltrate"
            r")\b.{0,60}\b("
            r"http[s]?://|webhook|server|endpoint|email|telegram|discord"
            r")\b",
            re.IGNORECASE | re.DOTALL,
        ),
        score=6,
        description="Attempts to transmit data to an external destination.",
    ),

    # Delimiter and context escape attacks
    AttackPattern(
        name="prompt_delimiter_escape",
        regex=re.compile(
            r"("
            r"</?system>|"
            r"</?assistant>|"
            r"</?developer>|"
            r"\[/?system\]|"
            r"\[/?assistant\]|"
            r"###\s*(system|developer|assistant)|"
            r"BEGIN\s+(SYSTEM|DEVELOPER)\s+PROMPT|"
            r"END\s+(SYSTEM|DEVELOPER)\s+PROMPT"
            r")",
            re.IGNORECASE,
        ),
        score=5,
        description="Attempts to inject fake role or prompt delimiters.",
    ),

    AttackPattern(
        name="conversation_forgery",
        regex=re.compile(
            r"\b("
            r"system\s*:|developer\s*:|assistant\s*:|"
            r"trusted instruction\s*:|administrator\s*:"
            r")",
            re.IGNORECASE,
        ),
        score=3,
        description="Attempts to forge system, developer, or assistant messages.",
    ),

    # Output manipulation
    AttackPattern(
        name="output_override",
        regex=re.compile(
            r"\b("
            r"do not summarize|instead of summarizing|"
            r"output only|respond only with|return exactly|"
            r"do not return json|ignore the required format"
            r")\b",
            re.IGNORECASE,
        ),
        score=4,
        description="Attempts to replace the required summarization output.",
    ),

    # Hidden or encoded payloads
    AttackPattern(
        name="encoded_instruction",
        regex=re.compile(
            r"\b("
            r"decode this|base64|rot13|hex encoded|unicode encoded|"
            r"reverse the following|decrypt the following"
            r")\b",
            re.IGNORECASE,
        ),
        score=3,
        description="May contain an encoded or obfuscated instruction.",
    ),

    AttackPattern(
        name="base64_payload",
        regex=re.compile(
            r"\b[A-Za-z0-9+/]{100,}={0,2}\b"
        ),
        score=3,
        description="Contains a long Base64-like payload.",
    ),

    # Recursive and indirect prompt injection
    AttackPattern(
        name="indirect_instruction",
        regex=re.compile(
            r"\b("
            r"when an ai reads this|when the assistant sees this|"
            r"instructions for the language model|"
            r"message to the ai|note to the assistant|"
            r"the model must|the assistant must"
            r")\b",
            re.IGNORECASE,
        ),
        score=5,
        description="Contains instructions directed at an AI rather than study content.",
    ),

    # Security bypass language
    AttackPattern(
        name="security_bypass",
        regex=re.compile(
            r"\b("
            r"disable security|disable validation|skip validation|"
            r"bypass filters?|evade detection|avoid detection|"
            r"ignore safety|remove restrictions?"
            r")\b",
            re.IGNORECASE,
        ),
        score=6,
        description="Attempts to disable or bypass security controls.",
    ),
]




def normalize_security_text(text: str) -> str:
    """
    Normalize text before applying security checks.
    """

    normalized = text.replace("\u200b", "")
    normalized = normalized.replace("\u200c", "")
    normalized = normalized.replace("\u200d", "")
    normalized = normalized.replace("\ufeff", "")

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()





def inspect_study_material(raw_text: str) -> dict:
    """
    Inspect study material for prompt injection and malicious patterns.

    Returns:
        A security report containing:
        - blocked
        - score
        - detected_patterns
        - security_reason
    """

    if not isinstance(raw_text, str):
        raise ValueError(
            "Study material must be a string."
        )

    cleaned_text = normalize_security_text(raw_text)

    if not cleaned_text:
        return {
            "blocked": True,
            "score": 10,
            "detected_patterns": ["empty_input"],
            "security_reason": "Study material is empty.",
        }

    if len(cleaned_text) > MAX_INPUT_CHARACTERS:
        return {
            "blocked": True,
            "score": 10,
            "detected_patterns": ["oversized_input"],
            "security_reason": (
                "Study material exceeds the maximum allowed size "
                f"of {MAX_INPUT_CHARACTERS} characters."
            ),
        }

    total_score = 0
    detected_patterns = []
    reasons = []

    for attack_pattern in ATTACK_PATTERNS:
        if attack_pattern.regex.search(cleaned_text):
            total_score += attack_pattern.score

            detected_patterns.append(
                attack_pattern.name
            )

            reasons.append(
                attack_pattern.description
            )

    blocked = total_score >= SECURITY_BLOCK_SCORE

    if blocked:
        security_reason = "; ".join(reasons)
    elif detected_patterns:
        security_reason = (
            "Potentially suspicious content was detected, "
            "but the blocking threshold was not reached."
        )
    else:
        security_reason = ""

    return {
        "blocked": blocked,
        "score": total_score,
        "detected_patterns": detected_patterns,
        "security_reason": security_reason,
    }





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

        security_report = inspect_study_material(
            study_text
        )

        if security_report["blocked"]:
            current_logs.append(
                "Summarization Agent blocked the input: "
                f"{security_report['security_reason']}"
            )

            return {
                "blocked": True,
                "security_reason": security_report[
                    "security_reason"
                ],
                "security_score": security_report["score"],
                "detected_attack_patterns": security_report[
                    "detected_patterns"
                ],
                "execution_logs": current_logs,
            }

        current_logs.append(
            "Study material passed security inspection."
        )

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

        # Security result for successful input
        "blocked": False,
        "security_reason": "",
        "security_score": security_report["score"],
        "detected_attack_patterns": security_report[
            "detected_patterns"
        ],

        "execution_logs": current_logs,
    }
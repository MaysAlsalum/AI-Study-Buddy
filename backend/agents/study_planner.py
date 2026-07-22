"""
Study Planner Agent for AI Study Buddy.

Receives `key_topics` and `study_days` from the LangGraph state,
creates a balanced study plan via Gemini 2.5 Flash (OpenRouter),
enriches each day with difficulty and estimated_hours,
applies spaced repetition scheduling as a pure-Python post-processing step,
and returns only the updated `study_plan` field.

Security layer is co-located in this file as standalone helper functions,
keeping it clearly separated from the business logic.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Literal

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Days after first introduction at which a topic should be reviewed.
# Based on the SM-2 spaced repetition principle (simplified).
_SPACED_REPETITION_INTERVALS: list[int] = [1, 3, 7]

_REVIEW_PREFIX = "Review: "

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class StudyPlannerInput(BaseModel):
    """Schema for the Study Planner Agent's validated input."""

    key_topics: list[str] = Field(..., min_length=1, description="Topics to study.")
    study_days: int = Field(..., ge=1, le=30, description="Number of available study days.")

    @field_validator("key_topics")
    @classmethod
    def topics_must_be_non_empty_strings(cls, topics: list[str]) -> list[str]:
        """Ensure every topic is a non-blank string."""
        if not topics:
            raise ValueError("key_topics must contain at least one entry.")
        for topic in topics:
            if not isinstance(topic, str) or not topic.strip():
                raise ValueError("Every topic must be a non-empty string.")
        return topics

    model_config = {"extra": "ignore"}  # Silently drop unexpected fields


class DayPlan(BaseModel):
    """Represents one day in the study plan."""

    day: int = Field(..., ge=1, description="Day number (1-indexed).")
    topics: list[str] = Field(
        ..., min_length=1, description="Topics or review items for the day."
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        ..., description="Overall difficulty level for this day's content."
    )
    estimated_hours: float = Field(
        ..., ge=0.5, le=8.0, description="Estimated study hours required for this day."
    )


class StudyPlanOutput(BaseModel):
    """Structured output produced by the LLM."""

    study_plan: list[DayPlan] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Security Layer
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+(a\s+)?(?!study)", re.IGNORECASE),
    re.compile(r"(system|assistant)\s*:", re.IGNORECASE),
    re.compile(r"<\s*(script|iframe|object|embed)\b", re.IGNORECASE),
    re.compile(r"\beval\s*\(", re.IGNORECASE),
    re.compile(r"\bexec\s*\(", re.IGNORECASE),
    re.compile(r"\bprompt\s+injection\b", re.IGNORECASE),
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
    re.compile(r"\bDAN\b"),  # "Do Anything Now" jailbreak token
    re.compile(r"\bbase64\b", re.IGNORECASE),
    re.compile(r"\\u[0-9a-fA-F]{4}"),  # Unicode escape attempts
]

_CONTROL_CHARS_RE: re.Pattern[str] = re.compile(r"[\x00-\x1f\x7f]")


def validate_input(raw: dict[str, Any]) -> StudyPlannerInput:
    """Validate raw state input against the StudyPlannerInput schema.

    Args:
        raw: Raw dictionary extracted from LangGraph state.

    Returns:
        A validated :class:`StudyPlannerInput` instance.

    Raises:
        ValueError: If the input fails Pydantic validation.
    """
    try:
        return StudyPlannerInput.model_validate(raw)
    except Exception as exc:
        logger.error("Input validation failed: %s", exc)
        raise ValueError(f"Input validation error: {exc}") from exc


def sanitize_input(validated: StudyPlannerInput) -> StudyPlannerInput:
    """Strip control characters and leading/trailing whitespace from topic strings.

    Args:
        validated: A :class:`StudyPlannerInput` that has already passed schema validation.

    Returns:
        A new :class:`StudyPlannerInput` with sanitized topic strings.

    Raises:
        ValueError: If all topics become empty after sanitization.
    """
    sanitized_topics: list[str] = [
        _CONTROL_CHARS_RE.sub("", topic).strip()
        for topic in validated.key_topics
    ]
    sanitized_topics = [t for t in sanitized_topics if t]

    if not sanitized_topics:
        raise ValueError("All topics were empty after sanitization.")

    return StudyPlannerInput(
        key_topics=sanitized_topics,
        study_days=validated.study_days,
    )


def detect_prompt_injection(topics: list[str]) -> None:
    """Scan topic strings for known prompt injection patterns.

    Args:
        topics: List of sanitized topic strings.

    Raises:
        ValueError: If any topic matches a known injection pattern.
    """
    for topic in topics:
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(topic):
                logger.warning("Prompt injection detected in topic: %r", topic)
                raise ValueError(
                    "Potentially malicious content detected in input. Request rejected."
                )


def validate_output(output: StudyPlanOutput, expected_days: int) -> StudyPlanOutput:
    """Validate the LLM-generated study plan for structural and field correctness.

    Ensures:
    - The plan is not empty.
    - The number of entries matches the requested study_days.
    - Day numbers are sequential starting from 1.
    - Every day has at least one topic.
    - Every day has a valid difficulty level.
    - Every day's estimated_hours is within the accepted range.

    Args:
        output: Structured output returned by the LLM.
        expected_days: Number of study days that was requested.

    Returns:
        The validated :class:`StudyPlanOutput`.

    Raises:
        ValueError: If the output does not conform to expectations.
    """
    plan = output.study_plan

    if not plan:
        raise ValueError("LLM returned an empty study plan.")

    if len(plan) != expected_days:
        raise ValueError(
            f"Study plan contains {len(plan)} day(s) but {expected_days} were requested."
        )

    expected_sequence = list(range(1, expected_days + 1))
    actual_sequence = [entry.day for entry in plan]
    if actual_sequence != expected_sequence:
        raise ValueError(
            f"Day numbers are not sequential. Expected {expected_sequence}, got {actual_sequence}."
        )

    valid_difficulties = {"easy", "medium", "hard"}
    for entry in plan:
        if not entry.topics:
            raise ValueError(f"Day {entry.day} has no topics assigned.")
        if entry.difficulty not in valid_difficulties:
            raise ValueError(
                f"Day {entry.day} has invalid difficulty '{entry.difficulty}'. "
                f"Must be one of {valid_difficulties}."
            )
        if not (0.5 <= entry.estimated_hours <= 8.0):
            raise ValueError(
                f"Day {entry.day} estimated_hours ({entry.estimated_hours}) is out of range [0.5, 8.0]."
            )

    return output


# ---------------------------------------------------------------------------
# Spaced Repetition (pure Python — no LLM involvement)
# ---------------------------------------------------------------------------


def apply_spaced_repetition(plan: list[DayPlan]) -> list[DayPlan]:
    """Inject spaced repetition review entries into an existing study plan.

    For each topic first introduced on day X, schedules a review session
    on days X+1, X+3, and X+7 (when those days exist in the plan).
    Review entries are deduplicated and never overwrite existing topics.

    This function is purely deterministic and does not call the LLM.

    Args:
        plan: A validated list of :class:`DayPlan` objects sorted by day number.

    Returns:
        An updated list of :class:`DayPlan` objects with review entries injected.
        The original plan's difficulty and estimated_hours are preserved;
        days that receive reviews have their estimated_hours adjusted upward
        slightly (+0.5 h per review session, capped at 8.0 h).
    """
    # Build a mutable day-keyed store
    day_store: dict[int, dict[str, Any]] = {
        entry.day: {
            "topics": list(entry.topics),
            "difficulty": entry.difficulty,
            "estimated_hours": entry.estimated_hours,
        }
        for entry in plan
    }
    existing_days = set(day_store.keys())

    # Discover when each topic is first introduced (ignore review entries)
    first_seen: dict[str, int] = {}
    for entry in sorted(plan, key=lambda e: e.day):
        for topic in entry.topics:
            if not topic.startswith(_REVIEW_PREFIX) and topic not in first_seen:
                first_seen[topic] = entry.day

    # Inject review entries at spaced intervals
    for topic, intro_day in first_seen.items():
        review_label = f"{_REVIEW_PREFIX}{topic}"
        for interval in _SPACED_REPETITION_INTERVALS:
            review_day = intro_day + interval
            if review_day not in existing_days:
                continue
            day_data = day_store[review_day]
            if review_label not in day_data["topics"]:
                day_data["topics"].append(review_label)
                # Slightly increase estimated_hours to account for the review workload
                day_data["estimated_hours"] = min(
                    round(day_data["estimated_hours"] + 0.5, 1), 8.0
                )

    # Rebuild as DayPlan instances, preserving original sort order
    return [
        DayPlan(
            day=day,
            topics=data["topics"],
            difficulty=data["difficulty"],
            estimated_hours=data["estimated_hours"],
        )
        for day, data in sorted(day_store.items())
    ]


# ---------------------------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------------------------

_STUDY_PLAN_PROMPT = PromptTemplate(
    input_variables=["key_topics", "study_days"],
    template=(
        "You are an expert academic tutor specializing in personalized learning plans.\n\n"
        "Create a structured, balanced study plan based on the following:\n"
        "- Key topics to cover: {key_topics}\n"
        "- Total study days available: {study_days}\n\n"
        "Rules:\n"
        "1. Distribute topics as evenly as possible across all {study_days} days.\n"
        "2. Every day MUST have at least one topic.\n"
        "3. ALL provided topics must appear in the plan.\n"
        "4. Return EXACTLY {study_days} day entries — no more, no fewer.\n"
        "5. For each day, assess the overall difficulty of its content:\n"
        "   - 'easy'  : introductory or familiar material.\n"
        "   - 'medium': moderately complex concepts requiring focus.\n"
        "   - 'hard'  : advanced or abstract topics requiring significant effort.\n"
        "6. For each day, estimate the total hours of focused study required (0.5 – 8.0).\n"
        "   Base this on the complexity and number of topics assigned to that day.\n\n"
        "Respond with a JSON object that strictly follows this schema:\n"
        "{{\n"
        '  "study_plan": [\n'
        "    {{\n"
        '      "day": 1,\n'
        '      "topics": ["<topic>"],\n'
        '      "difficulty": "easy|medium|hard",\n'
        '      "estimated_hours": 2.0\n'
        "    }}\n"
        "  ]\n"
        "}}\n"
        "Return only the JSON. Do not include any explanation or markdown fencing."
    ),
)


def _build_prompt(sanitized: StudyPlannerInput) -> str:
    """Format the study plan prompt with sanitized input values.

    Args:
        sanitized: Sanitized and validated planner input.

    Returns:
        A ready-to-send prompt string.
    """
    topics_str = ", ".join(sanitized.key_topics)
    return _STUDY_PLAN_PROMPT.format(
        key_topics=topics_str,
        study_days=sanitized.study_days,
    )


# ---------------------------------------------------------------------------
# LLM Response Parser
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def _parse_llm_response(content: str) -> StudyPlanOutput:
    """Extract and parse a JSON study plan from a raw LLM response string.

    Handles responses that are:
    - Pure JSON strings.
    - JSON wrapped in markdown code fences (```json ... ```).

    Args:
        content: Raw text content from the LLM response.

    Returns:
        A validated :class:`StudyPlanOutput` instance.

    Raises:
        RuntimeError: If no valid JSON can be extracted or parsed.
    """
    # Strip markdown fences if present
    fence_match = _JSON_BLOCK_RE.search(content)
    json_str = fence_match.group(1).strip() if fence_match else content.strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.error("Failed to decode LLM JSON response: %s\nContent: %s", exc, content[:500])
        raise RuntimeError(f"LLM returned invalid JSON: {exc}") from exc

    try:
        return StudyPlanOutput.model_validate(data)
    except Exception as exc:
        logger.error("LLM output failed Pydantic validation: %s", exc)
        raise RuntimeError(f"LLM output schema mismatch: {exc}") from exc


# ---------------------------------------------------------------------------
# LLM Factory
# ---------------------------------------------------------------------------


def _build_llm() -> ChatOpenAI:
    """Initialise a ChatOpenAI instance backed by OpenRouter (Gemini 2.5 Flash).

    Reads credentials and model config from environment variables:
    - OPENAI_API_KEY  : OpenRouter API key (required)
    - LLM_BASE_URL    : API base URL (default: https://openrouter.ai/api/v1)
    - LLM_MODEL       : Model identifier (default: google/gemini-2.5-flash)

    Returns:
        Configured :class:`ChatOpenAI` instance.

    Raises:
        EnvironmentError: If the API key environment variable is missing.
    """
    api_key = os.environ.get("PLANNER_OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "PLANNER_OPENROUTER_API_KEY is not set. "
            "Check your .env file."
        )

    base_url = os.environ.get(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    model = os.environ.get(
        "PLANNER_MODEL",
        "google/gemini-2.5-flash",
    )

    temperature = float(
        os.environ.get("PLANNER_TEMPERATURE", "0.3")
    )


    return ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=temperature,
        max_tokens=4096,
        default_headers={
            "HTTP-Referer": "https://ai-study-buddy.app",
            "X-Title": "AI Study Buddy",
        },
    )


# ---------------------------------------------------------------------------
# Study Planner Agent (LangGraph Node)
# ---------------------------------------------------------------------------


def study_planner_agent(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: Study Planner Agent.

    Pipeline:
        1. Extract ``key_topics`` and ``study_days`` from state.
        2. Security: validate → sanitize → detect injection.
        3. Build LLM prompt.
        4. Invoke LLM with structured output (topics, difficulty, estimated_hours).
        5. Security: validate LLM output.
        6. Apply spaced repetition (pure Python post-processing).
        7. Return only ``study_plan``.

    Args:
        state: The LangGraph shared state dictionary. Required keys:
               ``key_topics`` (list[str]) and ``study_days`` (int).

    Returns:
        ``{"study_plan": [{"day": int, "topics": [...], "difficulty": str,
        "estimated_hours": float}, ...]}``

    Raises:
        ValueError: On input/output validation failure or injection detection.
        EnvironmentError: If ``OPENROUTER_API_KEY`` is absent.
        RuntimeError: If the LLM invocation or response parsing fails.
    """
    logger.info("Study Planner Agent: invoked.")

    # ------------------------------------------------------------------
    # Step 1 – Extract only the relevant state fields
    # ------------------------------------------------------------------
    raw_input: dict[str, Any] = {
        "key_topics": state.get("key_topics"),
        "study_days": state.get("study_days"),
    }

    # ------------------------------------------------------------------
    # Step 2 – Security: validate → sanitize → injection check
    # ------------------------------------------------------------------
    validated = validate_input(raw_input)
    sanitized = sanitize_input(validated)
    detect_prompt_injection(sanitized.key_topics)

    logger.debug(
        "Security checks passed. topics=%s, days=%d",
        sanitized.key_topics,
        sanitized.study_days,
    )

    # ------------------------------------------------------------------
    # Step 3 – Build the LLM prompt
    # ------------------------------------------------------------------
    prompt_text = _build_prompt(sanitized)

    # ------------------------------------------------------------------
    # Step 4 – Invoke the LLM and parse JSON manually
    # (with_structured_output uses OpenAI function-calling which OpenRouter
    #  proxies unreliably for Gemini — plain invoke + JSON extraction is safer)
    # ------------------------------------------------------------------
    try:
        llm = _build_llm()
        raw_response = llm.invoke(prompt_text)
        llm_output: StudyPlanOutput = _parse_llm_response(raw_response.content)
    except EnvironmentError:
        raise
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.error("LLM invocation failed: %s", exc)
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Step 5 – Security: validate LLM output
    # ------------------------------------------------------------------
    validated_output = validate_output(llm_output, sanitized.study_days)

    # ------------------------------------------------------------------
    # Step 6 – Apply spaced repetition (pure Python, no LLM)
    # ------------------------------------------------------------------
    enriched_plan = apply_spaced_repetition(validated_output.study_plan)

    # ------------------------------------------------------------------
    # Step 7 – Return ONLY the study_plan field (never pollute state)
    # ------------------------------------------------------------------
    result = {"study_plan": [entry.model_dump() for entry in enriched_plan]}

    logger.info(
        "Study Planner Agent: done. %d day(s) planned.",
        len(result["study_plan"]),
    )
    return result

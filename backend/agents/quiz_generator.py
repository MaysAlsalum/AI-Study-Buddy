import json
import re

from core.llm import call_llm,LLMError

SYSTEM_PROMPT = (
    "You are a quiz-generation engine for a study app. "
    "You ALWAYS respond with a single valid JSON object and NOTHING else. "
    "No markdown code fences, no explanations, no text before or after the JSON. "
    "If you are unsure about a value, still produce valid JSON with your best answer."
)



def _build_prompt(summary:str , key_topics:list , num_mcq:int , num_short:int, difficulty:str )-> str:
    topics_str=",".join(key_topics) if key_topics else "the material below"
    return f"""Based on the study summary and key topics below, generate a practice quiz.
    
    Study summary:
    \"\"\"{summary}\"\"\"
    
    Key topics to cover: {topics_str}
    Difficulty level: {difficulty}
    
    Generate exactly {num_mcq} multiple-choice questions and {num_short} short-answer questions,
    distributed across the key topics (don't focus on only one topic).
    
    Return ONLY a JSON object with this exact structure:
    {{
    "quiz": [
        {{
        "question": "string",
        "type": "mcq",
        "choices": ["string", "string", "string", "string"],
        "correct_answer": "string (must exactly match one of the choices)",
        "explanation": "string, 1-2 sentences"
        }},
        {{
        "question": "string",
        "type": "short_answer",
        "correct_answer": "string",
        "explanation": "string, 1-2 sentences"
        }}
    ]
    }}
    
    Rules:
    - "type" must be either "mcq" or "short_answer".
    - "mcq" items must have exactly 4 items in "choices", and "correct_answer" must be
    one of those 4 strings verbatim.
    - "short_answer" items must NOT include a "choices" key.
    - Do not repeat the same question twice.
    - Output raw JSON only, starting with {{ and ending with }}.
    """
def _extract_json(raw_text:str)->dict:
    text=raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
 
    # If there's stray text around the JSON object, grab the outermost {...}
    if not text.startswith("{"):
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)
 
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from LLM output: {e}\nRaw output:\n{raw_text[:800]}")
 
 
def _validate_quiz_schema(data: dict) -> None:
    """Raises ValueError if the parsed data doesn't match the expected contract."""
    if "quiz" not in data or not isinstance(data["quiz"], list):
        raise ValueError("Missing or invalid 'quiz' key (expected a list).")
 
    if len(data["quiz"]) == 0:
        raise ValueError("'quiz' list is empty.")
 
    for i, item in enumerate(data["quiz"]):
        if "question" not in item or "type" not in item or "correct_answer" not in item:
            raise ValueError(f"Quiz item {i} is missing required fields: {item}")
 
        if item["type"] not in ("mcq", "short_answer"):
            raise ValueError(f"Quiz item {i} has invalid type: {item['type']}")
 
        if item["type"] == "mcq":
            choices = item.get("choices")
            if not isinstance(choices, list) or len(choices) != 4:
                raise ValueError(f"Quiz item {i} (mcq) must have exactly 4 choices: {item}")
            if item["correct_answer"] not in choices:
                raise ValueError(
                    f"Quiz item {i} (mcq) correct_answer not found in choices: {item}"
                )
 
 
def generate_quiz(summary: str, key_topics: list, num_mcq: int = 3, num_short: int = 2,
                   difficulty: str = "medium", max_retries: int = 1) -> dict:
    """
    Main entry point for Agent 2.
 
    Args:
        summary: the summary text produced by Agent 1.
        key_topics: list of topic strings produced by Agent 1.
        num_mcq: number of multiple-choice questions to generate.
        num_short: number of short-answer questions to generate.
        difficulty: "easy" | "medium" | "hard".
        max_retries: how many times to retry if the LLM returns malformed JSON.
 
    Returns:
        dict matching the {"quiz": [...]} contract.
 
    Raises:
        LLMError if the API call itself fails.
        ValueError if the model repeatedly fails to produce valid, schema-correct JSON.
    """
    if not summary or not summary.strip():
        raise ValueError("summary cannot be empty.")
 
    prompt = _build_prompt(summary, key_topics, num_mcq, num_short, difficulty)
 
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            raw_output = call_llm(prompt, system_prompt=SYSTEM_PROMPT, temperature=0.4)
            parsed = _extract_json(raw_output)
            _validate_quiz_schema(parsed)
            return parsed
        except (ValueError, LLMError) as e:
            last_error = e
            if attempt < max_retries:
                # Tighten the prompt slightly on retry
                prompt += "\n\nIMPORTANT: Your previous output was invalid JSON or broke the schema. Return ONLY the raw JSON object, nothing else."
                continue
 
    raise ValueError(f"Failed to generate a valid quiz after {max_retries + 1} attempts: {last_error}")
 
"""
-----------example-----------
if __name__ == "__main__":
    # Quick manual test — run with: python -m agents.quiz_generator
    sample_summary = (
        "Machine Learning is a subset of AI focused on building systems that learn "
        "patterns from data. Supervised learning uses labeled data to train models, "
        "while unsupervised learning finds structure in unlabeled data. Overfitting "
        "occurs when a model memorizes training data instead of generalizing."
    )
    sample_topics = ["Supervised Learning", "Overfitting"]
 
    result = generate_quiz(sample_summary, sample_topics, num_mcq=2, num_short=1)
    print(json.dumps(result, indent=2))
"""
import json
from pathlib import Path

from backend.agents.summarizer import summarization_agent


pdf_path = Path(
    "backend/tests/sample.pdf"
)

test_state = {
    "pdf_path": str(pdf_path),
    "study_days": 3,
    "difficulty": "medium",
    "execution_logs": [],
}

result = summarization_agent(test_state)

print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
    )
)
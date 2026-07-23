import json
from pathlib import Path

from backend.core.workflow import graph


pdf_path = Path("backend/tests/sample.pdf")

test_state = {
    "raw_text": "",
    "pdf_path": str(pdf_path),
    "study_days": 5,
    "difficulty": "medium",
    "summary": "",
    "key_topics": [],
    "definitions": [],
    "quiz": [],
    "study_plan": [],
    "execution_logs": [],
}

result = graph.invoke(test_state)

print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False,
    )
)
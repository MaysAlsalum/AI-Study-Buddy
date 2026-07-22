import json

from backend.core.workflow import graph


test_state = {
    "raw_text": """
Cybersecurity is the practice of protecting computer systems, networks,
and sensitive information from cyber threats. Phishing attacks attempt
to trick users into revealing passwords or personal information.

Encryption converts readable data into an unreadable form. Firewalls
monitor network traffic and block unauthorized access. Multi-factor
authentication adds an extra layer of security by requiring more than
one verification method.
""",
    "study_days": 3,
    "difficulty": "medium",

    "summary": "",
    "key_topics": [],
    "definitions": [],
    "quiz": [],
    "study_plan": [],

    "blocked": False,
    "security_reason": "",
    "execution_logs": [],
}


result = graph.invoke(test_state)

print(json.dumps(result, indent=4, ensure_ascii=False))
import json

from backend.agents.summarizer import summarization_agent

test_state = {
    "raw_text": """
Cybersecurity is the practice of protecting computer systems, networks,
and sensitive information from cyber threats. One of the most common
types of attacks is phishing, where attackers trick users into revealing
passwords or personal information through fake emails or websites.

Encryption is used to convert readable data into an unreadable format,
ensuring that only authorized users with the correct key can access it.
Firewalls monitor incoming and outgoing network traffic and block
unauthorized access based on security rules.

Multi-factor authentication (MFA) improves security by requiring users
to verify their identity using more than one authentication method,
such as a password and a mobile verification code. Regular software
updates and security patches help fix vulnerabilities that attackers
might exploit.
""",
    "study_days": 4,
    "difficulty": "medium",
    "execution_logs": [],
}

result = summarization_agent(test_state)

print(json.dumps(result, indent=4, ensure_ascii=False))
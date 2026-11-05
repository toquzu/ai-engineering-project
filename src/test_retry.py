
import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

import clients.ollama_client as ollama_module
from clients.ollama_client import OllamaClient


class FakeClient:

    responses = []
    calls = 0

    def __init__(self, timeout=60):
        pass

    def chat(self, **kwargs):
        response_content = self.responses.pop(0)

        FakeClient.calls += 1

        return SimpleNamespace(
            message=SimpleNamespace(content=response_content),
            prompt_eval_count=10,
            eval_count=5,
        )


ollama_module.ollama.Client = FakeClient


valid_incident = {
    "category": "phishing",
    "severity": "medium",
    "status": "suspected",
    "asset": "employee account",
    "summary": "Suspicious phishing email.",
    "indicators": ["Fake login page"],
    "recommended_actions": [
        {
            "action": "Review authentication logs",
            "priority": 1
        }
    ],
    "needs_human_review": True,
}

invalid_incident = {
    "category": "phishing",
    "severity": "medium",
    "status": "suspected",
    "asset": "employee account",
    "summary": "Suspicious phishing email.",
    "indicators": [],
    "recommended_actions": [],
    # Missing needs_human_review
}


client = OllamaClient()

params = {
    "model": "llama3.2:3b",
    "temperature": 0.0,
    "top_p": 1.0,
    "timeout": 60,
}

# Test 1: First attempt fails, second succeeds
FakeClient.calls = 0
FakeClient.responses = [
    json.dumps(invalid_incident),
    json.dumps(valid_incident),
]

result = client.extract(
    text="Test incident",
    prompt="Test prompt",
    params=params,
)

print("TEST 1: Retry succeeds")
print("Status:", result.status)
print("Attempts:", result.validation_attempts)
print("API calls:", FakeClient.calls)
print("Incident exists:", result.incident is not None)

assert result.status == "success"
assert result.validation_attempts == 2
assert FakeClient.calls == 2
assert result.incident is not None


# Test 2: Both attempts fail
FakeClient.calls = 0
FakeClient.responses = [
    json.dumps(invalid_incident),
    json.dumps(invalid_incident),
]

result = client.extract(
    text="Test incident",
    prompt="Test prompt",
    params=params,
)

print("\nTEST 2: Both attempts fail")
print("Status:", result.status)
print("Attempts:", result.validation_attempts)
print("API calls:", FakeClient.calls)
print("Incident exists:", result.incident is not None)

assert result.status == "failed"
assert result.validation_attempts == 2
assert FakeClient.calls == 2
assert result.incident is None

print("\nALL TESTS PASSED!")

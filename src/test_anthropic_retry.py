
import json
import sys
from types import SimpleNamespace

sys.path.insert(0, "src")

import clients.anthropic_client as anthropic_module
from clients.anthropic_client import AnthropicClient


class FakeAnthropic:

    responses = []
    calls = 0

    def __init__(self, **kwargs):
        self.messages = self
        self.create = self.fake_create

    def fake_create(self, **kwargs):
        content = self.responses.pop(0)
        FakeAnthropic.calls += 1

        return SimpleNamespace(
            content=[
                SimpleNamespace(
                    type="text",
                    text=content
                )
            ],
            usage=SimpleNamespace(
                input_tokens=10,
                output_tokens=5
            )
        )


anthropic_module.anthropic.Anthropic = FakeAnthropic


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
    "needs_human_review": True
}

invalid_incident = {
    "category": "phishing",
    "severity": "medium",
    "status": "suspected",
    "asset": "employee account",
    "summary": "Suspicious phishing email.",
    "indicators": [],
    "recommended_actions": []
}


# Fake API key for the test
import os
os.environ["ANTHROPIC_API_KEY"] = "test-key"

client = AnthropicClient()

params = {
    "model": "claude-haiku-5-5",
    "max_tokens": 1500,
    "timeout": 60
}


# Test 1: Retry succeeds
FakeAnthropic.calls = 0
FakeAnthropic.responses = [
    json.dumps(invalid_incident),
    json.dumps(valid_incident)
]

result = client.extract(
    "Test incident",
    "Test prompt",
    params
)

print("TEST 1: Retry succeeds")
print("Status:", result.status)
print("Attempts:", result.validation_attempts)
print("API calls:", FakeAnthropic.calls)

assert result.status == "success"
assert result.validation_attempts == 2
assert FakeAnthropic.calls == 2


# Test 2: Both attempts fail
FakeAnthropic.calls = 0
FakeAnthropic.responses = [
    json.dumps(invalid_incident),
    json.dumps(invalid_incident)
]

result = client.extract(
    "Test incident",
    "Test prompt",
    params
)

print("\nTEST 2: Both attempts fail")
print("Status:", result.status)
print("Attempts:", result.validation_attempts)
print("API calls:", FakeAnthropic.calls)

assert result.status == "failed"
assert result.validation_attempts == 2
assert FakeAnthropic.calls == 2

print("\nALL ANTHROPIC TESTS PASSED!")

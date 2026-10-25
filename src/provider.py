
import json
from pathlib import Path

import ollama
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from schemas import Incident


BASE_DIR = Path(__file__).resolve().parent.parent


def load_prompt() -> str:
    path = BASE_DIR / "prompts" / "extract_v1.md"
    return path.read_text(encoding="utf-8")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_incident(
    text: str,
    model: str,
    temperature: float = 0.2,
    timeout: float = 60.0,
) -> Incident:
    client = ollama.Client(timeout=timeout)

    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": load_prompt()},
            {"role": "user", "content": text},
        ],
        format=Incident.model_json_schema(),
        options={"temperature": temperature},
    )

    content = response.message.content
    data = json.loads(content)
    return Incident.model_validate(data)

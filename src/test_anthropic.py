import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_DIR / "src"

sys.path.insert(0, str(SRC_DIR / "clients"))

from anthropic_client import extract_with_anthropic


prompt_path = PROJECT_DIR / "prompts" / "extract_v2.md"
prompt = prompt_path.read_text(encoding="utf-8")

test_text = """
An employee received an email asking them to verify
their bank account password using an external link.
The employee has not clicked the link.
"""

try:
    result = extract_with_anthropic(
        text=test_text,
        prompt=prompt,
    )

    print("ANTHROPIC CONNECTION OK")
    print(result.model_dump_json(indent=2))

except Exception as error:
    print("ERROR:", error)
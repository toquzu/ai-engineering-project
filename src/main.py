
import ollama
import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

response = ollama.chat(
    model=config["model"],
    messages=[
        {
            "role": "user",
            "content": "Hey pls, answer me."
        }
    ],
)

print(response["message"]["content"])
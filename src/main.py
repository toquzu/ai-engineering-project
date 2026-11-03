
import json
from pathlib import Path

import yaml

from provider import extract_incident


BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

input_file = BASE_DIR / config["input_dir"] / "texts.jsonl"
output_dir = BASE_DIR / config["output_dir"]
output_dir.mkdir(parents=True, exist_ok=True)

prompt_name = "extract_v2.md"
output_file = output_dir / "baseline_v2.jsonl"

success_count = 0
error_count = 0

with open(input_file, "r", encoding="utf-8") as file:
    texts = [json.loads(line) for line in file if line.strip()]

with open(output_file, "w", encoding="utf-8") as output:
    for item in texts:
        record = {"id": item["id"], "text": item["text"]}

        try:
            incident = extract_incident(
                text=item["text"],
                model=config["model"],
                prompt_name=prompt_name,
                temperature=config.get("temperature", 0.2),
                timeout=config.get("timeout", 60),
            )

            record["result"] = incident.model_dump(mode="json")
            record["error"] = None
            success_count += 1

            print(f'[{item["id"]}] OK: {incident.category.value}')

        except Exception as exc:
            record["result"] = None
            record["error"] = str(exc)
            error_count += 1

            print(f'[{item["id"]}] ERROR: {exc}')

        output.write(json.dumps(record, ensure_ascii=False) + "\n")
        output.flush()

print("\nProcessing finished.")
print(f"Total texts: {len(texts)}")
print(f"Successful: {success_count}")
print(f"Errors: {error_count}")
print(f"Results saved to: {output_file}")

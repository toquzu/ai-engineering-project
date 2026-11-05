
import json
import yaml
from pathlib import Path

from clients.ollama_client import OllamaClient
from clients.anthropic_client import AnthropicClient


BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration
with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

provider = config["provider"]
model = config["models"][provider]

# Select client
if provider == "ollama":
    client = OllamaClient()
elif provider == "anthropic":
    client = AnthropicClient()
else:
    raise ValueError(f"Unknown provider: {provider}")

# Load prompt
prompt_version = "v6"
prompt_path = BASE_DIR / "prompts" / "extract_v6.md"
prompt = prompt_path.read_text(encoding="utf-8")

# Load input data
input_path = BASE_DIR / config["input_dir"] / "texts.jsonl"

output_dir = BASE_DIR / config["output_dir"]
output_dir.mkdir(exist_ok=True)

# Run experiments
for experiment in config["experiments"]:

    experiment_name = experiment["name"]

    params = {
        "model": model,
        "temperature": experiment["temperature"],
        "top_p": experiment["top_p"],
        "timeout": config["timeout"],
        "max_tokens": config["max_tokens"],
    }

    output_path = output_dir / (
        f"benchmark_{provider}_{prompt_version}_{experiment_name}.jsonl"
    )

    processed = 0
    successful = 0
    failed = 0
    errors = 0

    print(f"\nStarting {experiment_name}")
    print(f"Prompt: {prompt_version}")
    print(f"Temperature: {params['temperature']}")
    print(f"Top P: {params['top_p']}")

    with open(input_path, "r", encoding="utf-8") as source, \
         open(output_path, "w", encoding="utf-8") as output:

        for line in source:
            if not line.strip():
                continue

            item = json.loads(line)
            processed += 1

            try:
                result = client.extract(
                    text=item["text"],
                    prompt=prompt,
                    params=params,
                )

                record = {
                    "id": item["id"],
                    "provider": result.provider,
                    "model": result.model,
                    "prompt_version": prompt_version,
                    "experiment": experiment_name,
                    "temperature": params["temperature"],
                    "top_p": params["top_p"],
                    "status": result.status,
                    "validation_attempts": result.validation_attempts,
                    "error": result.error,
                    "incident": (
                        result.incident.model_dump()
                        if result.incident is not None
                        else None
                    ),
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "latency_seconds": result.latency_seconds,
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                if result.status == "success":
                    successful += 1
                else:
                    failed += 1

                print(
                    f"Processed: {item['id']} | "
                    f"Status: {result.status} | "
                    f"Attempts: {result.validation_attempts}"
                )

            except Exception as error:
                errors += 1

                record = {
                    "id": item["id"],
                    "provider": provider,
                    "model": model,
                    "prompt_version": prompt_version,
                    "experiment": experiment_name,
                    "temperature": params["temperature"],
                    "top_p": params["top_p"],
                    "status": "failed",
                    "validation_attempts": 0,
                    "error": str(error),
                    "incident": None,
                    "input_tokens": None,
                    "output_tokens": None,
                    "latency_seconds": None,
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                print(f"Error on {item['id']}: {error}")

    print(f"\n{experiment_name} finished")
    print(f"Processed: {processed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print(f"Saved to: {output_path}")

print("\nAll experiments finished!")

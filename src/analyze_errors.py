
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_DIR = BASE_DIR / "results"
GOLDEN_PATH = BASE_DIR / "data" / "golden.jsonl"


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


golden = load_jsonl(GOLDEN_PATH)

for prompt_version in ["v2", "v3", "v4", "v5","v6"]:
    for config_name in ["config_A", "config_B"]:

        results_path = (
            RESULTS_DIR
            / f"benchmark_ollama_{prompt_version}_{config_name}.jsonl"
        )

        results = load_jsonl(results_path)

        results_by_id = {
            item["id"]: item
            for item in results
        }

        print(
            f"\n========== {prompt_version} / "
            f"{config_name} ERRORS =========="
        )

        error_count = 0

        for expected in golden:
            record = results_by_id.get(expected["id"])

            if record is None:
                print(f"\nID {expected['id']}: RESULT MISSING")
                error_count += 1
                continue

            if (
                record.get("status") != "success"
                or record.get("incident") is None
            ):
                print(f"\nID {expected['id']}: PROCESSING FAILED")
                error_count += 1
                continue

            actual = record["incident"]
            errors = []

            for field in ["category", "severity", "status"]:
                if actual.get(field) != expected.get(field):
                    errors.append(
                        f"{field}: expected='{expected.get(field)}', "
                        f"actual='{actual.get(field)}'"
                    )

            if actual.get("asset", "").lower() != expected["asset"].lower():
                errors.append(
                    f"asset: expected='{expected['asset']}', "
                    f"actual='{actual.get('asset', '')}'"
                )

            if errors:
                error_count += 1
                print(f"\nID {expected['id']}:")

                for error in errors:
                    print(f"  - {error}")

        print(
            f"\nTotal records with errors: "
            f"{error_count}/{len(golden)}"
        )

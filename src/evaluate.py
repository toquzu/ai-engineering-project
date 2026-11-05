
import json
import re
import csv
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parent.parent

GOLDEN_PATH = BASE_DIR / "data" / "golden.jsonl"
RESULTS_DIR = BASE_DIR / "results"

VERSIONS = ["v2", "v3", "v4", "v5", "v6"]
CONFIGS = ["config_A", "config_B"]


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def normalize(text):
    return re.findall(r"[^\W_]+", str(text).lower(), flags=re.UNICODE)


def token_f1(expected, actual):
    expected_tokens = set(normalize(expected))
    actual_tokens = set(normalize(actual))

    if not expected_tokens or not actual_tokens:
        return 0.0

    common = expected_tokens & actual_tokens

    precision = len(common) / len(actual_tokens)
    recall = len(common) / len(expected_tokens)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def percentile(values, percent):
    values = sorted(values)

    if not values:
        return 0.0

    position = (len(values) - 1) * percent / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)

    return (
        values[lower]
        + (values[upper] - values[lower]) * (position - lower)
    )


def evaluate(prompt_version, config_name, golden):

    path = RESULTS_DIR / (
        f"benchmark_ollama_{prompt_version}_{config_name}.jsonl"
    )

    if not path.exists():
        print(f"File not found: {path.name}")
        return None

    results = load_jsonl(path)

    results_by_id = {
        item["id"]: item
        for item in results
    }

    successful_results = {
        item_id: item
        for item_id, item in results_by_id.items()
        if item.get("status") == "success"
        and item.get("incident") is not None
    }

    valid_count = sum(
        1 for item in golden
        if item["id"] in successful_results
    )

    fields = ["category", "severity", "status"]

    scores = {field: [] for field in fields}
    asset_scores = []
    action_scores = []
    latencies = []

    for expected in golden:

        actual_record = successful_results.get(expected["id"])

        if actual_record is None:
            continue

        actual = actual_record["incident"]

        for field in fields:
            scores[field].append(
                actual.get(field) == expected.get(field)
            )

        asset_scores.append(
            token_f1(
                expected["asset"],
                actual.get("asset", "")
            )
        )

        recommended = actual.get("recommended_actions", [])

        best_action_score = max(
            (
                token_f1(expected["action"], item.get("action", ""))
                for item in recommended
            ),
            default=0.0
        )

        action_scores.append(best_action_score)

        latency = actual_record.get("latency_seconds")

        if latency is not None:
            latencies.append(latency)

    def accuracy(field):
        return (
            mean(scores[field]) * 100
            if scores[field]
            else 0.0
        )

    row = {
        "prompt": prompt_version,
        "config": config_name,
        "valid_outputs": valid_count,
        "valid_rate": valid_count / len(golden) * 100,
        "category_accuracy": accuracy("category"),
        "severity_accuracy": accuracy("severity"),
        "status_accuracy": accuracy("status"),
        "asset_f1": mean(asset_scores) * 100 if asset_scores else 0,
        "action_f1": mean(action_scores) * 100 if action_scores else 0,
        "avg_latency": mean(latencies) if latencies else 0,
        "p50_latency": percentile(latencies, 50),
        "p95_latency": percentile(latencies, 95),
    }

    print(f"\n========== {prompt_version} / {config_name} ==========")

    for key, value in row.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

    return row


def save_csv(rows):

    path = RESULTS_DIR / "evaluation_summary.csv"

    if not rows:
        print("No results to save.")
        return

    with open(path, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV saved: {path}")


def save_markdown(rows):

    path = RESULTS_DIR / "evaluation_summary.md"

    headers = [
        "Prompt",
        "Config",
        "Valid",
        "Valid %",
        "Category %",
        "Severity %",
        "Status %",
        "Asset F1 %",
        "Action F1 %",
        "Avg sec",
        "P50 sec",
        "P95 sec",
    ]

    lines = [
        "# Evaluation Summary",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for row in rows:

        values = [
            row["prompt"],
            row["config"],
            str(row["valid_outputs"]),
            f'{row["valid_rate"]:.1f}',
            f'{row["category_accuracy"]:.1f}',
            f'{row["severity_accuracy"]:.1f}',
            f'{row["status_accuracy"]:.1f}',
            f'{row["asset_f1"]:.1f}',
            f'{row["action_f1"]:.1f}',
            f'{row["avg_latency"]:.2f}',
            f'{row["p50_latency"]:.2f}',
            f'{row["p95_latency"]:.2f}',
        ]

        lines.append("| " + " | ".join(values) + " |")

    lines.extend([
        "",
        "## Metric notes",
        "",
        "- Valid %: percentage of Golden Set records with successful validated output.",
        "- Category, severity and status: exact-match accuracy.",
        "- Asset F1: token-based similarity using unique words.",
        "- Action F1: best token F1 between the expected action and one predicted action.",
        "- Avg, P50 and P95: latency measured on Golden Set records.",
        "- Golden Set contains only 10 examples, so results are preliminary.",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Markdown saved: {path}")


def main():

    golden = load_jsonl(GOLDEN_PATH)

    rows = []

    for prompt_version in VERSIONS:
        for config_name in CONFIGS:

            row = evaluate(
                prompt_version,
                config_name,
                golden
            )

            if row is not None:
                rows.append(row)

    save_csv(rows)
    save_markdown(rows)

    print("\nEvaluation finished!")


if __name__ == "__main__":
    main()

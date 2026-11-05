# AI-Based Cybersecurity Incident Analysis

## 1. Project Overview

The goal of this project is to build an AI-based system for analysing cybersecurity incident reports.

The system uses a Large Language Model (LLM) to extract structured information from incident descriptions.

The output contains:
- Incident category
- Severity
- Incident status
- Affected asset
- Incident summary
- Indicators
- Recommended actions
- Human review requirement

The system validates model responses using Pydantic and saves the results in JSONL format.

## 2. Technologies

The project uses:

- Python 3.13
- Ollama
- Llama 3.2 3B
- Anthropic API integration
- Pydantic
- JSON and JSONL
- YAML
- Tenacity
- Git and GitHub

The main tested model was `llama3.2:3b`, running locally through Ollama.

Anthropic integration was implemented, but a real benchmark was not performed because the API account had insufficient credit. Its retry logic was tested using a simulated API.

## 3. Project Architecture

The project is divided into several components:

- `src/main.py` - runs experiments and saves results.
- `src/schemas.py` - defines the Pydantic data schema.
- `src/clients/base.py` - defines the common LLM interface and Result structure.
- `src/clients/ollama_client.py` - communicates with the local Ollama model.
- `src/clients/anthropic_client.py` - implements Anthropic API integration.
- `src/evaluate.py` - calculates evaluation metrics.
- `src/analyze_errors.py` - analyses differences between predictions and expected results.
- `prompts/` - contains versioned extraction prompts.
- `data/` - contains incident reports and the Golden Set.
- `results/` - stores experiment results and evaluation summaries.

## 4. Dataset and Evaluation Method

The project uses:
- 30 incident reports for model experiments.
- 10 manually labelled examples in the Golden Set.

The Golden Set is used to compare model predictions with expected results.

Five prompt versions were evaluated: v2, v3, v4, v5 and v6.

Two parameter configurations were compared:

| Configuration | Temperature | Top P |
|---|---:|---:|
| Config A | 0.0 | 1.0 |
| Config B | 0.7 | 0.9 |

The evaluation uses the following metrics:

- Valid output rate - percentage of successfully validated responses.
- Category accuracy - exact match.
- Severity accuracy - exact match.
- Status accuracy - exact match.
- Asset similarity - token-based F1.
- Action similarity - best token-based F1 between the expected action and one predicted action.
- Average latency, P50 and P95 - response time measurements.

## 5. Experimental Results

The following table presents the results for all evaluated prompt versions.

| Prompt | Config | Valid % | Category % | Severity % | Status % | Asset F1 % | Action F1 % | Avg. sec |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v2 | A | 100 | 90 | 60 | 50 | 45.0 | 25.5 | 4.95 |
| v2 | B | 100 | 80 | 50 | 50 | 45.0 | 25.9 | 5.46 |
| v3 | A | 100 | 90 | 40 | 50 | 40.3 | 27.7 | 5.18 |
| v3 | B | 100 | 80 | 50 | 60 | 41.8 | 19.6 | 4.32 |
| v4 | A | 100 | 100 | 90 | 40 | 43.8 | 25.2 | 5.30 |
| v4 | B | 100 | 100 | 80 | 30 | 35.2 | 24.4 | 5.20 |
| v5 | A | 100 | 100 | 100 | 40 | 43.8 | 24.2 | 6.05 |
| v5 | B | 100 | 90 | 80 | 40 | 44.0 | 24.1 | 5.06 |
| v6 | A | 100 | 100 | 100 | 40 | 50.7 | 27.5 | 6.15 |
| v6 | B | 100 | 100 | 80 | 50 | 46.7 | 16.6 | 4.78 |

All configurations produced valid outputs for the 10 Golden Set examples.

The complete automatically generated results are available in:
- `results/evaluation_summary.csv`
- `results/evaluation_summary.md`

## 6. Error Analysis

The experiments showed that status classification was the most difficult part of the task.

Examples of errors in v6:

1. ID003: Multiple failed login attempts were sometimes classified as `reported` or `investigating` instead of `suspected`.

2. ID004: An ATM tamper warning was classified as `investigating` instead of `confirmed_alert` in Config A.

3. ID005: A user-reported problem with a banking application was sometimes classified as `suspected` instead of `reported`.

4. ID009: A potential data leak involving a personal cloud drive was sometimes classified as `reported` instead of `suspected`.

5. ID010: An endpoint protection system quarantined a suspicious file, but the model sometimes returned `confirmed_alert` or `investigating` instead of `blocked_by_control`.

Asset identification also remains difficult. The model sometimes returns descriptions that are too general or different from the expected wording.

The token-based F1 metric does not fully understand semantic similarity. Therefore, two descriptions with the same meaning can receive a lower score if they use different words.

## 7. Validation and Retry Mechanism

Both LLM clients use Pydantic validation.

The validation process works as follows:

1. The model generates a JSON response.
2. The response is parsed and validated.
3. If validation fails, the client sends the validation error and previous response to the model.
4. The model gets one additional attempt to correct the response.
5. If the second response is invalid, the result receives the `failed` status.

Both clients were tested using simulated model responses.

The tests confirmed:
- Successful correction after the first validation error.
- Correct `failed` status after two invalid responses.
- Exactly two model calls in the retry scenario.

The Python files also passed compilation using `py -m compileall src`.

## 8. Final Configuration Choice

The best quality results were obtained with prompt v6 and Config A.

Config A achieved:
- 100% category accuracy.
- 100% severity accuracy.
- 50.7% asset similarity F1.
- 27.5% action similarity F1.

Config B was faster:
- Average latency: 4.78 seconds.
- P50 latency: 4.67 seconds.
- P95 latency: 6.44 seconds.

However, Config B achieved lower action similarity and lower severity accuracy.

For this reason, v6 Config A is the preferred configuration when classification quality is more important than speed.

Config B can be considered when lower latency is more important.

## 9. Limitations and Future Improvements

The project has several limitations:

- The Golden Set contains only 10 examples.
- Status classification still needs improvement.
- Asset and recommended action extraction require further work.
- Token-based F1 does not fully measure semantic similarity.
- Anthropic was not evaluated using real API requests.
- The local model requires suitable hardware resources.

Future improvements could include:
- Expanding the Golden Set.
- Adding more difficult incident examples.
- Improving status classification rules.
- Using semantic evaluation for assets and recommended actions.
- Performing a real benchmark with a second model.
- Testing the system on a larger dataset.

## 10. Conclusion

The project demonstrates that a local LLM can extract structured information from cybersecurity incident reports.

Prompt engineering improved category and severity classification. The final v6 prompt achieved 100% category accuracy and up to 100% severity accuracy on the Golden Set.

However, status classification and recommended action extraction remain challenging.

The project also includes a common interface for different LLM providers, structured validation, one retry attempt, automated evaluation and error analysis.

The results are promising, but further testing on a larger dataset is necessary before using the system in a real production environment.

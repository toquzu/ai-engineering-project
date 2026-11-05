# Prompt Changelog

## v1
- Initial version of the incident extraction prompt.
- Used as the baseline for evaluation.

## v2
- Improved category definitions.
- Added clearer severity classification rules.
- Added instructions to avoid unsupported assumptions.
- Improved asset identification and recommended actions.
- Added clearer JSON output requirements.

### Reason for changes
The v1 evaluation showed low category and severity accuracy.
The v2 prompt was introduced to improve classification consistency.

### Initial evaluation results
- Category accuracy improved from 20% to 80%.
- Severity accuracy improved from 20% to 60%.
- Evaluation was performed on 10 golden examples.

## v3
- Aligned status definitions with the Pydantic schema.
- Added clearer rules for distinguishing incident statuses.
- Improved consistency between prompt instructions and allowed enum values.

### Reason for changes
The v2 prompt contained differences between its status descriptions and the actual schema.

### Evaluation results
- Category accuracy: 80-90%.
- Severity accuracy: 40-50%.
- Status accuracy: 40-50%.
- No clear overall improvement compared with v2.

## v4
- Strengthened category classification rules.
- Improved severity definitions.
- Added more specific asset identification instructions.
- Clarified the difference between reported and investigating incidents.

### Reason for changes
Previous experiments showed classification errors, especially in category, severity and status.

### Evaluation results
- Category accuracy: 100% in both configurations.
- Severity accuracy: 90% in Config A and 80% in Config B.
- Status accuracy: 50% in Config A and 40% in Config B.

## v5
- Reworked status classification rules.
- Added clearer distinctions between suspected, reported, investigating, confirmed_alert and blocked_by_control.
- Added rules to avoid assuming that an investigation has started.

### Reason for changes
Status classification remained one of the main sources of errors.

### Evaluation results
- Category accuracy: 100% in Config A and 90% in Config B.
- Severity accuracy: 100% in Config A and 80% in Config B.
- Status accuracy: 30% in both configurations.
- The changes did not solve the status classification problem.

## v6
- Further improved status definitions.
- Clarified the difference between reported and suspected incidents.
- Added rules for distinguishing confirmed alerts from successfully blocked threats.
- Improved asset identification by preserving specific details from the source text.

### Reason for changes
Previous experiments showed that status classification and asset identification still needed improvement.

### Evaluation results
- Category accuracy: 100% in both configurations.
- Severity accuracy: 100% in Config A and 80% in Config B.
- Status accuracy: 40% in Config A and 50% in Config B.
- Asset similarity F1: 50.7% in Config A and 46.7% in Config B.
- Action similarity F1: 27.3% in Config A and 16.6% in Config B.
- Config B had lower average latency: 4.78 seconds compared with 6.15 seconds for Config A.

## General conclusions
- Prompt improvements significantly increased category and severity accuracy.
- Status classification remains the main weakness.
- Asset identification improved, but exact matching is still difficult.
- Config A generally provides better classification quality.
- Config B is faster in the v6 experiment.
- All v2-v6 configurations produced valid JSON outputs on the 10-example Golden Set.

### Evaluation notes
- Golden Set contains 10 examples.
- One example represents 10 percentage points in accuracy.
- Asset similarity uses token-based F1.
- Action similarity uses the best per-action token F1.
- Results should be treated as preliminary because the evaluation dataset is small.
# Synthetic Financial Statement Violation Dataset

## Overview

This folder contains synthetic financial statements for evaluating accounting-violation detection, rule identification, error localization, and explanation generation. The full dataset additionally preserves the corresponding original statements for auditing and transformation analysis.

Each synthetic statement contains one intentionally introduced accounting, classification, presentation, or reconciliation error. These synthetic errors are created only for research and are not claims about the reporting quality of the represented companies.

## Dataset Summary

- **Companies:** 102
- **Synthetic rules:** 50
- **Original–synthetic pairs:** 5,100
- **Model-ready examples:** 10,200
- **`VIOLATION` examples:** 5,100
- **`NO_VIOLATION` examples:** 5,100
- **Pairs per company:** 50
- **Pairs per rule:** 102
- **Economic sectors:** 11

## Files

| File | Purpose |
|---|---|
| `synthetic_financial_statement_cases_simplified.jsonl.zip` | Recommended model-ready dataset |
| `final_financial_statement_cases_102_companies.json.zip` | Full dataset with provenance and quality-control fields |
| `example_usage.py` | Minimal loading and prompt example |
| `build_simplified_dataset.py` | Rebuilds the simplified release from the full dataset |

The simplified file is recommended for most users. The full file is intended for dataset auditing, provenance inspection, and detailed transformation analysis.

## Simplified Format

The recommended dataset is compressed JSON Lines. It contains one JSON object per line and only four top-level fields:

| Field | Description |
|---|---|
| `id` | Unique example identifier, including its original/synthetic variant |
| `input` | One financial statement presented to the model |
| `label` | Binary label and, for violations, rule-level ground truth |
| `metadata` | Minimal grouping information for evaluation |

Example structure:

```json
{
  "id": "AAPL_BS-001::synthetic",
  "input": {
    "title_rows": [],
    "columns": [],
    "rows": []
  },
  "label": {
    "classification": "VIOLATION",
    "rule_id": "BS-04",
    "violation": "PP&E classified as a current asset",
    "synthetic_transformation": "Move PP&E from non-current assets into current assets.",
    "expected_effect": "Total assets unchanged; classification intentionally wrong.",
    "affected_line_items": ["Property, plant and equipment, net"]
  },
  "metadata": {
    "pair_id": "AAPL_BS-001",
    "variant": "synthetic",
    "ticker": "AAPL",
    "statement_type": "Balance Sheet",
    "sector": "Information Technology"
  }
}
```

Statement rows retain only their line item, section, section-header indicator, and reported values. Internal source-row numbers, highlights, change flags, filing metadata, and quality-control fields are excluded. Labels such as `ORIGINAL REPORTED` and `SYNTHETIC VIOLATION` are also removed from the model input to prevent answer leakage.

Each pair produces two examples:

```text
original statement  -> NO_VIOLATION
synthetic statement -> VIOLATION
```

For an original example, `rule_id`, `violation`, `synthetic_transformation`, and `expected_effect` are `null`, and `affected_line_items` is empty.

## Recommended Tasks

### 1. Binary Violation Detection

```text
input -> label.classification
```

This task uses all 10,200 examples and has an exactly balanced label distribution.

### 2. Rule Identification

Using only examples for which `label.classification == "VIOLATION"`:

```text
input -> label.rule_id
```

### 3. Violation Identification

Using only violation examples:

```text
input -> label.violation
```

### 4. Joint Diagnosis

Using only violation examples, predict the rule ID, violation, affected lines, and expected effect.

The fields inside `label` must never be included in the model input during evaluation.

## Quick Start

The example script reads the compressed JSONL file directly; manual extraction is not required.

```bash
python example_usage.py
```

Inspect another pair or print the complete model prompt:

```bash
python example_usage.py --sample-index 10
python example_usage.py --sample-index 10 --show-prompt
```

The script requires only the Python standard library.

## Minimal Python Usage

```python
import json
import zipfile

path = "synthetic_financial_statement_cases_simplified.jsonl.zip"

with zipfile.ZipFile(path) as archive:
    jsonl_name = next(
        name for name in archive.namelist()
        if name.endswith(".jsonl")
    )
    with archive.open(jsonl_name) as file:
        first_sample = json.loads(file.readline())

print(first_sample["id"])
print(first_sample["input"])
print(first_sample["label"])
```

## Rebuilding the Simplified Dataset

```bash
python build_simplified_dataset.py \
  --input final_financial_statement_cases_102_companies.json.zip \
  --output synthetic_financial_statement_cases_simplified.jsonl \
  --zip
```

## Evaluation Recommendations

- Split by `metadata.ticker` to test generalization to unseen companies.
- Split by `label.rule_id` to test generalization to unseen violation types.
- Keep both examples sharing the same `metadata.pair_id` in the same split.
- Prefer company-level splitting because the same original company statement may be reused across multiple rule pairs.
- Report results by rule and statement type in addition to overall performance.
- Use the full dataset only when provenance, detailed line changes, or quality-control metadata is required.

## Full Dataset

The full archive preserves company and filing metadata, original and synthetic statements, detailed `line_changes`, `ground_truth`, source information, and `quality_control`. It is substantially larger and contains many fields intended for dataset maintenance rather than ordinary modeling.

The full dataset contains 5,100 paired records. The simplified release expands each pair into one original `NO_VIOLATION` example and one synthetic `VIOLATION` example. Here, `NO_VIOLATION` means that the original statement does not contain the intentionally introduced violation represented by its paired synthetic case; it is not a universal audit opinion that the filing contains no issue of any kind.

## Limitations

- Synthetic errors may not represent the full ambiguity of real regulatory cases.
- Some cases use documented hypothetical assumptions when the source statement lacks the event needed to instantiate a rule.
- Statement layouts and terminology vary across companies and sectors.
- Some fiscal-year metadata in the full dataset is missing or anomalous.
- Automated validation supports quality control but does not replace accounting judgment.

## Citation

A formal citation will be added when the associated paper is released. Until then, please cite the repository URL and the dataset version or commit used in the experiment.

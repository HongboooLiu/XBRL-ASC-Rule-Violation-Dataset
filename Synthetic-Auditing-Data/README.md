# Synthetic Financial Statement Violation Dataset

## Overview

This folder contains paired original and synthetic financial statements for evaluating accounting-violation detection, rule identification, error localization, and explanation generation.

Each synthetic statement contains one intentionally introduced accounting, classification, presentation, or reconciliation error. These synthetic errors are created only for research and are not claims about the reporting quality of the represented companies.

## Dataset Summary

- **Companies:** 102
- **Synthetic rules:** 50
- **Original–synthetic pairs:** 5,100
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
| `id` | Unique company–case identifier |
| `input` | Original and synthetic financial statements presented to the model |
| `label` | Rule and ground-truth description of the introduced violation |
| `metadata` | Minimal grouping information for evaluation |

Example structure:

```json
{
  "id": "AAPL_BS-001",
  "input": {
    "original_statement": {},
    "synthetic_statement": {}
  },
  "label": {
    "rule_id": "BS-04",
    "violation": "PP&E classified as a current asset",
    "synthetic_transformation": "Move PP&E from non-current assets into current assets.",
    "expected_effect": "Total assets unchanged; classification intentionally wrong.",
    "affected_line_items": ["Property, plant and equipment, net"]
  },
  "metadata": {
    "ticker": "AAPL",
    "statement_type": "Balance Sheet",
    "sector": "Information Technology"
  }
}
```

Statement rows retain only their line item, section, section-header indicator, and reported values. Internal source-row numbers, highlights, change flags, filing metadata, and quality-control fields are excluded. Labels such as `ORIGINAL REPORTED` and `SYNTHETIC VIOLATION` are also removed from the model input to prevent answer leakage.

## Recommended Task

Provide `input` to the model and predict the information in `label`:

```text
original statement + synthetic statement
    -> rule ID + violation + affected lines + expected effect
```

The fields inside `label` must not be included in the model input during evaluation.

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
- Keep each original–synthetic pair intact.
- Report results by rule and statement type in addition to overall performance.
- Use the full dataset only when provenance, detailed line changes, or quality-control metadata is required.

## Full Dataset

The full archive preserves company and filing metadata, original and synthetic statements, detailed `line_changes`, `ground_truth`, source information, and `quality_control`. It is substantially larger and contains many fields intended for dataset maintenance rather than ordinary modeling.

All 5,100 full records are labeled `VIOLATION` because each record represents an original–synthetic comparison. The original statement should not be treated as an independently verified universal `NO_VIOLATION` filing; it is the unchanged baseline for the particular synthetic transformation.

## Limitations

- Synthetic errors may not represent the full ambiguity of real regulatory cases.
- Some cases use documented hypothetical assumptions when the source statement lacks the event needed to instantiate a rule.
- Statement layouts and terminology vary across companies and sectors.
- Some fiscal-year metadata in the full dataset is missing or anomalous.
- Automated validation supports quality control but does not replace accounting judgment.

## Citation

A formal citation will be added when the associated paper is released. Until then, please cite the repository URL and the dataset version or commit used in the experiment.

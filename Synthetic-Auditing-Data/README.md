# Synthetic Financial Statement Violation Dataset

## Overview

This folder contains synthetic financial-statement violations constructed from financial statements in publicly available annual filings. Each record pairs an original statement with a modified version containing one intentionally introduced accounting, classification, presentation, or reconciliation error.

The dataset is intended for evaluating financial-statement reasoning, violation detection, rule identification, error localization, and explanation generation.

> The synthetic violations are created solely for research. They are not claims that the companies made these errors in their reported filings.

## Dataset Summary

- **Companies:** 102
- **Rules:** 50
- **Synthetic violation records:** 5,100
- **Records per company:** 50
- **Records per rule:** 102
- **Economic sectors:** 11
- **Format:** JSON

The main dataset file is:

```text
final_financial_statement_cases_102_companies.json
```

## Record Structure

The JSON file is a list of records. Each record contains one original–synthetic statement pair.

| Field | Description |
|---|---|
| `record_id` | Unique identifier for the company–case combination |
| `company` | Company name |
| `ticker` | Company ticker |
| `fiscal_year` | Fiscal year associated with the source statement, when available |
| `rule_id` | Standardized synthetic rule identifier shared across companies |
| `statement_type` | Affected statement or comparison type |
| `case_name` | Short description of the introduced violation |
| `label` | Label of the synthetic statement; currently `VIOLATION` for every record |
| `original_statement` | Statement before modification |
| `synthetic_statement` | Statement containing the intentional violation |
| `line_changes` | Structured evidence describing changed, added, removed, or moved lines |
| `ground_truth` | Violation description, transformation, and expected effect |
| `sector` | Economic sector of the company |
| `source` | Source-filing metadata |
| `quality_control` | Dataset-construction and validation metadata |

For cross-company analysis, use `rule_id` as the common rule identifier. Some company-specific `case_id` values are not standardized across the complete dataset.

### Statement Objects

Both `original_statement` and `synthetic_statement` contain:

| Field | Description |
|---|---|
| `title_rows` | Statement title, company, reporting period, and unit information |
| `columns` | Ordered statement columns |
| `rows` | Ordered financial-statement rows and values |

Each row typically includes its line item, section, cell values, and indicators showing whether it was changed or highlighted.

### Ground Truth

The `ground_truth` object contains three fields:

- `violation`: the accounting or presentation problem;
- `synthetic_transformation`: how the original statement was modified; and
- `expected_effect`: the expected financial-statement consequence.

`line_changes` provides more granular transformation evidence. These annotations should normally be used as targets or evaluation references, not included in the model input.

## Task Configurations

### 1. Paired Violation Analysis

Provide both statements and ask the model to identify the violation introduced in the synthetic version:

```text
Original statement + synthetic statement
    -> violated rule + affected lines + explanation
```

### 2. Binary Violation Detection

Derive two examples from each record:

```text
original_statement  -> NO_VIOLATION
synthetic_statement -> VIOLATION
```

This produces 10,200 statement examples. The two examples derived from the same record must remain in the same train, validation, or test split.

### 3. Rule Identification

Provide the synthetic statement without `rule_id`, `case_name`, `line_changes`, or `ground_truth`, and ask the model to predict the applicable `rule_id`.

## Important Label Note

All 5,100 top-level records have the label `VIOLATION` because each record represents a synthetic violation. A binary classifier should therefore not be trained directly on the top-level `label` field alone. Use the original and synthetic statements as paired negative and positive examples, as described above.

## Quick Start

The included script loads the dataset, prints its main statistics, displays one record, and builds a paired model prompt.

```bash
python example_usage.py
```

Inspect a different record:

```bash
python example_usage.py --sample-index 10
```

Use another dataset location:

```bash
python example_usage.py --json /path/to/dataset.json --sample-index 10
```

The example requires only the Python standard library.

## Minimal Python Usage

```python
import json

with open(
    "final_financial_statement_cases_102_companies.json",
    encoding="utf-8",
) as file:
    records = json.load(file)

sample = records[0]

print(sample["record_id"])
print(sample["rule_id"])
print(sample["case_name"])
print(sample["ground_truth"])
```

## Evaluation Recommendations

- Split by company when evaluating generalization to unseen issuers.
- Split by `rule_id` when evaluating generalization to unseen violation types.
- Keep each original–synthetic pair in the same split.
- Do not expose `line_changes`, `ground_truth`, `case_name`, or `quality_control` in the input when they are evaluation targets.
- Report performance by rule category and statement type in addition to overall performance.

## Limitations

- The errors are synthetic and may not capture the full complexity of real SEC reporting violations.
- Some cases use documented hypothetical assumptions when the source filing lacks the event needed to instantiate a rule.
- Statement structure varies across companies and industries.
- Sector coverage is broad and approximately, but not perfectly, balanced.
- Some `fiscal_year` metadata is missing or anomalous; users should validate this field before using it for year-based analysis.
- Automated checks support dataset quality control but do not replace accounting judgment.

## Citation

A formal citation will be added when the associated paper is released. Until then, please cite the repository URL and the dataset version or commit used in your experiment.

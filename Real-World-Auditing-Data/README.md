# ASC Table Compliance Benchmark

## Overview

This repository contains a dataset for evaluating whether a financial statement complies with a specified Accounting Standards Codification (ASC) rule.

Each sample provides:

- an ASC rule and a financial statement table as the model input; and
- a binary compliance label: `VIOLATION` or `NO_VIOLATION`.

The current release contains 1,092 samples: 563 violation cases and 529 matched non-violation controls.

## Dataset File

The main file is:

```text
balanced_table_dataset_simplified.csv
```

It contains four columns:

| Column | Description |
|---|---|
| `sample_id` | Unique sample identifier |
| `input` | ASC rule and financial statement table presented to the model |
| `label` | Ground-truth label: `VIOLATION` or `NO_VIOLATION` |
| `pair_id` | Identifier linking a violation case to its matched control |

The first three columns are sufficient for standard evaluation. `pair_id` is included to support paired analysis and leakage-safe data splitting.

## Task

Given the `input`, predict the corresponding `label`:

```text
ASC rule + financial statement table -> VIOLATION / NO_VIOLATION
```

## Example

```text
ASC Rule:
230-10-45-28

Financial Statement:
<financial statement table in Markdown>

Label:
VIOLATION
```

## Dataset Construction

Violation samples are derived from SEC comment-letter cases in Audit Analytics and linked to the corresponding SEC filings. We retain cases in which the identified ASC violation is directly observable in a primary financial statement table.

Non-violation samples are matched peer-company filings selected using filing period, form type, industry, relevant statement type, and target ASC rule. A `NO_VIOLATION` label means that no violation associated with the target rule was identified under the dataset's screening procedure; it is not a general audit opinion on the filing.

Financial statement tables are extracted from SEC filings and converted to Markdown.

## Loading the Dataset

```python
import pandas as pd

df = pd.read_csv(
    "balanced_table_dataset_simplified.csv",
    low_memory=False,
)

print(df.shape)
print(df["label"].value_counts())

sample = df.iloc[0]
print(sample["input"])
print(sample["label"])
```

## Evaluation Note

When creating train, validation, and test sets, split by `pair_id` rather than by individual rows. This prevents the two members of a matched pair from appearing in different splits.

## Citation

A formal citation will be added when the associated paper is released. Until then, please cite the repository URL and the dataset version or commit used in your experiment.

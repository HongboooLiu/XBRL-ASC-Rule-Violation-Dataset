# ASC Table Compliance Benchmark

## Overview

This repository contains a financial-statement compliance benchmark constructed from **Audit Analytics (AA) SEC comment-letter data** and SEC EDGAR filings.

The current release contains **1,092 samples**:

- **563 `VIOLATION` samples**: confirmed ASC-related violations that are directly reflected in financial statement tables.
- **529 `NO_VIOLATION` samples**: matched peer-company controls with no known violation for the paired ASC task under the current screening procedure.

The benchmark is intended for evaluating whether large language models can identify accounting-rule violations directly from financial statement tables.

The main dataset files are:

```text
balanced_table_dataset_with_markdown.csv
balanced_table_input.md
```

The repository also includes:

```text
example_usage.py
requirements.txt
```

---

## Repository Structure

```text
ASC-Table-Compliance-Benchmark/
│
├── README.md
├── example_usage.py
├── requirements.txt
├── balanced_table_dataset_with_markdown.csv
└── balanced_table_input.md
```

> The ZIP distributed with this README contains the repository documentation and example code.  
> Place the two dataset files above in the same directory before running the example.

---

## Dataset Construction

### 1. Audit Analytics SEC comment letters

The dataset starts from SEC comment-letter cases collected through **Audit Analytics (AA)**.

The upstream data contains information such as:

- SEC question letters,
- company response letters,
- referenced SEC filings,
- accounting-related comments,
- and ASC rule references.

The comment-letter text itself is not used as the final financial-statement input. Instead, the referenced SEC filing is retrieved from EDGAR so that the actual reported financial statement can be reconstructed.

```text
Audit Analytics SEC Comment Letters
                ↓
Accounting-related cases
                ↓
ASC rule identification and adjudication
                ↓
Referenced SEC filing
                ↓
Financial statement extraction
```

### 2. Confirmed table-level violations

The upstream screening pipeline determines whether an identified ASC violation is directly visible in one or more of the four primary financial statements:

- `BALANCE_SHEET`
- `INCOME_STATEMENT`
- `CASH_FLOW_STATEMENT`
- `STATEMENT_OF_EQUITY`

Only confirmed cases whose violations can be directly localized to the financial statement tables are retained as positive samples.

This produces:

```text
563 confirmed table-level violation samples
```

Each positive sample preserves the relevant company, SEC filing, ASC rule(s), statement type(s), and violation metadata.

### 3. SEC financial statement extraction

For each sample, the referenced SEC filing is retrieved from EDGAR.

The extraction pipeline primarily follows:

```text
SEC filing
   ↓
FilingSummary.xml
   ↓
R*.htm statement reports
   ↓
Primary financial statement tables
```

When the filing summary is missing or incomplete, the pipeline falls back to the filing's primary HTML document.

Multi-level SEC/pandas headers are flattened into Markdown-safe column names so the resulting tables can be used directly as LLM inputs.

### 4. Matched non-violation controls

To reduce class imbalance and enable meaningful binary evaluation, positive samples are paired with peer-company control filings whenever a defensible match can be found.

For each positive sample, the matching process attempts to find a different company with:

1. a similar industry, prioritizing exact SEC SIC;
2. the same filing form, such as `10-K` with `10-K` or `10-Q` with `10-Q`;
3. the same fiscal year, with the same quarter preferred for quarterly filings;
4. the same relevant financial statement type(s);
5. the same target ASC rule(s); and
6. no known violation in the existing screening results for the selected filing.

Example:

```text
Positive Sample
Company A
FY2024
10-K
Income Statement
ASC 260-10-45-5
Label: VIOLATION

          ↕

Matched Control
Company B
Same/similar industry
FY2024
10-K
Income Statement
ASC 260-10-45-5
Label: NO_VIOLATION
```

The current release contains **529 matched controls**. Samples for which no sufficiently defensible control was found are not automatically labeled as negative.

---

## Current Dataset Statistics

| Label | Samples |
|---|---:|
| `VIOLATION` | 563 |
| `NO_VIOLATION` | 529 |
| **Total** | **1,092** |

---

## Main CSV Fields

Important columns in `balanced_table_dataset_with_markdown.csv` include:

| Field | Description |
|---|---|
| `sample_id` | Unique sample identifier |
| `pair_id` | Links a positive sample with its matched control |
| `label` | `VIOLATION` or `NO_VIOLATION` |
| `source_sample_id` | Original positive sample ID used for pairing |
| `Name` | Company name |
| `Ticker` | Company ticker |
| `CIK` | SEC Central Index Key |
| `SIC` | SEC Standard Industrial Classification code |
| `Fiscal Year` | Fiscal year of the filing |
| `Filing Type` | Filing form, e.g. `10-K` or `10-Q` |
| `Accession` | SEC accession number |
| `Filing URL` | SEC EDGAR filing URL |
| `target_asc_rule_ids` | ASC rule(s) associated with the task |
| `target_statement_types` | Relevant statement type(s) |
| `table_input` | Extracted financial statement table(s) in Markdown |
| `Led_to_Restatement` | Restatement indicator when available |
| `industry_match` | Industry matching level for controls |
| `control_status` | Control construction status |

Comment-letter-specific fields are retained for positive samples and may be blank for matched controls.

---

## Intended Tasks

### Rule Verification

```text
Financial statement table
+ one ASC rule
→ VIOLATION / NO_VIOLATION
```

### Rule Identification

```text
Financial statement table
+ multiple candidate ASC rules
→ identify the violated rule(s)
```

### Open-World Joint Diagnosis

```text
Financial statement table only
→ detect whether a violation exists
→ identify the applicable ASC rule
→ locate affected line item(s)
→ explain the issue
```

---

# Quick Start

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

The example only requires `pandas`.

---

## 2. Put the dataset files in the repository folder

Your directory should look like:

```text
ASC-Table-Compliance-Benchmark/
│
├── README.md
├── example_usage.py
├── requirements.txt
├── balanced_table_dataset_with_markdown.csv
└── balanced_table_input.md
```

---

## 3. Run the example

```bash
python example_usage.py
```

This will:

1. load the CSV;
2. print the number of samples;
3. print the label distribution;
4. show one example sample;
5. print the ASC rule, statement type, and Markdown financial statement table;
6. build a minimal prompt that can be sent to an LLM.

You can inspect a different row with:

```bash
python example_usage.py --sample-index 10
```

Or specify a different CSV path:

```bash
python example_usage.py \
  --csv /path/to/balanced_table_dataset_with_markdown.csv \
  --sample-index 10
```

---

## Example Python Usage

```python
import pandas as pd

df = pd.read_csv(
    "balanced_table_dataset_with_markdown.csv",
    low_memory=False
)

print(df.shape)
print(df["label"].value_counts())

sample = df.iloc[0]

print("Sample ID:", sample["sample_id"])
print("Label:", sample["label"])
print("ASC Rule:", sample["target_asc_rule_ids"])
print("Statement Type:", sample["target_statement_types"])
print(sample["table_input"])
```

---

## Minimal LLM Prompt

The included `example_usage.py` also creates a simple rule-verification prompt:

```text
You are a financial accounting compliance analyst.

Review the financial statement below and determine whether it
violates the specified ASC rule.

ASC Rule:
<target ASC rule>

Financial Statement:
<Markdown financial statement>

Return only:
VIOLATION
or
NO_VIOLATION
```

The script only creates and prints the prompt. It does **not** require an API key and does not call any external LLM by default.

This makes the repository model-agnostic: the prompt can be passed to OpenAI, DeepSeek, Qwen, Llama, or another model.

---

## Markdown Dataset

To load `balanced_table_input.md` directly:

```python
from pathlib import Path

markdown = Path(
    "balanced_table_input.md"
).read_text(encoding="utf-8")

print(markdown[:3000])
```

---

## Important Notes

- `NO_VIOLATION` means **no known violation for the paired task under the current construction and screening procedure**. It should not be interpreted as a universal audit opinion that the filing contains no accounting issue of any kind.
- Comment-letter-specific fields may be empty for controls because matched controls do not necessarily originate from a corresponding SEC comment-letter case.
- The financial statement tables are extracted from SEC filings and converted to Markdown while preserving their primary tabular structure.
- The current release contains 529 controls. Additional matched controls may be added in future versions.

---

## Data Lineage

```text
Audit Analytics SEC comment-letter dataset
                    ↓
        Accounting-related cases
                    ↓
        ASC rule identification
                    ↓
      SEC referenced filing retrieval
                    ↓
Four primary financial statement extraction
                    ↓
  Confirmed directly visible ASC violations
                    ↓
             563 positives
                    ↓
      SIC/year/form matched peer search
                    ↓
       Known-violation filing exclusion
                    ↓
             529 controls
                    ↓
      1,092-sample balanced dataset
                    ↓
        Markdown table generation
```

---

## Citation

A formal citation will be added when the associated paper is released.

If you use this dataset before then, please cite the repository URL and the version or commit used in your experiment.

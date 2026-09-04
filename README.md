# Financial Statement Auditing Benchmark

## Overview

This repository provides complementary real-world and synthetic datasets for evaluating large language models on financial-statement auditing and accounting-compliance tasks.

The repository contains:

1. **Real-World Auditing Data**, derived from SEC comment-letter cases and the corresponding financial statements; and
2. **Synthetic Auditing Dataset**, created by introducing controlled accounting, classification, presentation, and reconciliation errors into financial statements.

Together, the two components support evaluation under both naturally occurring regulatory cases and controlled rule-based violations.

> Synthetic violations are created solely for research and should not be interpreted as actual reporting errors made by the companies represented in the dataset.

## Repository Structure

```text
.
├── README.md
├── final_primary_financial_statement_rules.xlsx
├── Real-World-Auditing-Data/
│   ├── README.md
│   ├── example_usage.py
│   └── balanced_table_dataset_simplified.csv
└── synthetic-auditing-dataset/
    ├── README.md
    ├── example_usage.py
    └── final_financial_statement_cases_102_companies.json
```

## Dataset Components

| Component | Source | Size | Primary purpose |
|---|---|---:|---|
| `Real-World-Auditing-Data/` | SEC comment letters and referenced SEC filings | 1,092 samples | Binary table-level ASC violation detection |
| `synthetic-auditing-dataset/` | Controlled transformations of public financial statements | 5,100 original–synthetic pairs | Rule-based violation analysis, localization, and explanation |
| `final_primary_financial_statement_rules.xlsx` | Curated primary-statement rule set | 50 rules | Rule definitions and synthetic-data construction guidance |

Each dataset folder contains its own README and minimal usage script. Refer to those files for the detailed schema, task construction, and limitations of each component.

## Real-World Auditing Data

The real-world benchmark contains 1,092 financial-statement samples:

- 563 confirmed table-level `VIOLATION` samples; and
- 529 matched `NO_VIOLATION` controls.

Its public CSV uses a compact four-column schema:

| Column | Description |
|---|---|
| `sample_id` | Unique sample identifier |
| `input` | Target ASC rule and Markdown financial statement presented to the model |
| `label` | `VIOLATION` or `NO_VIOLATION` |
| `pair_id` | Identifier linking a violation case with its matched control |

The principal task is:

```text
ASC rule + financial statement table -> VIOLATION / NO_VIOLATION
```

Run the example:

```bash
cd Real-World-Auditing-Data
python example_usage.py
```

For additional details, see [`Real-World-Auditing-Data/README.md`](Real-World-Auditing-Data/README.md).

## Synthetic Auditing Dataset

The synthetic dataset contains 5,100 records covering:

- 102 companies;
- 50 synthetic rules;
- 11 economic sectors; and
- 50 original–synthetic statement pairs per company.

Each record includes an original statement, a modified statement containing an intentional violation, transformation evidence, and ground-truth annotations.

The recommended paired task is:

```text
original statement + synthetic statement
    -> violated rule + affected lines + explanation
```

For binary detection, each pair may be expanded into:

```text
original statement  -> NO_VIOLATION
synthetic statement -> VIOLATION
```

This produces 10,200 derived statement examples. The original and synthetic versions from the same record must remain in the same data split.

Run the example:

```bash
cd synthetic-auditing-dataset
python example_usage.py
```

For additional details, see [`synthetic-auditing-dataset/README.md`](synthetic-auditing-dataset/README.md).

## Supporting Rule File

### `final_primary_financial_statement_rules.xlsx`

This workbook documents 50 curated rules intended to be identifiable from primary financial statements. It contains:

- `Final Rules`: rule identifiers, categories, summaries, ASC references, and synthetic use cases;
- `Review Summary`: review-level statistics and assessment notes; and
- `Changes and Exclusions`: documentation of removed, merged, or renumbered candidate rules.

The current workbook and synthetic JSON use related but not identical rule-ID inventories. In particular, the workbook includes `CF-13` and `SE-07`, while the synthetic dataset includes `XS-001` and `XS-002`. Users performing rule-level joins should align the rule-set version explicitly instead of assuming a direct one-to-one match.

The workbook's `Final Rules` sheet contains 50 rows, although a retained summary cell reports 48; users should treat the rule table itself as the current inventory and verify version alignment for downstream experiments.

## Supported Research Tasks

The repository supports several evaluation settings:

- binary violation detection;
- ASC rule verification;
- rule identification;
- affected-line-item localization;
- violation explanation generation;
- cross-statement consistency checking;
- robustness evaluation across companies, industries, and statement formats; and
- comparison between real-world and controlled synthetic violations.

## Recommended Evaluation Protocol

- Keep matched real-world samples together by splitting on `pair_id`.
- Keep each synthetic original–modified pair in the same split.
- Use company-level splits to test generalization to unseen issuers.
- Use rule-level splits to test generalization to unseen violation types.
- Do not expose ground-truth explanations, line-change annotations, case names, or quality-control metadata as model input when those fields are evaluation targets.
- Report category-level and statement-level results in addition to overall performance.
- Evaluate real-world and synthetic results separately before reporting any combined aggregate.

## Data Sources and Disclaimer

The repository uses financial-statement information and SEC correspondence derived from publicly available SEC EDGAR filings, together with Audit Analytics source data where applicable.

`NO_VIOLATION` in the real-world benchmark means that no violation associated with the paired target rule was identified under the dataset's construction and screening procedure. It is not a general audit opinion on the filing.

Synthetic records contain intentionally introduced errors. They are designed for controlled research and are not evidence of misconduct, deficient reporting, or audit failure by any represented company.

## Limitations

- Synthetic errors may not reflect the full ambiguity and complexity of real regulatory cases.
- Matched real-world controls may contain unrelated accounting issues outside the target rule.
- Financial-statement layouts and terminology vary across issuers and industries.
- Some synthetic metadata, including a small number of fiscal-year values, requires validation before year-based analysis.
- Rule identifiers should be versioned carefully when joining the rule workbook to the synthetic dataset.
- Automated checks support data quality but do not replace professional accounting judgment.

## Citation

A formal citation will be added when the associated paper is released. Until then, please cite the repository URL and the version or commit used in your experiment.

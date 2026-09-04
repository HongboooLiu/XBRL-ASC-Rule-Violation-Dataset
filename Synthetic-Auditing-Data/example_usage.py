#!/usr/bin/env python3
"""Minimal usage example for the synthetic financial-statement dataset."""

import argparse
import json
from collections import Counter
from pathlib import Path


DEFAULT_JSON = "final_financial_statement_cases_102_companies.json"
REQUIRED_FIELDS = {
    "record_id",
    "ticker",
    "rule_id",
    "statement_type",
    "case_name",
    "label",
    "original_statement",
    "synthetic_statement",
    "ground_truth",
}


def build_prompt(record: dict) -> str:
    """Build a paired prompt without exposing ground-truth annotations."""
    original = json.dumps(
        record["original_statement"], ensure_ascii=False, indent=2
    )
    synthetic = json.dumps(
        record["synthetic_statement"], ensure_ascii=False, indent=2
    )

    return f"""You are a financial accounting analyst.

Compare the original and synthetic financial statements below. Identify the
accounting, classification, presentation, or reconciliation violation introduced
in the synthetic statement. Name the affected line item(s) and briefly explain
the expected financial-statement effect.

Original Financial Statement:
{original}

Synthetic Financial Statement:
{synthetic}
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect the synthetic financial-statement dataset."
    )
    parser.add_argument(
        "--json",
        default=DEFAULT_JSON,
        help=f"Path to the dataset JSON. Default: {DEFAULT_JSON}",
    )
    parser.add_argument(
        "--sample-index",
        type=int,
        default=0,
        help="Zero-based record index to inspect. Default: 0",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Print the full paired prompt, which may be long.",
    )
    args = parser.parse_args()

    dataset_path = Path(args.json)
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}\n"
            f"Place {DEFAULT_JSON} in this folder or use --json."
        )

    with dataset_path.open(encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list) or not records:
        raise ValueError("The dataset must be a non-empty JSON list.")

    missing = REQUIRED_FIELDS.difference(records[0])
    if missing:
        raise ValueError(f"First record is missing fields: {sorted(missing)}")

    if not 0 <= args.sample_index < len(records):
        raise IndexError(
            f"--sample-index must be between 0 and {len(records) - 1}"
        )

    print("Synthetic Financial Statement Violation Dataset")
    print(f"Records: {len(records):,}")
    print(f"Companies: {len({record['ticker'] for record in records}):,}")
    print(f"Rules: {len({record['rule_id'] for record in records}):,}")
    print(f"Labels: {dict(Counter(record['label'] for record in records))}")

    sample = records[args.sample_index]
    print("\nExample Record")
    for field in (
        "record_id",
        "company",
        "ticker",
        "fiscal_year",
        "rule_id",
        "statement_type",
        "case_name",
        "label",
    ):
        print(f"{field}: {sample.get(field)}")

    original_rows = sample["original_statement"].get("rows", [])
    synthetic_rows = sample["synthetic_statement"].get("rows", [])
    print(f"original rows: {len(original_rows):,}")
    print(f"synthetic rows: {len(synthetic_rows):,}")
    print(f"documented line changes: {len(sample.get('line_changes', [])):,}")

    print("\nGround Truth")
    for field, value in sample["ground_truth"].items():
        print(f"{field}: {value}")

    if args.show_prompt:
        print("\nPaired Model Prompt")
        print(build_prompt(sample))
    else:
        print("\nUse --show-prompt to print the full paired model prompt.")


if __name__ == "__main__":
    main()

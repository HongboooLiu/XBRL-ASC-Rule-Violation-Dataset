#!/usr/bin/env python3
"""Minimal usage example for the simplified synthetic dataset."""

import argparse
import json
import zipfile
from pathlib import Path


DEFAULT_DATASET = "synthetic_financial_statement_cases_simplified.jsonl.zip"
REQUIRED_FIELDS = {"id", "input", "label", "metadata"}


def iter_jsonl(path: Path):
    """Yield records from a .jsonl file or a .jsonl.zip archive."""
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = [
                name
                for name in archive.namelist()
                if name.lower().endswith(".jsonl")
                and not name.startswith("__MACOSX/")
            ]
            if len(members) != 1:
                raise ValueError(f"Expected one JSONL file in {path}, found {members}")
            with archive.open(members[0]) as file:
                for line in file:
                    if line.strip():
                        yield json.loads(line)
        return

    with path.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


def get_record(path: Path, sample_index: int) -> dict:
    if sample_index < 0:
        raise IndexError("--sample-index must be non-negative")
    for index, record in enumerate(iter_jsonl(path)):
        if index == sample_index:
            return record
    raise IndexError(f"--sample-index {sample_index} is outside the dataset")


def build_prompt(record: dict) -> str:
    model_input = json.dumps(record["input"], ensure_ascii=False, indent=2)
    return f"""You are a financial accounting analyst.

Compare the original and synthetic financial statements. Identify the rule that
is violated, the violation itself, the affected line item(s), and the expected
financial-statement effect.

Input:
{model_input}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path(DEFAULT_DATASET))
    parser.add_argument("--sample-index", type=int, default=0)
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()

    if not args.dataset.exists():
        raise FileNotFoundError(
            f"Dataset not found: {args.dataset}\n"
            f"Place {DEFAULT_DATASET} in this folder or use --dataset."
        )

    record = get_record(args.dataset, args.sample_index)
    missing = REQUIRED_FIELDS.difference(record)
    if missing:
        raise ValueError(f"Record is missing fields: {sorted(missing)}")

    print("Synthetic Financial Statement Violation Dataset")
    print(f"Sample index: {args.sample_index}")
    print(f"ID: {record['id']}")
    print(f"Ticker: {record['metadata'].get('ticker')}")
    print(f"Statement type: {record['metadata'].get('statement_type')}")
    print(f"Rule: {record['label'].get('rule_id')}")
    print(f"Violation: {record['label'].get('violation')}")
    print(
        "Affected line items:",
        record["label"].get("affected_line_items", []),
    )

    original_rows = record["input"]["original_statement"].get("rows", [])
    synthetic_rows = record["input"]["synthetic_statement"].get("rows", [])
    print(f"Original rows: {len(original_rows):,}")
    print(f"Synthetic rows: {len(synthetic_rows):,}")

    if args.show_prompt:
        print("\nModel Prompt")
        print(build_prompt(record))
    else:
        print("\nUse --show-prompt to print the full model input.")


if __name__ == "__main__":
    main()

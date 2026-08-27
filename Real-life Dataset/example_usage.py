#!/usr/bin/env python3

"""
Minimal usage example for the ASC Table Compliance Benchmark.

Usage:
    python example_usage.py
    python example_usage.py --sample-index 10
    python example_usage.py --csv /path/to/dataset.csv --sample-index 10
"""

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_CSV = "balanced_table_dataset_with_markdown.csv"


def build_prompt(sample):
    """Create a minimal rule-verification prompt."""

    return f"""
You are a financial accounting compliance analyst.

Review the financial statement below and determine whether it
violates the specified ASC rule.

ASC Rule:
{sample['target_asc_rule_ids']}

Financial Statement:
{sample['table_input']}

Return only:
VIOLATION
or
NO_VIOLATION
""".strip()


def main():
    parser = argparse.ArgumentParser(
        description="Simple example for loading the ASC Table Compliance Benchmark."
    )

    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV,
        help=f"Path to the dataset CSV. Default: {DEFAULT_CSV}",
    )

    parser.add_argument(
        "--sample-index",
        type=int,
        default=0,
        help="0-based row index to inspect. Default: 0",
    )

    args = parser.parse_args()

    csv_path = Path(args.csv)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {csv_path}\n"
            "Place balanced_table_dataset_with_markdown.csv in this folder "
            "or provide its location with --csv."
        )

    df = pd.read_csv(
        csv_path,
        low_memory=False,
    )

    print("=" * 70)
    print("ASC Table Compliance Benchmark")
    print("=" * 70)

    print(f"\nDataset: {csv_path}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    if "label" in df.columns:
        print("\nLabel distribution:")
        print(df["label"].value_counts(dropna=False))

    if not 0 <= args.sample_index < len(df):
        raise IndexError(
            f"--sample-index must be between 0 and {len(df) - 1}"
        )

    sample = df.iloc[args.sample_index]

    print("\n" + "=" * 70)
    print("Example Sample")
    print("=" * 70)

    for column in [
        "sample_id",
        "pair_id",
        "label",
        "Name",
        "Ticker",
        "Filing Type",
        "target_asc_rule_ids",
        "target_statement_types",
    ]:
        if column in sample.index:
            print(f"{column}: {sample[column]}")

    print("\nFinancial Statement Markdown:")
    print("-" * 70)

    table_input = sample.get("table_input", "")

    if pd.isna(table_input) or not str(table_input).strip():
        print("[table_input is empty]")
    else:
        print(table_input)

    print("\n" + "=" * 70)
    print("Minimal LLM Prompt")
    print("=" * 70)
    print(build_prompt(sample))

    print("\n" + "=" * 70)
    print("Ground Truth")
    print("=" * 70)
    print(sample.get("label", "Label column not found"))


if __name__ == "__main__":
    main()

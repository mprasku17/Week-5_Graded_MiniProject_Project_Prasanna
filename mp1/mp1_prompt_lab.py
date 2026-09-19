from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.eval.golden import load_golden_set, load_snippets, validate_dataset
from src.eval.judge import judge_all
from src.eval.scoring import add_deterministic_scores, aggregate_by_strategy
from src.pipeline.pipeline import run_extraction_batch
from src.pipeline.settings import ROOT_DIR, Settings


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a list of result dictionaries to a JSONL file."""
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write a CSV file using the first row's keys as the column order."""
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def format_comparison_table(summary: list[dict[str, Any]]) -> str:
    """Format strategy metrics as a pandas markdown table for terminal output."""
    if not summary:
        return "No strategy comparison available."

    display = []
    for row in summary:
        display.append(
            {
                "Strategy": row["strategy"],
                "Accuracy (mean of 3)": f"{row['Accuracy (mean of 3)']:.3f}",
                "Parse rate": f"{row['Parse rate']:.3f}",
                "Judge score": f"{row['Judge score']:.3f}",
                "Total cost ($)": f"${row['Total cost ($)']:.6f}",
                "Latency p50 (s)": f"{row['Latency p50 (s)']:.3f}",
            }
        )

    df = pd.DataFrame(display)
    return df.to_markdown(index=False)


# Run the full benchmark pipeline for extraction, judging, and aggregate reporting.
async def run_project(settings: Settings) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    snippets = load_snippets(settings.snippets_path)
    golden_lookup = load_golden_set(settings.golden_path)

    # Run the extraction batch for all snippets and strategies, then score and judge the results.
    extraction_results = await run_extraction_batch(snippets, settings)

    # Score and judge the results, then aggregate by strategy for the final summary.
    scored_results = add_deterministic_scores(extraction_results, golden_lookup)

    # Judge the scored results using the configured judge model and return the final summary.
    judged_results = await judge_all(scored_results, snippets, golden_lookup, settings)

    # Aggregate the judged results by strategy for the final summary table.
    summary = aggregate_by_strategy(judged_results)
    return judged_results, summary


def main() -> int:
    """Entry point for validating data and executing the MP1 comparison workflow."""
    parser = argparse.ArgumentParser(description="Run MP1 prompt strategy comparison.")
    parser.add_argument("--skip-api", action="store_true", help="Validate inputs and write execution-required docs without API calls.")
    #args = parser.parse_args()

    settings = Settings()
    validation = validate_dataset(settings.snippets_path, settings.golden_path)
    settings.results_dir.mkdir(exist_ok=True)

    print(f"Settings.openai_api_key: {settings.openai_api_key}")


    results, summary = asyncio.run(run_project(settings))
    results_path = settings.results_dir / "mp1_results.jsonl"
    summary_path = settings.results_dir / "mp1_summary.csv"
    write_jsonl(results_path, results)
    write_csv(summary_path, summary)

    print(format_comparison_table(summary))
    print(f"\nWrote {results_path}, {summary_path}, mp1_comparison.md, and mp1_writeup.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

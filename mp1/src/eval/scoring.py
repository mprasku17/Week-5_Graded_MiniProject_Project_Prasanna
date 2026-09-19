from __future__ import annotations

import re
from typing import Any

import pandas as pd

from src.pipeline.models import EXTRACTION_KEYS


def normalize_text(value: Any) -> str | None:
    """Normalize text values by trimming whitespace and lowercasing for comparison."""
    if value is None:
        return None
    return re.sub(r"\s+", " ", str(value).strip()).casefold()


def normalize_years(value: Any) -> int | None | str:
    """Convert varied year-based values into a consistent comparable form."""
    if value is None:
        return None
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    text = str(value).strip().casefold()
    if text in {"null", "none", "not stated", "not specified", "n/a", "na"}:
        return None
    match = re.search(r"\d+", text)
    if match:
        return int(match.group(0))
    return text


def field_matches(field: str, actual: Any, expected: Any) -> bool:
    """Check whether one extracted field matches the gold value under the normalization rules."""
    if field == "years_experience_required":
        return normalize_years(actual) == normalize_years(expected)
    return normalize_text(actual) == normalize_text(expected)


def deterministic_accuracy(parsed: dict[str, Any] | None, expected: dict[str, Any]) -> int:
    """Count how many extracted fields exactly match the expected answer after normalization."""
    if parsed is None:
        return 0
    return sum(1 for key in EXTRACTION_KEYS if field_matches(key, parsed.get(key), expected.get(key)))


def add_deterministic_scores(
    results: list[dict[str, Any]],
    golden_lookup: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Attach deterministic accuracy and parse-success flags for each extraction result."""
    scored = []
    for result in results:
        expected = golden_lookup[result["snippet_id"]]
        scored.append(
            {
                **result,
                "accuracy": deterministic_accuracy(result.get("parsed_extraction"), expected),
                "parse_success": result.get("parsed_extraction") is not None,
            }
        )
    return scored


def aggregate_by_strategy(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate per-strategy metrics such as accuracy, parse rate, cost, and latency."""
    df = pd.DataFrame(results)

    summary = df.groupby("strategy").agg({
        "accuracy": "mean",
        "parse_success": "mean",
        "llm_judge_score": "mean",
        "cost_usd": "sum",
        "latency_s": "median",
    }).round({
        "accuracy": 3,
        "parse_success": 3,
        "llm_judge_score": 3,
        "cost_usd": 6,
        "latency_s": 3,
    })

    summary.columns = [
        "Accuracy (mean of 3)",
        "Parse rate",
        "Judge score",
        "Total cost ($)",
        "Latency p50 (s)",
    ]
    return summary.reset_index().to_dict(orient="records")

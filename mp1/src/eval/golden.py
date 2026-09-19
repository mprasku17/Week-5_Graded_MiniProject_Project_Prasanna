from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.pipeline.models import EXTRACTION_KEYS, JobSnippet


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSONL file and return one Python dictionary per non-empty line."""
    p = Path(path)
    rows = []
    with p.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{p}:{line_number} invalid JSONL: {exc}") from exc
    return rows


def load_snippets(path: str | Path) -> list[JobSnippet]:
    """Convert the snippet JSONL into typed JobSnippet objects for the pipeline."""
    rows = load_jsonl(path)
    return [JobSnippet(id=row["id"], snippet=row["snippet"]) for row in rows]


def load_golden_set(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load the golden answer set keyed by snippet id for deterministic comparison."""
    rows = load_jsonl(path)
    return {row["id"]: row for row in rows}


def validate_dataset(snippets_path: str | Path, golden_path: str | Path) -> dict[str, Any]:
    """Check that the snippet and golden datasets are aligned and have the expected shape."""
    snippets = load_jsonl(snippets_path)
    golden_rows = load_jsonl(golden_path)
    if len(snippets) != 10:
        raise ValueError(f"Expected 10 snippets, found {len(snippets)}")
    if len(golden_rows) != 10:
        raise ValueError(f"Expected 10 golden rows, found {len(golden_rows)}")
    snippet_ids = {row.get("id") for row in snippets}
    golden_ids = {row.get("id") for row in golden_rows}
    if snippet_ids != golden_ids:
        raise ValueError(f"Snippet IDs and golden IDs differ: {snippet_ids ^ golden_ids}")
    for row in snippets:
        if "id" not in row or "snippet" not in row:
            raise ValueError(f"Snippet row missing id/snippet: {row}")
    for row in golden_rows:
        missing = {"id", *EXTRACTION_KEYS} - set(row)
        if missing:
            raise ValueError(f"Golden row missing {missing}: {row}")
    return {"n_snippets": len(snippets), "n_golden": len(golden_rows), "ids": sorted(snippet_ids)}


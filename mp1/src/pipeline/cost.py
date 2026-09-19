from __future__ import annotations

from typing import Any


RATES = {
    "gpt-4o-mini": {"in": 0.15 / 1_000_000, "out": 0.60 / 1_000_000},
    "gpt-4o":      {"in": 2.50 / 1_000_000, "out": 10.00 / 1_000_000},
}


def compute_cost_usd(model: str, usage: dict[str, Any] | None) -> float:
    """Compute the USD cost for a model call using the token usage and pricing table."""
    if not usage:
        return 0.0
    pricing = RATES.get(model, {"in": 0.0, "out": 0.0})
    input_tokens = int(usage.get("prompt_tokens", 0) or 0)
    completion_tokens = int(usage.get("completion_tokens", 0) or 0)
    
    return (
        input_tokens * pricing["in"]
        + completion_tokens * pricing["out"]
    )


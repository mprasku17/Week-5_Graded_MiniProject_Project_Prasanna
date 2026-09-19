from __future__ import annotations

import json
import re
from typing import Any

from .models import EXTRACTION_KEYS


def parse_json_response(raw_response: str) -> dict[str, Any] | None:
    """Extract the JSON object from a model response and keep only the required job fields."""
    cleaned = raw_response.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    candidates = [cleaned]
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidates.append(cleaned[first : last + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return {key: parsed.get(key) for key in EXTRACTION_KEYS}
    return None


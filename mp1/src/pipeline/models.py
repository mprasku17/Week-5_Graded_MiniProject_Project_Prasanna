from __future__ import annotations

#from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any


EXTRACTION_KEYS = ("company", "role", "years_experience_required")


class JobSnippet(BaseModel):
    id: str
    snippet: str


class ExtractionResult(BaseModel):
    strategy: str
    snippet_id: str
    raw_response: str
    parsed_extraction: dict[str, Any] | None
    cost_usd: float
    latency_seconds: float
    usage: dict[str, Any]
    parse_success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "snippet_id": self.snippet_id,
            "raw_response": self.raw_response,
            "parsed_extraction": self.parsed_extraction,
            "cost_usd": self.cost_usd,
            "latency_s": self.latency_seconds,
            "latency_seconds": self.latency_seconds,
            "usage": self.usage,
            "parse_success": self.parse_success,
            "error": self.error,
        }

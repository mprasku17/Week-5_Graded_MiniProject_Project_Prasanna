from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from numpy import integer
from openai import AsyncOpenAI

from src.pipeline.cost import compute_cost_usd
from src.pipeline.models import EXTRACTION_KEYS
from src.pipeline.settings import Settings


def parse_judge_response(raw: str) -> dict[str, Any]:
    """Extract the JSON payload from the judge model response and return the parsed object."""
    cleaned = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first != -1 and last != -1 and last > first:
        cleaned = cleaned[first : last + 1]
    return json.loads(cleaned)


def build_judge_messages(
    snippet: str,
    gold: dict[str, Any],
    parsed: dict[str, Any] | None,
    raw_response: str,
) -> list[dict[str, str]]:
    """Construct the evaluation prompt that compares a parsed extraction to the gold answer."""
    return [
        {
            "role": "system",
            "content": (
                "You are a strict evaluator for structured extraction quality. "
                "Return only a JSON object with integer score from 1 to 4 and a brief reason."
            ),
        },
        {
            "role": "user",
            "content": (
                "Score how well the model extracted company, role, and years_experience_required.\n"
                "Rubric:\n"
                "4 - all three fields correct\n"
                "3 - two of three correct and no fabricated data\n"
                "2 - one of three correct, or fabricated a field\n"
                "1 - none correct or unparsable\n\n"
                f"Snippet:\n{snippet}\n\n"
                f"Gold JSON:\n{json.dumps({key: gold.get(key) for key in EXTRACTION_KEYS}, ensure_ascii=False)}\n\n"
                f"Parsed extraction:\n{json.dumps(parsed, ensure_ascii=False)}\n\n"
                f"Raw model response:\n{raw_response}"
            ),
        },
    ]


    
async def judge_one(
    client: AsyncOpenAI,
    settings: Settings,
    result: dict[str, Any],
    snippet_lookup: dict[str, str],
    golden_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Judge one extraction result against the golden answer and return the score metadata."""
    messages = build_judge_messages(
        snippet_lookup[result["snippet_id"]],
        golden_lookup[result["snippet_id"]],
        result.get("parsed_extraction"),
        result.get("raw_response", ""),
    )
    try:
        response = await client.chat.completions.create(
            model=settings.judge_model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=120,
        )
        raw = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if hasattr(response.usage, "model_dump") else dict(response.usage or {})
        latency = 0.0
        parsed = parse_judge_response(raw)
        score = max(1, min(4, int(parsed.get("score"))))
        reason = str(parsed.get("reason", "")).strip()
        error = None
    except Exception as exc:
        raw = ""
        usage = {}
        latency = 0.0
        score = None
        reason = ""
        error = str(exc)
    return {
        **result,
        "llm_judge_score": score,
        "judge_reason": reason,
        "judge_raw_response": raw,
        "judge_usage": usage,
        "judge_cost_usd": compute_cost_usd(settings.judge_model, usage),
        "judge_latency_seconds": latency,
        "judge_error": error,
    }


async def judge_all(
    results: list[dict[str, Any]],
    snippets: list[Any],
    golden_lookup: dict[str, dict[str, Any]],
    settings: Settings,
) -> list[dict[str, Any]]:
    """Judge every extraction result in parallel and return the enriched evaluation rows."""
    snippet_lookup = {snippet.id: snippet.snippet for snippet in snippets}
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.request_timeout_seconds)
    try:
        tasks = [judge_one(client, settings, result, snippet_lookup, golden_lookup) for result in results]
        return await asyncio.gather(*tasks)
    finally:
        await client.close()

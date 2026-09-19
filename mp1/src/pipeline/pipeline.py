from __future__ import annotations

import asyncio
import time
from typing import Any

from openai import AsyncOpenAI

from src.pipeline.cost import compute_cost_usd
from src.pipeline.models import ExtractionResult, JobSnippet
from src.pipeline.parsing import parse_json_response
from src.pipeline.settings import Settings
from src.pipeline.strategies import STRATEGIES


async def run_one(
    client: AsyncOpenAI,
    settings: Settings,
    strategy: str,
    snippet: JobSnippet,
) -> ExtractionResult:
    """Send one extraction request for one strategy and return a normalized result payload."""
    messages = STRATEGIES[strategy](snippet.snippet)
    started = time.perf_counter()
    try:
        response = await client.chat.completions.create(
            model=settings.extraction_model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=220,
        )
        raw_response = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if hasattr(response.usage, "model_dump") else dict(response.usage or {})
        latency = time.perf_counter() - started
        parsed = parse_json_response(raw_response)
        return ExtractionResult(
            strategy=strategy,
            snippet_id=snippet.id,
            raw_response=raw_response,
            parsed_extraction=parsed,
            cost_usd=compute_cost_usd(settings.extraction_model, usage),
            latency_seconds=latency,
            usage=usage,
            parse_success=parsed is not None,
        )
    except Exception as exc:
        return ExtractionResult(
            strategy=strategy,
            snippet_id=snippet.id,
            raw_response="",
            parsed_extraction=None,
            cost_usd=0.0,
            latency_seconds=time.perf_counter() - started,
            usage={},
            parse_success=False,
            error=str(exc),
        )


async def run_all(snippets: list[JobSnippet], settings: Settings) -> list[dict[str, Any]]:
    """Run every snippet against every strategy and return the flattened extraction results."""
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url, timeout=settings.request_timeout_seconds)
    try:
        tasks = [
            run_one(client, settings, strategy, snippet)
            for snippet in snippets
            for strategy in STRATEGIES
        ]
        results = await asyncio.gather(*tasks)
    finally:
        await client.close()
    return [result.to_dict() for result in results]


async def run_strategy_call(
    client: AsyncOpenAI,
    settings: Settings,
    strategy: str,
    snippet: JobSnippet,
) -> ExtractionResult:
    """Helper wrapper to run a single strategy call for one snippet."""
    return await run_one(client, settings, strategy, snippet)


async def run_extraction_batch(snippets: list[JobSnippet], settings: Settings) -> list[dict[str, Any]]:
    """Entry function for the extraction phase, returning one result per snippet/strategy pair."""
    return await run_all(snippets, settings)

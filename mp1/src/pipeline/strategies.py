from __future__ import annotations

from collections.abc import Callable

from prompts import chain_of_thought, few_shot, structured_role_based, zero_shot


StrategyBuilder = Callable[[str], list[dict[str, str]]]


def evaluate_zero_shot(snippet: str) -> list[dict[str, str]]:
    """Return the zero-shot prompt messages for one snippet."""
    return zero_shot(snippet)


def evaluate_few_shot(snippet: str) -> list[dict[str, str]]:
    """Return the few-shot prompt messages for one snippet."""
    return few_shot(snippet)


def evaluate_structured_role_based(snippet: str) -> list[dict[str, str]]:
    """Return the structured role-based prompt messages for one snippet."""
    return structured_role_based(snippet)


def evaluate_chain_of_thought(snippet: str) -> list[dict[str, str]]:
    """Return the chain-of-thought prompt messages for one snippet."""
    return chain_of_thought(snippet)


STRATEGIES: dict[str, StrategyBuilder] = {
    "zero_shot": evaluate_zero_shot,
    "few_shot": evaluate_few_shot,
    "structured_role_based": evaluate_structured_role_based,
    "chain_of_thought": evaluate_chain_of_thought,
}


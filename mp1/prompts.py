from __future__ import annotations

from typing import Callable


EXTRACTION_KEYS = ("company", "role", "years_experience_required")


def zero_shot(snippet: str) -> list[dict[str, str]]:
    """Build a minimal, direct extraction prompt for the company, role, and seniority fields."""
    return [
        {
            "role": "user",
            "content": (
                "Extract the hiring company, job title, and minimum years of "
                "experience required from this job snippet. Return only JSON "
                'with keys "company", "role", and "years_experience_required". '
                "Use null for years_experience_required if no specific years "
                f"requirement is stated.\n\nSnippet:\n{snippet}"
            ),
        }
    ]


def few_shot(snippet: str) -> list[dict[str, str]]:
    """Build a prompt that includes a few examples to teach the extraction format and edge cases."""
    return [
        {
            "role": "user",
            "content": (
                "Extract company, role, and minimum years_experience_required "
                "from each job snippet. Return only JSON.\n\n"
                "Example 1\n"
                "Snippet: Acme Corp seeks a Backend Engineer with 5+ years of Python experience.\n"
                'Answer: {"company":"Acme Corp","role":"Backend Engineer","years_experience_required":5}\n\n'
                "Example 2\n"
                "Snippet: Hooli is hiring an intern. No experience required; new grads welcome.\n"
                'Answer: {"company":"Hooli","role":"intern","years_experience_required":0}\n\n'
                "Example 3\n"
                "Snippet: Cyberdyne needs an AI Researcher with strong publications. No years listed.\n"
                'Answer: {"company":"Cyberdyne","role":"AI Researcher","years_experience_required":null}\n\n'
                f"Now extract from this snippet:\n{snippet}"
            ),
        }
    ]


def structured_role_based(snippet: str) -> list[dict[str, str]]:
    """Build a structured recruiter-style prompt that enforces the exact JSON schema and parsing rules."""
    return [
        {
            "role": "system",
            "content": (
                "You are an expert recruiter and data extraction specialist. "
                "You convert short job postings into strict JSON for evaluation."
            ),
        },
        {
            "role": "user",
            "content": (
                "Extract exactly this JSON schema and no extra text:\n"
                "{\n"
                '  "company": string,\n'
                '  "role": string,\n'
                '  "years_experience_required": integer or null\n'
                "}\n\n"
                "Rules:\n"
                "- Use the company doing the hiring.\n"
                "- Use the advertised job title as written, preserving seniority.\n"
                "- For ranges, use the minimum number.\n"
                "- For phrases like fresh grads welcome or no prior experience, use 0.\n"
                "- If no years requirement is stated, use null.\n\n"
                f"Snippet:\n{snippet}"
            ),
        },
    ]


def chain_of_thought(snippet: str) -> list[dict[str, str]]:
    """Build a reasoning-oriented prompt that asks the model to work through the extraction before returning JSON."""
    return [
        {
            "role": "user",
            "content": (
                "Think step by step about the company, job title, and minimum "
                "years of experience in the snippet. After reasoning internally, "
                "return only the final JSON object with keys company, role, and "
                "years_experience_required. Use 0 if no years are stated and"
                "if the snippet says no experience is required, and the minimum "
                "number for a range.\n\n"
                f"Snippet:\n{snippet}"
            ),
        }
    ]


PROMPT_BUILDERS: dict[str, Callable[[str], list[dict[str, str]]]] = {
    "zero_shot": zero_shot,
    "few_shot": few_shot,
    "structured_role_based": structured_role_based,
    "chain_of_thought": chain_of_thought,
}

from __future__ import annotations

import os
#from dataclasses import dataclass, field
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Set the ROOT_DIR to mp1
ROOT_DIR = Path(__file__).resolve().parents[2]


# def load_env_file(path: Path | None = None) -> None:
#     path = path or ROOT_DIR / ".env"
#     if not path.exists():
#         return
#     for line in path.read_text(encoding="utf-8").splitlines():
#         stripped = line.strip()
#         if not stripped or stripped.startswith("#") or "=" not in stripped:
#             continue
#         key, value = stripped.split("=", 1)
#         os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# Load .env before resolving settings values.
load_dotenv(ROOT_DIR/".env")

#load_env_file(ROOT_DIR / ".env")


# @dataclass(frozen=True)
# class Settings :
#     data_dir: Path = field(default_factory=lambda: ROOT_DIR / "data")
#     results_dir: Path = field(default_factory=lambda: ROOT_DIR / "results")
#     snippets_path: Path = field(default_factory=lambda: ROOT_DIR / "data" / "job_snippets.jsonl")
#     golden_path: Path = field(default_factory=lambda: ROOT_DIR / "data" / "golden_set.jsonl")
#     extraction_model: str = field(default_factory=lambda: os.getenv("MP1_EXTRACTION_MODEL", "gpt-4o-mini"))
#     judge_model: str = field(default_factory=lambda: os.getenv("MP1_JUDGE_MODEL", "gpt-4o"))
#     temperature: float = 0.0
#     max_concurrency: int = field(default_factory=lambda: int(os.getenv("MP1_MAX_CONCURRENCY", "8")))
#     request_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("MP1_REQUEST_TIMEOUT_SECONDS", "60")))

#     openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
#     fastapi_url: str = field(default_factory=lambda: os.getenv("MP1_FASTAPI_URL", "http://localhost:8000"))
#     openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

class Settings(BaseModel):
    """Project configuration loaded from the local environment and project folder layout."""
    data_dir: Path = Path(ROOT_DIR/"data")
    results_dir: Path = Path(ROOT_DIR/"results")
    snippets_path: Path = Path(ROOT_DIR/"data"/"job_snippets.jsonl")
    golden_path: Path = Path(ROOT_DIR/"data"/"golden_set.jsonl")

    openai_base_url: str = os.environ.get("OPENAI_BASE_URL", "")
    fastapi_url: str = os.environ.get("MP1_FASTAPI_URL", "http://localhost:8000")

    extraction_model: str = os.environ.get("MP1_EXTRACTION_MODEL", "gpt-4o-mini")
    judge_model: str = os.environ.get("MP1_JUDGE_MODEL", "gpt-4o")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    temperature: float = Field(0.0, ge=0.0, le=1.0)
    max_concurrency: int = int(os.environ.get("MP1_MAX_CONCURRENCY", "8"))
    request_timeout_seconds: float = float(os.environ.get("MP1_REQUEST_TIMEOUT_SECONDS", "60"))
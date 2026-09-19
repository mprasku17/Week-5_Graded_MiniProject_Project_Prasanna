# MP1 Prompt Strategy Comparison

This project compares four prompt strategies for extracting structured information from job snippets:

- `zero_shot`
- `few_shot`
- `structured_role_based`
- `chain_of_thought`

The workflow loads the dataset, calls the OpenAI API for each snippet/strategy pair, validates the JSON output, computes deterministic scores against the golden set, optionally runs an LLM-as-judge, and writes the final comparison report.

## Current project structure

```text
mp1/
  .env
  README.md
  requirements.txt
  mp1_prompt_lab.py
  prompts.py
  mp1_comparison.md
  mp1_writeup.md
  data/
    golden_set.jsonl
    job_snippets.jsonl
  results/
    mp1_results.jsonl
    mp1_summary.csv
  src/
    eval/
      __init__.py
      golden.py
      judge.py
      scoring.py
    pipeline/
      __init__.py
      cost.py
      models.py
      parsing.py
      pipeline.py
      settings.py
      strategies.py
```

The current implementation active runtime is centered on `prompts.py`, `src/pipeline/*`, and `src/eval/*`.

## What the code does

- `prompts.py` defines the four actual prompt builders and their JSON output contract.
- `src/pipeline/strategies.py` registers the strategy names used by the benchmark.
- `src/pipeline/pipeline.py` runs the extraction batch with `AsyncOpenAI` and returns normalized result objects.
- `src/eval/golden.py` validates the snippet and golden datasets.
- `src/eval/scoring.py` computes deterministic accuracy and aggregate metrics.
- `src/eval/judge.py` scores the extraction results using the configured judge model.
- `mp1_prompt_lab.py` is the main runner that writes the final comparison markdown and writeup.

## Setup

```bash
cd mp1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` file is maintained with API key and other settings as given below:

```bash
OPENAI_API_KEY=<my openai_api_key>
OPENAI_BASE_URL=<my openai base url>
MP1_EXTRACTION_MODEL=gpt-4o-mini
MP1_JUDGE_MODEL=gpt-4o
MP1_MAX_CONCURRENCY=8
MP1_REQUEST_TIMEOUT_SECONDS=60
```

The project also reads `ROOT_DIR/.env` automatically via `src/pipeline/settings.py`.

## Run the benchmark

Execute the full comparison workflow:

```bash
python3 mp1_prompt_lab.py
```

This validates the JSONL inputs, runs all snippet/strategy combinations, writes `results/mp1_results.jsonl` and `results/mp1_summary.csv`


## Output format

The generated results include per-extraction fields such as:

- `strategy`
- `snippet_id`
- `raw_response`
- `parsed_extraction`
- `cost_usd`
- `latency_seconds`
- `parse_success`
- `accuracy`
- `llm_judge_score`

The summary table is aggregated by strategy and written to `results/mp1_summary.csv`.

## Notes

- The benchmark uses `gpt-4o-mini` for extraction and `gpt-4o` for judging by default.
- Temperature is fixed at `0.0` in the pipeline settings.
- Cost is computed from token usage and stored per extraction result.
- If `OPENAI_API_KEY` is missing, the script does not fabricate scores; it exits cleanly after validation and writes placeholder documentation instead.

## Typical workflow

1. Populate `.env` with the OpenAI credentials.
2. Run `python3 mp1_prompt_lab.py`.
3. Inspect the detailed raw results in `results/mp1_results.jsonl`.
4. Use the aggregate summary in `results/mp1_summary.csv` for the final comparison.

## GitHub Link
This Mini Project code is published here : https://github.com/mprasku17/Week-5_Graded_MiniProject_Project_Prasanna.git 
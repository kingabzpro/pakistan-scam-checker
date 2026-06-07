"""Evaluate Qwen3.5 4B Q8 with the deployed Qwen3.6 LLM judge."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.modal_minicpm_v46_q8 import test_request as shared  # noqa: E402

shared.MINICPM_ENDPOINT = (
    "https://abidali899--pakistan-scam-checker-qwen35-4b-q8-serve.modal.run"
)
shared.MINICPM_MODEL = "qwen3.5-4b-q8"
shared.RESULT_PATH = Path(__file__).parent / "latest_results.json"

if __name__ == "__main__":
    raise SystemExit(shared.main())

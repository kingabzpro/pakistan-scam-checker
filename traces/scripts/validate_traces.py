"""Validate privacy-safe trace JSONL files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from traces.runtime import validate_trace


def validate_file(path: Path) -> tuple[int, list[str]]:
    count = 0
    errors: list[str] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        count += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
            continue
        for error in validate_trace(record):
            errors.append(f"{path}:{line_number}: {error}")
    return count, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths or [TRACE_DIR / "data" / "trace_samples.jsonl"]
    total = 0
    all_errors: list[str] = []
    for path in paths:
        if not path.exists():
            all_errors.append(f"{path}: file does not exist")
            continue
        count, errors = validate_file(path)
        total += count
        all_errors.extend(errors)
    if all_errors:
        print("\n".join(all_errors), file=sys.stderr)
        return 1
    print(f"Validated {total} trace records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

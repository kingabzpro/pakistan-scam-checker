"""Export validated pending trace shards into one JSONL file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from traces.runtime import PENDING_DIR, validate_trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "traces" / "export" / "trace_export.jsonl",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    records = []
    for path in sorted(PENDING_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            record = json.loads(line)
            errors = validate_trace(record)
            if errors:
                raise RuntimeError(f"{path}: {'; '.join(errors)}")
            records.append(record)
    content = "".join(
        json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
        for record in records
    )
    if args.dry_run:
        print(content, end="")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"Exported {len(records)} traces to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

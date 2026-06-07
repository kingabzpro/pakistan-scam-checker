"""Validate and upload pending privacy-safe trace shards."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_traces import validate_file
from trace_runtime import DATASET_REPO, PENDING_DIR


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-id",
        default=os.getenv("HF_TRACE_DATASET_REPO", DATASET_REPO),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    paths = sorted(PENDING_DIR.glob("*.jsonl"))
    if not paths:
        print("No pending trace shards.")
        return 0
    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    date_path = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    for path in paths:
        count, errors = validate_file(path)
        if errors:
            raise RuntimeError("\n".join(errors))
        remote = f"data/{date_path}/{path.name}"
        if args.dry_run:
            print(f"Would upload {count} records: {path} -> {remote}")
            continue
        api.upload_file(
            path_or_fileobj=str(path),
            path_in_repo=remote,
            repo_id=args.repo_id,
            repo_type="dataset",
            commit_message=f"Add privacy-safe trace shard {path.name}",
        )
        if not args.keep:
            path.unlink()
        print(f"Uploaded {count} records to {remote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

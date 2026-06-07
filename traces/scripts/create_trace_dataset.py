"""Create and initialize the public Hugging Face trace dataset."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from huggingface_hub import HfApi
from huggingface_hub.errors import EntryNotFoundError

ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "build-small-hackathon/pakistan-notice-helper-traces"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-id",
        default=os.getenv("HF_TRACE_DATASET_REPO", DEFAULT_REPO),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--replace-data",
        action="store_true",
        help="Delete existing data files before uploading the current seed.",
    )
    args = parser.parse_args()
    files = {
        TRACE_DIR / "dataset_card.md": "README.md",
        TRACE_DIR / "data" / "trace_samples.jsonl": "data/seed/trace_samples.jsonl",
    }
    if args.dry_run:
        print(f"Would create public dataset: {args.repo_id}")
        if args.replace_data:
            print("Would delete the existing data/ folder.")
        for local, remote in files.items():
            print(f"Would upload {local} -> {remote}")
        return 0
    api = HfApi(token=os.getenv("HF_TOKEN") or None)
    api.create_repo(
        repo_id=args.repo_id,
        repo_type="dataset",
        private=False,
        exist_ok=True,
    )
    if args.replace_data:
        try:
            api.delete_folder(
                path_in_repo="data",
                repo_id=args.repo_id,
                repo_type="dataset",
                commit_message="Replace trace data for simplified schema",
            )
        except EntryNotFoundError:
            pass
    for local, remote in files.items():
        api.upload_file(
            path_or_fileobj=str(local),
            path_in_repo=remote,
            repo_id=args.repo_id,
            repo_type="dataset",
            commit_message=f"Add {remote}",
        )
    print(f"Initialized https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

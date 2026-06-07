"""Generate deterministic seed traces for the six built-in examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trace_runtime import PIPELINE_STEPS, build_trace_record, validate_trace

TEXT_EXAMPLES = {
    "text-courier": (
        "PAKISTAN POST: Your parcel address is incomplete. Pay Rs. 85 today "
        "at http://pakpost-delivery.xyz or the parcel will be destroyed."
    ),
    "text-fbr": (
        "FBR REFUND: You are eligible for Rs 42,500. Submit your CNIC and bank "
        "card details at the link today to receive payment."
    ),
    "text-bank": (
        "HBL Security: Your account will be suspended. Share the OTP sent to "
        "your phone with our support team immediately."
    ),
}
IMAGE_EXAMPLES = {
    "image-courier": ROOT / "static" / "example-courier.jpeg",
    "image-mobile": ROOT / "static" / "example-mobile.png",
    "image-traffic": ROOT / "static" / "example-trafic.png",
}


def build_seed_records() -> list[dict]:
    assessments = json.loads(
        (ROOT / "data" / "example_assessments.json").read_text(encoding="utf-8")
    )["examples"]
    pipeline_status = {
        step: (
            "completed"
            if step
            in {
                "receive",
                "validate",
                "reply_filter",
                "response",
            }
            else "hit"
            if step == "cache_lookup"
            else "skipped"
        )
        for step in PIPELINE_STEPS
    }
    records = []
    for example_id, assessment in assessments.items():
        text = TEXT_EXAMPLES.get(example_id, "")
        image_path = IMAGE_EXAMPLES.get(example_id)
        image_placeholder = ""
        if image_path:
            image_placeholder = "x" * int(image_path.stat().st_size * 4 / 3)
        record = build_trace_record(
            text=text,
            image_data_url=image_placeholder,
            example_id=example_id,
            request_source="cached_modal_example",
            pipeline_status=pipeline_status,
            pipeline_ms={},
            modal_called=False,
            modal_ms=0,
            retry_count=0,
            assessment=assessment,
        )
        errors = validate_trace(record)
        if errors:
            raise RuntimeError(f"{example_id}: {'; '.join(errors)}")
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data" / "trace_samples.jsonl",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    records = build_seed_records()
    content = "".join(
        json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
        for record in records
    )
    if args.dry_run:
        print(content, end="")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"Wrote {len(records)} traces to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

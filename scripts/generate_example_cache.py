"""Generate bundled example assessments with the configured model endpoint."""

from __future__ import annotations

import base64
import json
import mimetypes
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402

TEXT_EXAMPLES = {
    "text-courier": (
        "PAKISTAN POST: Your parcel address is incomplete. Pay Rs. 85 today at "
        "http://pakpost-delivery.xyz or the parcel will be destroyed."
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


def image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def quality_issue(example_id: str, assessment: dict[str, object]) -> str:
    explanation = str(assessment["simple_explanation"]).lower()
    next_steps = " ".join(
        str(item) for item in assessment["safe_next_steps"]  # type: ignore[union-attr]
    ).lower()
    if "social media" in next_steps:
        return "safe next steps recommend social media"
    if any(phrase in explanation for phrase in ("in the future", "in the past")):
        return "explanation makes an unsupported date comparison"
    if example_id == "image-traffic" and any(
        name in next_steps for name in ("fbr", "nadra")
    ):
        return "traffic fine advice names an unrelated authority"
    return ""


def generate_assessment(
    example_id: str,
    *,
    text: str = "",
    image: str = "",
) -> dict[str, object]:
    last_issue = ""
    for attempt in range(1, 4):
        assessment = app.call_model(text, image)
        last_issue = quality_issue(example_id, assessment)
        if not last_issue:
            print(f"{example_id}: accepted on attempt {attempt}")
            return assessment
        print(f"{example_id}: retrying after attempt {attempt}: {last_issue}")
    raise RuntimeError(f"{example_id} failed cache quality checks: {last_issue}")


def main() -> None:
    base_url, model_name, _ = app.env_config()
    examples = {
        example_id: generate_assessment(example_id, text=text)
        for example_id, text in TEXT_EXAMPLES.items()
    }
    examples.update(
        {
            example_id: generate_assessment(
                example_id,
                image=image_data_url(path),
            )
            for example_id, path in IMAGE_EXAMPLES.items()
        }
    )

    document = {
        "model_repo": "unsloth/Qwen3.5-4B-MTP-GGUF",
        "model_name": model_name,
        "endpoint": base_url,
        "endpoint_type": "Modal-hosted llama.cpp OpenAI-compatible endpoint",
        "generated_at": date.today().isoformat(),
        "examples": examples,
    }
    app.EXAMPLE_CACHE_PATH.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(examples)} assessments in {app.EXAMPLE_CACHE_PATH}")


if __name__ == "__main__":
    main()

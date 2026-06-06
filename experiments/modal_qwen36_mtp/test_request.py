"""Smoke-test the Qwen3.6 MTP OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from openai.types.chat import ChatCompletion

REQUIRED_FIELDS = {
    "risk_label",
    "simple_explanation",
    "red_flags",
    "safe_next_steps",
    "reply_draft",
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_label": {
            "type": "string",
            "enum": ["low", "medium", "high"],
        },
        "simple_explanation": {"type": "string"},
        "red_flags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "safe_next_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
        "reply_draft": {"type": "string"},
    },
    "required": sorted(REQUIRED_FIELDS),
    "additionalProperties": False,
}

SCAM_PROMPT = """You help people in Pakistan assess suspicious notices and messages.

Analyze this message:

"PAKISTAN POST: Your parcel was returned after a failed delivery attempt. Pay
Rs. 85 now at http://pakpost-delivery.example/verify to rearrange delivery.
Your parcel will be destroyed today if payment is not completed."

Return a concise assessment for a general audience. The reply draft must not
encourage engagement with a scammer; when appropriate, it may simply say not
to reply."""

IMAGE_DIR = Path(__file__).parent / "images"


class ResponseValidationError(ValueError):
    """Raised when the endpoint response does not match the experiment contract."""


def require_environment() -> tuple[str, str, str]:
    names = ("MODAL_PROXY_KEY", "MODAL_PROXY_SECRET")
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Create a token at https://modal.com/settings/proxy-auth-tokens "
            "and follow the README setup."
        )
    endpoint = "https://abidali899--pakistan-scam-checker-qwen36-mtp-serve.modal.run".rstrip("/")
    return endpoint, os.environ["MODAL_PROXY_KEY"], os.environ["MODAL_PROXY_SECRET"]


def extract_and_validate(response_body: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(response_body, dict):
        raise ResponseValidationError("response body must be a JSON object")
    try:
        choice = response_body["choices"][0]
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ResponseValidationError(
            "response is missing choices[0].message.content"
        ) from exc
    if not isinstance(content, str):
        raise ResponseValidationError("message content must be a string")

    try:
        assessment = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ResponseValidationError(
            f"message content is not valid JSON: {exc}"
        ) from exc
    if not isinstance(assessment, dict):
        raise ResponseValidationError("assessment must be a JSON object")

    validate_assessment(assessment)
    return assessment, choice


def send_request(
    endpoint: str,
    proxy_key: str,
    proxy_secret: str,
    retries: int,
    retry_delay: float,
    image_path: Path | None = None,
) -> tuple[dict[str, Any], float]:
    client = OpenAI(
        api_key="not-used-by-llama-server",
        base_url=f"{endpoint}/v1",
        default_headers={
            "Modal-Key": proxy_key,
            "Modal-Secret": proxy_secret,
        },
        timeout=1800.0,
        max_retries=0,
    )
    if image_path is None:
        user_content: Any = SCAM_PROMPT
    else:
        if not image_path.exists():
            raise RuntimeError(f"Image does not exist: {image_path}")
        image_url = (
            "data:image/png;base64,"
            + base64.b64encode(image_path.read_bytes()).decode("ascii")
        )
        user_content = [
            {
                "type": "text",
                "text": (
                    "Assess this screenshot for scam risk. Explain the visible "
                    "evidence and give safe next steps."
                ),
            },
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    started_at = time.monotonic()
    for attempt in range(1, retries + 1):
        try:
            completion: ChatCompletion = client.chat.completions.create(
                model="qwen3.6-27b-mtp",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Respond only with JSON matching the supplied schema. "
                            "Use clear English suitable for Pakistan. Do not invent "
                            "URLs or contact details. The reply_draft must be polite, "
                            "safe, and must not repeat insults or abusive language "
                            "visible in the input."
                        ),
                    },
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
                max_tokens=750 if image_path else 500,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "scam_assessment",
                        "strict": True,
                        "schema": OUTPUT_SCHEMA,
                    },
                },
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                },
            )
            return completion.model_dump(), time.monotonic() - started_at
        except APIStatusError as exc:
            if exc.status_code == 503 and attempt < retries:
                print(
                    f"Attempt {attempt} received 503 during cold start; retrying...",
                    file=sys.stderr,
                )
                time.sleep(retry_delay)
                continue
            body_preview = str(exc.body)[:1000]
            raise RuntimeError(
                f"endpoint returned HTTP {exc.status_code}: {body_preview}"
            ) from exc
        except (APIConnectionError, APITimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"request failed after {retries} attempts: {exc}") from exc
            print(f"Attempt {attempt} failed: {exc}; retrying...", file=sys.stderr)
            time.sleep(retry_delay)

    raise RuntimeError("request retry loop ended unexpectedly")


def run_self_test() -> None:
    valid_assessment = {
        "risk_label": "high",
        "simple_explanation": "This is a phishing message.",
        "red_flags": ["Urgent payment request"],
        "safe_next_steps": ["Do not open the link"],
        "reply_draft": "Do not reply.",
    }
    valid_response = {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": json.dumps(valid_assessment)},
            }
        ]
    }
    extract_and_validate(valid_response)

    invalid_cases = [
        {},
        {"choices": [{"message": {"content": "not json"}}]},
        {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {key: value for key, value in valid_assessment.items()
                             if key != "reply_draft"}
                        )
                    }
                }
            ]
        },
    ]
    for case in invalid_cases:
        try:
            extract_and_validate(case)
        except ResponseValidationError:
            continue
        raise AssertionError(f"invalid response unexpectedly passed: {case!r}")
    print("Self-test passed: malformed and incomplete responses are rejected.")


def validate_assessment(assessment: dict[str, Any]) -> None:
    """Validate an already-parsed assessment object."""
    missing = REQUIRED_FIELDS - assessment.keys()
    if missing:
        raise ResponseValidationError(
            "assessment is missing fields: " + ", ".join(sorted(missing))
        )
    extra = assessment.keys() - REQUIRED_FIELDS
    if extra:
        raise ResponseValidationError(
            "assessment has unexpected fields: " + ", ".join(sorted(extra))
        )
    if assessment["risk_label"] not in {"low", "medium", "high"}:
        raise ResponseValidationError("risk_label must be low, medium, or high")
    for field in ("simple_explanation", "reply_draft"):
        if not isinstance(assessment[field], str) or not assessment[field].strip():
            raise ResponseValidationError(f"{field} must be a non-empty string")
    for field in ("red_flags", "safe_next_steps"):
        value = assessment[field]
        if (
            not isinstance(value, list)
            or not value
            or not all(isinstance(item, str) and item.strip() for item in value)
        ):
            raise ResponseValidationError(
                f"{field} must be a non-empty array of non-empty strings"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--images",
        action="store_true",
        help="Test both bundled scam screenshots through the Modal function.",
    )
    parser.add_argument("--retries", type=int, default=20)
    parser.add_argument("--retry-delay", type=float, default=15.0)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        endpoint, proxy_key, proxy_secret = require_environment()
        image_paths = (
            [IMAGE_DIR / "scam_1.png", IMAGE_DIR / "scam_2.png"]
            if args.images
            else [None]
        )
        for image_path in image_paths:
            response_body, elapsed_seconds = send_request(
                endpoint,
                proxy_key,
                proxy_secret,
                retries=args.retries,
                retry_delay=args.retry_delay,
                image_path=image_path,
            )
            assessment, choice = extract_and_validate(response_body)
            print(f"Input: {image_path.name if image_path else 'text prompt'}")
            print(f"Endpoint: {endpoint}")
            print(f"Total request time: {elapsed_seconds:.2f} seconds")
            print(f"Finish reason: {choice.get('finish_reason', 'unknown')}")
            print(
                "Token usage:",
                json.dumps(response_body.get("usage", {}), sort_keys=True),
            )
            print("Validated assessment:")
            print(json.dumps(assessment, indent=2, ensure_ascii=False))
    except (RuntimeError, ResponseValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fast, deterministic, privacy-safe pipeline tracing."""

from __future__ import annotations

import json
import os
import queue
import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TRACE_ROOT = Path(os.getenv("TRACE_DIR", ROOT / "traces"))
PENDING_DIR = TRACE_ROOT / "pending"
DATASET_REPO = os.getenv(
    "HF_TRACE_DATASET_REPO",
    "build-small-hackathon/pakistan-notice-helper-traces",
)
SCHEMA_VERSION = "1.0"
BATCH_SIZE = max(1, int(os.getenv("TRACE_BATCH_SIZE", "20")))
FLUSH_SECONDS = max(1.0, float(os.getenv("TRACE_FLUSH_SECONDS", "60")))
MAX_QUEUE_SIZE = max(1, int(os.getenv("TRACE_MAX_QUEUE_SIZE", "5000")))

PIPELINE_STEPS = (
    "receive",
    "validate",
    "cache_lookup",
    "modal_request",
    "parse_json",
    "normalize_result",
    "reply_filter",
    "response",
)
RISK_LABELS = {
    "Looks normal",
    "Verify first",
    "Suspicious",
    "Likely scam",
    "Inappropriate",
    "none",
}
FAILURE_CATEGORIES = {
    "none",
    "validation_empty",
    "credentials_missing",
    "http_auth",
    "http_error",
    "connection_error",
    "timeout",
    "invalid_model_output",
    "internal_error",
}
PIPELINE_STATUSES = {"completed", "skipped", "rejected", "failed", "hit", "miss"}
REQUEST_SOURCES = {"user", "cached_modal_example"}
SIGNAL_PATTERNS = {
    "otp": r"\b(?:otp|one[- ]time (?:pin|password)|verification code)\b",
    "cnic": r"\bcnic\b",
    "credentials": r"\b(?:pin|password|cvv|card details?|bank details?)\b",
    "link": r"(?:https?://|www\.|bit\.ly|tinyurl\.|cutt\.ly|\.xyz\b|\.top\b)",
    "urgency": r"\b(?:urgent|immediately|today|now|within \d+|last warning)\b",
    "payment": r"\b(?:pay|payment|fee|fine|transfer|send money|rs\.?|pkr)\b",
    "refund_or_prize": r"\b(?:refund|prize|winner|lottery|cashback|reward)\b",
    "courier": r"\b(?:parcel|courier|delivery|pakistan post|leopards|tcs|customs)\b",
    "challan": r"\b(?:challan|traffic fine|traffic violation|e-challan)\b",
    "account_threat": (
        r"\b(?:account|sim|service|electricity)\b.{0,50}"
        r"\b(?:block|blocked|suspend|closed|disconnect)\b"
    ),
}
EXAMPLE_PROFILES = {
    "text-courier": ("text", "courier", {"link", "urgency", "payment", "courier"}),
    "text-fbr": ("text", "fbr", {"cnic", "credentials", "urgency", "refund_or_prize"}),
    "text-bank": ("text", "bank", {"otp", "urgency", "account_threat"}),
    "image-courier": ("image", "courier", {"link", "urgency", "courier"}),
    "image-mobile": ("image", "marketplace", {"credentials"}),
    "image-traffic": ("image", "traffic_challan", {"link", "urgency", "payment", "challan"}),
}


def _bucket_number(value: float, thresholds: tuple[tuple[float, str], ...]) -> str:
    for maximum, label in thresholds:
        if value <= maximum:
            return label
    return thresholds[-1][1]


def duration_bucket(milliseconds: float) -> str:
    return _bucket_number(
        max(0.0, milliseconds),
        (
            (1, "0-1ms"),
            (5, "2-5ms"),
            (10, "6-10ms"),
            (50, "11-50ms"),
            (250, "51-250ms"),
            (1000, "251-1000ms"),
            (5000, "1-5s"),
            (30000, "5-30s"),
            (float("inf"), "30s+"),
        ),
    )


def input_size_bucket(length: int) -> str:
    return _bucket_number(
        max(0, length),
        (
            (0, "empty"),
            (160, "1-160"),
            (500, "161-500"),
            (2000, "501-2000"),
            (6000, "2001-6000"),
            (12000, "6001-12000"),
            (float("inf"), "12000+"),
        ),
    )


def image_size_bucket(data_url_length: int) -> str:
    estimated_bytes = max(0, int(data_url_length * 0.75))
    return _bucket_number(
        estimated_bytes,
        (
            (0, "none"),
            (100_000, "up-to-100KB"),
            (500_000, "100-500KB"),
            (2_000_000, "500KB-2MB"),
            (8_000_000, "2-8MB"),
            (float("inf"), "8MB+"),
        ),
    )


def detect_signals(text: str, example_id: str = "") -> dict[str, bool]:
    detected = {
        name: bool(re.search(pattern, text or "", re.I | re.S))
        for name, pattern in SIGNAL_PATTERNS.items()
    }
    profile = EXAMPLE_PROFILES.get(example_id)
    if profile:
        for name in profile[2]:
            detected[name] = True
    return detected


def detect_category(text: str, signals: dict[str, bool], example_id: str = "") -> str:
    profile = EXAMPLE_PROFILES.get(example_id)
    if profile:
        return profile[1]
    lowered = (text or "").lower()
    categories = (
        ("fbr", ("fbr", "taxpayer", "tax refund")),
        ("bank", ("bank", "hbl", "ubl", "meezan", "alfalah")),
        ("wallet", ("easypaisa", "jazzcash", "wallet")),
        ("utility", ("electricity", "gas bill", "utility", "lesco", "k-electric")),
        ("traffic_challan", ("challan", "traffic fine", "traffic violation")),
        ("courier", ("parcel", "courier", "delivery", "pakistan post", "leopards", "tcs")),
        ("customs", ("customs", "duty")),
        ("university", ("university", "admission", "scholarship", "hec")),
        ("job", ("job", "salary", "recruiter", "employment")),
        ("marketplace", ("buyer", "seller", "marketplace", "whatsapp")),
    )
    for category, terms in categories:
        if any(term in lowered for term in terms):
            return category
    if signals["challan"]:
        return "traffic_challan"
    if signals["courier"]:
        return "courier"
    return "unknown"


def detect_language_hint(text: str) -> str:
    has_urdu = bool(re.search(r"[\u0600-\u06ff]", text or ""))
    has_latin = bool(re.search(r"[A-Za-z]", text or ""))
    roman_terms = bool(
        re.search(
            r"\b(?:aap|apka|apki|hai|hain|karo|karein|paisa|rupay|bhej|jaldi)\b",
            text or "",
            re.I,
        )
    )
    if has_urdu and has_latin:
        return "mixed_urdu_latin"
    if has_urdu:
        return "urdu_script"
    if roman_terms:
        return "roman_urdu"
    if has_latin:
        return "latin_script"
    return "unknown"


def safe_summary(category: str, signals: dict[str, bool], input_type: str) -> str:
    category_labels = {
        "fbr": "FBR-style",
        "bank": "Bank-style",
        "wallet": "Wallet-style",
        "utility": "Utility-style",
        "traffic_challan": "Traffic-challan-style",
        "courier": "Courier-style",
        "customs": "Customs-style",
        "university": "Education-style",
        "job": "Job-style",
        "marketplace": "Marketplace-style",
        "unknown": "Unclassified",
    }
    signal_labels = {
        "otp": "OTP",
        "cnic": "CNIC",
        "credentials": "credential",
        "link": "link",
        "urgency": "urgency",
        "payment": "payment",
        "refund_or_prize": "refund-or-prize",
        "courier": "courier",
        "challan": "challan",
        "account_threat": "account-threat",
    }
    active = [signal_labels[name] for name, enabled in signals.items() if enabled][:4]
    suffix = f" with {', '.join(active)} signals" if active else " with no mapped signals"
    return f"{category_labels[category]} {input_type} input{suffix}"


def build_input_profile(text: str, image_data_url: str, example_id: str = "") -> dict[str, Any]:
    profile = EXAMPLE_PROFILES.get(example_id)
    if profile:
        input_type = profile[0]
    elif image_data_url and text:
        input_type = "text_and_image"
    elif image_data_url:
        input_type = "image"
    else:
        input_type = "text"
    signals = detect_signals(text, example_id)
    category = detect_category(text, signals, example_id)
    return {
        "type": input_type,
        "text_character_bucket": input_size_bucket(len(text or "")),
        "text_byte_bucket": input_size_bucket(len((text or "").encode("utf-8"))),
        "image_size_bucket": image_size_bucket(len(image_data_url or "")),
        "category": category,
        "language_hint": detect_language_hint(text),
        "signals": signals,
        "safe_summary": safe_summary(category, signals, input_type),
    }


def build_trace_record(
    *,
    text: str,
    image_data_url: str,
    example_id: str,
    request_source: str,
    pipeline_status: dict[str, str],
    pipeline_ms: dict[str, float],
    modal_called: bool,
    modal_ms: float,
    retry_count: int,
    assessment: dict[str, Any] | None,
    failure_category: str = "none",
    failure_stage: str = "none",
) -> dict[str, Any]:
    trace_id = str(uuid.uuid4())
    risk_label = str((assessment or {}).get("risk_label", "none"))
    if risk_label not in RISK_LABELS:
        risk_label = "none"
    commit = (
        os.getenv("SPACE_COMMIT")
        or os.getenv("GIT_COMMIT")
        or os.getenv("COMMIT_SHA")
        or ""
    )
    commit = commit[:64] if re.fullmatch(r"[0-9a-fA-F]{7,64}", commit) else "unknown"
    request_source = (
        request_source if request_source in REQUEST_SOURCES else "user"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app_commit": commit,
        "request_source": request_source,
        "input": build_input_profile(text, image_data_url, example_id),
        "pipeline_steps": [
            {
                "step": step,
                "status": (
                    pipeline_status.get(step, "skipped")
                    if pipeline_status.get(step, "skipped") in PIPELINE_STATUSES
                    else "skipped"
                ),
                "duration_bucket": duration_bucket(pipeline_ms.get(step, 0.0)),
            }
            for step in PIPELINE_STEPS
        ],
        "cache": {
            "hit": request_source == "cached_modal_example",
            "example_id": example_id if example_id in EXAMPLE_PROFILES else "none",
        },
        "modal": {
            "called": bool(modal_called),
            "model_family": (
                "qwen3.6-27b-mtp"
                if "qwen3.6-27b-mtp"
                in os.getenv("MODEL_NAME", "qwen3.6-27b-mtp").lower()
                else "other"
            ),
            "latency_bucket": duration_bucket(modal_ms),
            "retry_count": max(0, min(int(retry_count), 20)),
            "outcome": (
                "success"
                if modal_called and failure_category == "none"
                else "failed"
                if modal_called
                else "not_called"
            ),
        },
        "result": {
            "risk_label": risk_label,
            "red_flag_count": min(len((assessment or {}).get("red_flags", [])), 50),
            "safe_next_step_count": min(
                len((assessment or {}).get("safe_next_steps", [])),
                50,
            ),
            "reply_draft_returned": bool((assessment or {}).get("reply_draft")),
            "reply_draft_policy": (
                "allowed"
                if risk_label in {"Verify first", "Suspicious"}
                else "suppressed"
                if risk_label != "none"
                else "not_applicable"
            ),
        },
        "failure": {
            "category": (
                failure_category
                if failure_category in FAILURE_CATEGORIES
                else "internal_error"
            ),
            "stage": failure_stage if failure_stage in {*PIPELINE_STEPS, "none"} else "response",
        },
        "privacy": {
            "raw_input_stored": False,
            "raw_image_stored": False,
            "raw_model_output_stored": False,
            "exception_text_stored": False,
            "identifiers_stored": False,
        },
    }


def validate_trace(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["Trace must be an object."]
    required = {
        "schema_version",
        "trace_id",
        "timestamp",
        "app_commit",
        "request_source",
        "input",
        "pipeline_steps",
        "cache",
        "modal",
        "result",
        "failure",
        "privacy",
    }
    missing = required - record.keys()
    if missing:
        errors.append("Missing fields: " + ", ".join(sorted(missing)))
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append("Unsupported schema_version.")
    if record.get("result", {}).get("risk_label") not in RISK_LABELS:
        errors.append("Invalid risk label.")
    privacy = record.get("privacy", {})
    if not isinstance(privacy, dict) or any(privacy.get(key) is not False for key in privacy):
        errors.append("Privacy flags must all be false.")
    steps = record.get("pipeline_steps", [])
    if not isinstance(steps, list) or [item.get("step") for item in steps] != list(
        PIPELINE_STEPS
    ):
        errors.append("Pipeline steps are invalid or out of order.")
    forbidden_keys = {
        "raw_input",
        "raw_text",
        "image_data_url",
        "raw_model_output",
        "reply_draft",
        "simple_explanation",
        "error",
        "exception",
        "url",
        "phone",
        "account_number",
    }

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in forbidden_keys:
                    errors.append(f"Forbidden field: {key}")
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(record)
    return sorted(set(errors))


class TracePublisher:
    def __init__(self) -> None:
        self.queue: queue.Queue[dict[str, Any]] = queue.Queue(MAX_QUEUE_SIZE)
        self.lock = threading.Lock()
        self.thread: threading.Thread | None = None
        self.counters = {
            "queued": 0,
            "persisted": 0,
            "uploaded": 0,
            "upload_failures": 0,
            "dropped": 0,
        }

    def enqueue(self, record: dict[str, Any]) -> str:
        if validate_trace(record):
            with self.lock:
                self.counters["dropped"] += 1
            return "invalid"
        try:
            self.queue.put_nowait(record)
        except queue.Full:
            with self.lock:
                self.counters["dropped"] += 1
            return "dropped"
        with self.lock:
            self.counters["queued"] += 1
        self._ensure_worker()
        return "queued"

    def status(self) -> dict[str, Any]:
        with self.lock:
            counters = dict(self.counters)
        counters.update(
            {
                "queue_size": self.queue.qsize(),
                "pending_shards": len(list(PENDING_DIR.glob("*.jsonl")))
                if PENDING_DIR.exists()
                else 0,
                "dataset_repo": DATASET_REPO,
            }
        )
        return counters

    def _ensure_worker(self) -> None:
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            self.thread = threading.Thread(
                target=self._worker,
                name="privacy-safe-trace-publisher",
                daemon=True,
            )
            self.thread.start()

    def _worker(self) -> None:
        batch: list[dict[str, Any]] = []
        deadline: float | None = None
        self._upload_pending()
        while True:
            timeout = (
                max(0.05, deadline - time.monotonic())
                if deadline is not None
                else FLUSH_SECONDS
            )
            try:
                record = self.queue.get(timeout=timeout)
                batch.append(record)
                if deadline is None:
                    deadline = time.monotonic() + FLUSH_SECONDS
            except queue.Empty:
                pass
            if batch and (
                len(batch) >= BATCH_SIZE
                or (deadline is not None and time.monotonic() >= deadline)
            ):
                self._persist_batch(batch)
                batch = []
                deadline = None
                self._upload_pending()

    def _persist_batch(self, records: list[dict[str, Any]]) -> None:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        pending_count = self._pending_record_count()
        capacity = max(0, MAX_QUEUE_SIZE - pending_count)
        if capacity == 0:
            with self.lock:
                self.counters["dropped"] += len(records)
            return
        accepted = records[:capacity]
        dropped = len(records) - len(accepted)
        if dropped:
            with self.lock:
                self.counters["dropped"] += dropped
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        filename = f"trace-{timestamp}-{uuid.uuid4().hex[:8]}.jsonl"
        final_path = PENDING_DIR / filename
        temporary_path = final_path.with_suffix(".tmp")
        content = "".join(
            json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n"
            for record in accepted
        )
        temporary_path.write_text(content, encoding="utf-8")
        os.replace(temporary_path, final_path)
        with self.lock:
            self.counters["persisted"] += len(accepted)

    def _pending_record_count(self) -> int:
        if not PENDING_DIR.exists():
            return 0
        count = 0
        for path in PENDING_DIR.glob("*.jsonl"):
            try:
                count += sum(
                    1
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line
                )
            except OSError:
                continue
        return count

    def _upload_pending(self) -> None:
        token = os.getenv("HF_TOKEN", "").strip()
        if not token or not PENDING_DIR.exists():
            return
        try:
            from huggingface_hub import HfApi

            api = HfApi(token=token)
            for path in sorted(PENDING_DIR.glob("*.jsonl")):
                date_path = datetime.now(timezone.utc).strftime("%Y/%m/%d")
                uploaded = False
                for attempt in range(3):
                    try:
                        api.upload_file(
                            path_or_fileobj=str(path),
                            path_in_repo=f"data/{date_path}/{path.name}",
                            repo_id=DATASET_REPO,
                            repo_type="dataset",
                            commit_message=f"Add privacy-safe trace shard {path.name}",
                        )
                        uploaded = True
                        break
                    except Exception:
                        if attempt < 2:
                            time.sleep(2**attempt)
                if not uploaded:
                    with self.lock:
                        self.counters["upload_failures"] += 1
                    return
                count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line)
                path.unlink(missing_ok=True)
                with self.lock:
                    self.counters["uploaded"] += count
        except Exception:
            with self.lock:
                self.counters["upload_failures"] += 1


PUBLISHER = TracePublisher()


def start_trace_worker() -> None:
    PUBLISHER._ensure_worker()


def queue_trace(**kwargs: Any) -> tuple[str, str]:
    record = build_trace_record(**kwargs)
    return record["trace_id"], PUBLISHER.enqueue(record)


def trace_status() -> dict[str, Any]:
    return PUBLISHER.status()

"""Tests for deterministic privacy-safe tracing."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from openai import APIStatusError, APITimeoutError

import app
from traces import runtime as trace_runtime


class TraceTests(unittest.TestCase):
    def sample_record(self) -> dict:
        return trace_runtime.build_trace_record(
            text=(
                "Ali call +92 300 1234567 CNIC 35202-1234567-1 "
                "card 4111111111111111 https://private.example/a "
                "account PK00TEST address House 10 tracking ABC123"
            ),
            image_data_url="data:image/png;base64,PRIVATE_IMAGE_BYTES",
            example_id="",
            request_source="user",
            pipeline_status={step: "completed" for step in trace_runtime.PIPELINE_STEPS},
            pipeline_ms={},
            modal_called=True,
            modal_ms=120,
            retry_count=0,
            assessment={
                "risk_label": "Likely scam",
                "simple_explanation": "PRIVATE MODEL EXPLANATION",
                "red_flags": ["PRIVATE FLAG"],
                "safe_next_steps": ["PRIVATE STEP"],
                "reply_draft": "PRIVATE REPLY",
            },
        )

    def test_trace_has_no_private_canaries(self) -> None:
        serialized = json.dumps(self.sample_record())
        for canary in (
            "Ali",
            "+92 300 1234567",
            "35202-1234567-1",
            "4111111111111111",
            "private.example",
            "PK00TEST",
            "House 10",
            "ABC123",
            "PRIVATE_IMAGE_BYTES",
            "PRIVATE MODEL EXPLANATION",
            "PRIVATE FLAG",
            "PRIVATE STEP",
            "PRIVATE REPLY",
        ):
            self.assertNotIn(canary, serialized)

    def test_trace_validation_and_performance(self) -> None:
        started = time.perf_counter()
        records = [self.sample_record() for _ in range(200)]
        elapsed_ms = (time.perf_counter() - started) * 1000 / len(records)
        self.assertLess(elapsed_ms, 10)
        self.assertFalse(trace_runtime.validate_trace(records[0]))

    def test_opt_out_does_not_queue_trace(self) -> None:
        with patch("app.queue_trace") as queue_mock:
            result = app.analyze_notice("", "", save_trace=False)
        queue_mock.assert_not_called()
        self.assertEqual(result["trace"]["status"], "disabled")

    def test_cached_trace_does_not_call_model(self) -> None:
        with patch("app.call_model") as model_mock, patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ):
            result = app.analyze_notice(example_id="text-bank")
        model_mock.assert_not_called()
        self.assertEqual(result["source"], "cached_modal_example")

    def test_empty_input_traces_sanitized_validation_failure(self) -> None:
        with patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("")
        self.assertFalse(result["ok"])
        self.assertEqual(
            queue_mock.call_args.kwargs["failure_category"],
            "validation_empty",
        )

    def test_missing_credentials_traces_without_model_call(self) -> None:
        with patch(
            "app.model_status",
            return_value={"connected": False, "label": "missing"},
        ), patch("app.call_model") as model_mock, patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("test message")
        self.assertFalse(result["ok"])
        model_mock.assert_not_called()
        self.assertEqual(
            queue_mock.call_args.kwargs["failure_category"],
            "credentials_missing",
        )

    def test_success_uses_existing_model_call_once(self) -> None:
        assessment = {
            "risk_label": "Verify first",
            "simple_explanation": "Check independently.",
            "red_flags": ["Unverified sender"],
            "safe_next_steps": ["Use an official channel."],
            "reply_draft": "Please confirm through your official channel.",
        }

        def fake_call(_text, _image, telemetry):
            telemetry.update(
                {
                    "modal_called": True,
                    "modal_ms": 120,
                    "retry_count": 1,
                    "parse_ms": 1,
                    "normalize_ms": 1,
                }
            )
            return assessment

        with patch(
            "app.model_status",
            return_value={"connected": True, "label": "ready"},
        ), patch("app.call_model", side_effect=fake_call) as model_mock, patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("test message")
        self.assertTrue(result["ok"])
        model_mock.assert_called_once()
        self.assertTrue(queue_mock.call_args.kwargs["modal_called"])
        self.assertEqual(queue_mock.call_args.kwargs["retry_count"], 1)

    def test_timeout_is_sanitized(self) -> None:
        timeout = APITimeoutError(request=httpx.Request("POST", "https://example.invalid"))
        with patch(
            "app.model_status",
            return_value={"connected": True, "label": "ready"},
        ), patch("app.call_model", side_effect=timeout), patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("test message")
        self.assertFalse(result["ok"])
        self.assertEqual(queue_mock.call_args.kwargs["failure_category"], "timeout")

    def test_http_failure_is_sanitized(self) -> None:
        request = httpx.Request("POST", "https://example.invalid")
        error = APIStatusError(
            "service unavailable",
            response=httpx.Response(503, request=request),
            body={"private": "must not be traced"},
        )
        with patch(
            "app.model_status",
            return_value={"connected": True, "label": "ready"},
        ), patch("app.call_model", side_effect=error), patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("test message")
        self.assertFalse(result["ok"])
        self.assertEqual(queue_mock.call_args.kwargs["failure_category"], "http_error")
        self.assertNotIn("private", json.dumps(queue_mock.call_args.kwargs))

    def test_malformed_output_is_sanitized(self) -> None:
        with patch(
            "app.model_status",
            return_value={"connected": True, "label": "ready"},
        ), patch("app.call_model", side_effect=ValueError("PRIVATE RAW OUTPUT")), patch(
            "app.queue_trace",
            return_value=("trace-id", "queued"),
        ) as queue_mock:
            result = app.analyze_notice("test message")
        self.assertFalse(result["ok"])
        self.assertEqual(
            queue_mock.call_args.kwargs["failure_category"],
            "invalid_model_output",
        )
        self.assertNotIn("PRIVATE RAW OUTPUT", json.dumps(queue_mock.call_args.kwargs))

    def test_normalization_failure_uses_normalize_stage(self) -> None:
        telemetry: dict = {}
        with self.assertRaises(ValueError):
            app.parse_model_json('{"risk_label":"invalid"}', telemetry)
        self.assertTrue(telemetry["parse_completed"])
        self.assertNotIn("normalize_completed", telemetry)

    def test_model_retry_is_counted_without_extra_trace_call(self) -> None:
        request = httpx.Request("POST", "https://example.invalid")
        unavailable = APIStatusError(
            "unavailable",
            response=httpx.Response(503, request=request),
            body=None,
        )

        class Completions:
            def __init__(self):
                self.calls = 0

            def create(self, **_kwargs):
                self.calls += 1
                if self.calls == 1:
                    raise unavailable
                message = type("Message", (), {"content": json.dumps({
                    "risk_label": "Verify first",
                    "simple_explanation": "Verify independently.",
                    "red_flags": ["Unverified sender"],
                    "safe_next_steps": ["Use an official channel."],
                    "reply_draft": "Please confirm through an official channel.",
                })})()
                choice = type("Choice", (), {"message": message})()
                return type("Completion", (), {"choices": [choice]})()

        completions = Completions()
        client = type(
            "Client",
            (),
            {"chat": type("Chat", (), {"completions": completions})()},
        )()
        telemetry: dict = {}
        with patch("app.create_model_client", return_value=(client, "model")), patch.dict(
            "os.environ",
            {"MODEL_MAX_ATTEMPTS": "2", "MODEL_RETRY_DELAY_SECONDS": "0"},
        ):
            result = app.call_model("test", "", telemetry)
        self.assertEqual(result["risk_label"], "Verify first")
        self.assertEqual(completions.calls, 2)
        self.assertEqual(telemetry["retry_count"], 1)

    def test_publisher_persists_batch(self) -> None:
        publisher = trace_runtime.TracePublisher()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            trace_runtime,
            "PENDING_DIR",
            Path(directory),
        ):
            records = [self.sample_record() for _ in range(20)]
            publisher._persist_batch(records)
            paths = list(Path(directory).glob("*.jsonl"))
            self.assertEqual(len(paths), 1)
            self.assertEqual(len(paths[0].read_text().splitlines()), 20)

    def test_concurrent_enqueue_and_queue_limit(self) -> None:
        with patch.object(trace_runtime, "MAX_QUEUE_SIZE", 20):
            publisher = trace_runtime.TracePublisher()
        with patch.object(publisher, "_ensure_worker"):
            threads = [
                threading.Thread(target=publisher.enqueue, args=(self.sample_record(),))
                for _ in range(20)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(publisher.status()["queued"], 20)
            self.assertEqual(publisher.queue.qsize(), 20)
            self.assertEqual(publisher.enqueue(self.sample_record()), "dropped")
            self.assertEqual(publisher.status()["dropped"], 1)

    def test_hub_failure_keeps_pending_shard(self) -> None:
        publisher = trace_runtime.TracePublisher()
        with tempfile.TemporaryDirectory() as directory, patch.object(
            trace_runtime,
            "PENDING_DIR",
            Path(directory),
        ), patch.dict("os.environ", {"HF_TOKEN": "test-token"}), patch(
            "huggingface_hub.HfApi.upload_file",
            side_effect=RuntimeError("offline"),
        ), patch("traces.runtime.time.sleep"):
            publisher._persist_batch([self.sample_record()])
            publisher._upload_pending()
            self.assertEqual(len(list(Path(directory).glob("*.jsonl"))), 1)
            self.assertEqual(publisher.status()["upload_failures"], 1)


if __name__ == "__main__":
    unittest.main()

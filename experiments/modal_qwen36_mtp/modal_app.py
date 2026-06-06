"""Modal experiment for serving Qwen3.6 27B MTP with llama.cpp."""

from __future__ import annotations

import base64
import os
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import modal

APP_NAME = "pakistan-scam-checker-qwen36-mtp"
LLAMA_CPP_COMMIT = "5a69c974392020e514c3b2b2910bb92f847cb4c9"
MODEL_REPO = "unsloth/Qwen3.6-27B-MTP-GGUF"
MODEL_FILENAME = "Qwen3.6-27B-UD-Q4_K_XL.gguf"
MMPROJ_FILENAME = "mmproj-F16.gguf"
MODEL_DIR = Path("/models")
MODEL_PATH = MODEL_DIR / MODEL_FILENAME
MMPROJ_PATH = MODEL_DIR / MMPROJ_FILENAME
TEST_IMAGE_DIR = Path("/test-images")
LOCAL_IMAGE_DIR = Path(__file__).parent / "images"
MODEL_VOLUME_NAME = "pakistan-scam-checker-qwen36-models"
SERVER_PORT = 8080
MINUTES = 60

app = modal.App(APP_NAME)
model_volume = modal.Volume.from_name(MODEL_VOLUME_NAME, create_if_missing=True)

download_image = modal.Image.debian_slim(python_version="3.11").uv_pip_install(
    "huggingface-hub==0.36.0"
)

llama_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.1-devel-ubuntu22.04",
        add_python="3.11",
    )
    .apt_install(
        "ca-certificates",
        "cmake",
        "curl",
        "git",
        "libcurl4-openssl-dev",
        "ninja-build",
    )
    .run_commands(
        "git clone https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp",
        f"git -C /opt/llama.cpp checkout {LLAMA_CPP_COMMIT}",
        (
            "cmake -S /opt/llama.cpp -B /opt/llama.cpp/build -G Ninja "
            "-DCMAKE_BUILD_TYPE=Release "
            "-DBUILD_SHARED_LIBS=OFF "
            "-DGGML_CUDA=ON "
            "-DCMAKE_CUDA_ARCHITECTURES=89 "
            "-DLLAMA_CURL=ON"
        ),
        (
            "cmake --build /opt/llama.cpp/build "
            "--target llama-server --parallel"
        ),
    )
    .uv_pip_install("openai==2.33.0")
    .add_local_dir(LOCAL_IMAGE_DIR, TEST_IMAGE_DIR, copy=True)
)


@app.function(
    image=download_image,
    volumes={str(MODEL_DIR): model_volume},
    timeout=2 * MINUTES,
)
def model_status() -> dict[str, object]:
    """Return whether the expected GGUF is already present in the Volume."""
    if not MODEL_PATH.exists() or not MMPROJ_PATH.exists():
        result: dict[str, object] = {
            "downloaded": False,
            "path": str(MODEL_PATH),
            "mmproj_path": str(MMPROJ_PATH),
            "model_exists": MODEL_PATH.exists(),
            "mmproj_exists": MMPROJ_PATH.exists(),
        }
    else:
        result = {
            "downloaded": True,
            "path": str(MODEL_PATH),
            "size_bytes": MODEL_PATH.stat().st_size,
            "mmproj_path": str(MMPROJ_PATH),
            "mmproj_size_bytes": MMPROJ_PATH.stat().st_size,
        }
    print(result, flush=True)
    return result


@app.function(
    image=download_image,
    volumes={str(MODEL_DIR): model_volume},
    timeout=2 * MINUTES,
)
def download_model() -> dict[str, object]:
    """Download the selected public GGUF to the persistent Modal Volume."""
    from huggingface_hub import hf_hub_download

    started_at = time.monotonic()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    downloaded_model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILENAME,
        local_dir=str(MODEL_DIR),
    )
    downloaded_mmproj_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MMPROJ_FILENAME,
        local_dir=str(MODEL_DIR),
    )
    model_volume.commit()
    model_path = Path(downloaded_model_path)
    mmproj_path = Path(downloaded_mmproj_path)
    result = {
        "path": str(model_path),
        "size_bytes": model_path.stat().st_size,
        "mmproj_path": str(mmproj_path),
        "mmproj_size_bytes": mmproj_path.stat().st_size,
        "download_seconds": round(time.monotonic() - started_at, 2),
    }
    print(result, flush=True)
    return result


def wait_for_server(process: subprocess.Popen[bytes], timeout_seconds: int) -> None:
    """Wait until llama-server reports healthy or exits."""
    deadline = time.monotonic() + timeout_seconds
    health_url = f"http://127.0.0.1:{SERVER_PORT}/health"
    last_error = "server has not responded"

    while time.monotonic() < deadline:
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(
                f"llama-server exited with status {return_code} before becoming ready"
            )
        try:
            with urllib.request.urlopen(health_url, timeout=5) as response:
                if response.status == 200:
                    return
                last_error = f"health endpoint returned HTTP {response.status}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(2)

    process.terminate()
    raise TimeoutError(
        f"llama-server did not become healthy within {timeout_seconds}s: {last_error}"
    )


def server_command() -> list[str]:
    """Build the shared llama-server command for deployment and smoke tests."""
    return [
        "/opt/llama.cpp/build/bin/llama-server",
        "--model",
        str(MODEL_PATH),
        "--mmproj",
        str(MMPROJ_PATH),
        "--host",
        "0.0.0.0",
        "--port",
        str(SERVER_PORT),
        "--n-gpu-layers",
        "all",
        "--ctx-size",
        "8192",
        "--parallel",
        "1",
        "--flash-attn",
        "on",
        "--cache-type-k",
        "q8_0",
        "--cache-type-v",
        "q8_0",
        "--spec-type",
        "draft-mtp",
        "--spec-draft-n-max",
        "2",
        "--jinja",
        "--metrics",
        "--log-timestamps",
    ]


def assessment_schema() -> dict[str, object]:
    """Return the scam-assessment JSON schema used by smoke tests."""
    return {
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
        "required": [
            "risk_label",
            "simple_explanation",
            "red_flags",
            "safe_next_steps",
            "reply_draft",
        ],
        "additionalProperties": False,
    }


@app.function(
    image=llama_image,
    gpu="L40S",
    volumes={str(MODEL_DIR): model_volume},
    timeout=30 * MINUTES,
)
def smoke_test() -> dict[str, object]:
    """Exercise the OpenAI route inside the same GPU container."""
    from openai import OpenAI

    if not MODEL_PATH.exists() or not MMPROJ_PATH.exists():
        raise FileNotFoundError("model or multimodal projector is missing")

    command = server_command()
    print("Starting llama-server:", " ".join(command), flush=True)
    started_at = time.monotonic()
    process = subprocess.Popen(command)
    try:
        wait_for_server(process, timeout_seconds=20 * MINUTES)
        load_seconds = time.monotonic() - started_at
        gpu_state = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        payload = {
            "model": "qwen3.6-27b-mtp",
            "messages": [
                {
                    "role": "system",
                    "content": "Return only JSON matching the supplied schema.",
                },
                {
                    "role": "user",
                    "content": (
                        "Assess this message for a person in Pakistan: "
                        "'Pakistan Post: pay Rs. 85 at pakpost-delivery.example "
                        "today or your parcel will be destroyed.'"
                    ),
                },
            ],
            "temperature": 0.2,
            "max_tokens": 500,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "scam_assessment",
                    "strict": True,
                    "schema": assessment_schema(),
                },
            },
        }
        client = OpenAI(
            api_key="not-used-by-llama-server",
            base_url=f"http://127.0.0.1:{SERVER_PORT}/v1",
            timeout=15 * MINUTES,
            max_retries=0,
        )
        inference_started_at = time.monotonic()
        completion = client.chat.completions.create(
            model=payload["model"],
            messages=payload["messages"],
            temperature=payload["temperature"],
            max_tokens=payload["max_tokens"],
            response_format=payload["response_format"],
            extra_body={
                "chat_template_kwargs": payload["chat_template_kwargs"],
            },
        )
        inference_seconds = time.monotonic() - inference_started_at
        body = completion.model_dump()
        raw_content = completion.choices[0].message.content
        if not raw_content:
            raise RuntimeError(
                "model returned empty content; response was: "
                + json.dumps(body, ensure_ascii=False)
            )
        content = json.loads(raw_content)
        result = {
            "load_seconds": round(load_seconds, 2),
            "inference_seconds": round(inference_seconds, 2),
            "gpu": gpu_state,
            "finish_reason": body["choices"][0].get("finish_reason"),
            "usage": body.get("usage", {}),
            "assessment": content,
        }
        print(json.dumps(result, indent=2), flush=True)
        return result
    finally:
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()


@app.function(
    image=llama_image,
    gpu="L40S",
    volumes={str(MODEL_DIR): model_volume},
    timeout=30 * MINUTES,
)
def smoke_test_images() -> list[dict[str, object]]:
    """Analyze both scam screenshots through the OpenAI-compatible vision API."""
    from openai import OpenAI

    if not MODEL_PATH.exists() or not MMPROJ_PATH.exists():
        raise FileNotFoundError("model or multimodal projector is missing")

    image_paths = [TEST_IMAGE_DIR / "scam_1.png", TEST_IMAGE_DIR / "scam_2.png"]
    missing_images = [str(path) for path in image_paths if not path.exists()]
    if missing_images:
        raise FileNotFoundError("missing test images: " + ", ".join(missing_images))

    command = server_command()
    print("Starting llama-server:", " ".join(command), flush=True)
    process = subprocess.Popen(command)
    try:
        wait_for_server(process, timeout_seconds=20 * MINUTES)
        client = OpenAI(
            api_key="not-used-by-llama-server",
            base_url=f"http://127.0.0.1:{SERVER_PORT}/v1",
            timeout=15 * MINUTES,
            max_retries=0,
        )
        results: list[dict[str, object]] = []
        for image_path in image_paths:
            image_url = (
                "data:image/png;base64,"
                + base64.b64encode(image_path.read_bytes()).decode("ascii")
            )
            started_at = time.monotonic()
            completion = client.chat.completions.create(
                model="qwen3.6-27b-mtp",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Analyze suspicious notices and messages for people in "
                            "Pakistan. Read the image carefully and return only JSON "
                            "matching the supplied schema. Do not invent URLs or "
                            "contact details. The reply_draft must be polite, safe, "
                            "and must not repeat insults or abusive language visible "
                            "in the input."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Assess this screenshot for scam risk. Explain "
                                    "the visible evidence and give safe next steps."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    },
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "scam_assessment",
                        "strict": True,
                        "schema": assessment_schema(),
                    },
                },
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                },
            )
            content = completion.choices[0].message.content
            if not content:
                raise RuntimeError(f"{image_path.name} returned empty content")
            assessment = json.loads(content)
            result = {
                "image": image_path.name,
                "seconds": round(time.monotonic() - started_at, 2),
                "finish_reason": completion.choices[0].finish_reason,
                "usage": completion.usage.model_dump() if completion.usage else {},
                "assessment": assessment,
            }
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
            results.append(result)
        return results
    finally:
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()


@app.function(
    image=llama_image,
    gpu="L40S",
    volumes={str(MODEL_DIR): model_volume},
    timeout=30 * MINUTES,
    startup_timeout=30 * MINUTES,
    scaledown_window=5 * MINUTES,
    min_containers=0,
    max_containers=1,
)
@modal.concurrent(max_inputs=1)
@modal.web_server(
    port=SERVER_PORT,
    startup_timeout=25 * MINUTES,
    requires_proxy_auth=True,
)
def serve() -> None:
    """Start a private OpenAI-compatible llama-server endpoint."""
    if not MODEL_PATH.exists() or not MMPROJ_PATH.exists():
        raise FileNotFoundError(
            "The model or multimodal projector is missing. Run `modal run "
            "experiments/modal_qwen36_mtp/modal_app.py::download_model` first."
        )

    command = server_command()
    print("Starting llama-server:", " ".join(command), flush=True)
    started_at = time.monotonic()
    process = subprocess.Popen(command, env={**os.environ, "LLAMA_CACHE": str(MODEL_DIR)})
    wait_for_server(process, timeout_seconds=20 * MINUTES)
    print(
        f"llama-server ready after {time.monotonic() - started_at:.2f} seconds",
        flush=True,
    )

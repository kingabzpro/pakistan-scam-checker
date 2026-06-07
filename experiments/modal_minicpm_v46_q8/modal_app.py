"""Serve MiniCPM-V 4.6 Q8 GGUF on Modal with llama.cpp."""

from __future__ import annotations

import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import modal

APP_NAME = "pakistan-scam-checker-minicpm-v46-q8"
LLAMA_CPP_COMMIT = "9e3b928fd8c9d14dbf15a8768b9fdd7e5c721d66"
MODEL_REPO = "openbmb/MiniCPM-V-4.6-gguf"
MODEL_FILENAME = "MiniCPM-V-4_6-Q8_0.gguf"
MMPROJ_FILENAME = "mmproj-model-f16.gguf"
MODEL_NAME = "minicpm-v-4.6-q8"
MODEL_DIR = Path("/models")
MODEL_PATH = MODEL_DIR / MODEL_FILENAME
MMPROJ_PATH = MODEL_DIR / MMPROJ_FILENAME
MODEL_VOLUME_NAME = "pakistan-scam-checker-minicpm-v46-models"
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
        "cmake --build /opt/llama.cpp/build --target llama-server --parallel",
    )
)


@app.function(
    image=download_image,
    volumes={str(MODEL_DIR): model_volume},
    timeout=15 * MINUTES,
)
def download_model() -> dict[str, object]:
    """Download the Q8 model and vision projector to a persistent Volume."""
    from huggingface_hub import hf_hub_download

    started_at = time.monotonic()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = Path(
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MODEL_FILENAME,
            local_dir=str(MODEL_DIR),
        )
    )
    mmproj_path = Path(
        hf_hub_download(
            repo_id=MODEL_REPO,
            filename=MMPROJ_FILENAME,
            local_dir=str(MODEL_DIR),
        )
    )
    model_volume.commit()
    result = {
        "model_path": str(model_path),
        "model_size_bytes": model_path.stat().st_size,
        "mmproj_path": str(mmproj_path),
        "mmproj_size_bytes": mmproj_path.stat().st_size,
        "download_seconds": round(time.monotonic() - started_at, 2),
    }
    print(result, flush=True)
    return result


@app.function(
    image=download_image,
    volumes={str(MODEL_DIR): model_volume},
    timeout=2 * MINUTES,
)
def model_status() -> dict[str, object]:
    """Report whether both required model files are present."""
    result = {
        "downloaded": MODEL_PATH.exists() and MMPROJ_PATH.exists(),
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists(),
        "model_size_bytes": MODEL_PATH.stat().st_size if MODEL_PATH.exists() else 0,
        "mmproj_path": str(MMPROJ_PATH),
        "mmproj_exists": MMPROJ_PATH.exists(),
        "mmproj_size_bytes": (
            MMPROJ_PATH.stat().st_size if MMPROJ_PATH.exists() else 0
        ),
    }
    print(result, flush=True)
    return result


def server_command() -> list[str]:
    """Build the llama-server command used by the deployed endpoint."""
    return [
        "/opt/llama.cpp/build/bin/llama-server",
        "--model",
        str(MODEL_PATH),
        "--mmproj",
        str(MMPROJ_PATH),
        "--alias",
        MODEL_NAME,
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
        "--jinja",
        "--metrics",
        "--log-timestamps",
    ]


def wait_for_server(process: subprocess.Popen[bytes], timeout_seconds: int) -> None:
    """Wait for llama-server health or fail with its exit status."""
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


@app.function(
    image=llama_image,
    gpu="L4",
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
    """Start the private OpenAI-compatible MiniCPM endpoint."""
    if not MODEL_PATH.exists() or not MMPROJ_PATH.exists():
        raise FileNotFoundError(
            "Model files are missing. Run `modal run "
            "experiments/modal_minicpm_v46_q8/modal_app.py::download_model`."
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

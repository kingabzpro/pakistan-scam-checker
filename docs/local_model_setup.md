# Local model setup

Pakistan Notice Helper uses the OpenAI Python SDK as a client for any
OpenAI-compatible model server. It does not call OpenAI cloud APIs by default.

## Environment

```powershell
$env:MODEL_BASE_URL = "http://127.0.0.1:8080"
$env:MODEL_NAME = "qwen3.6-27b-mtp"
$env:MODEL_API_KEY = ""
python app.py
```

`MODEL_BASE_URL` may include `/v1`; the app adds it when absent. An API key is
optional for local servers. `MODEL_TIMEOUT_SECONDS` defaults to 180 seconds.

## llama.cpp example

Start a recent `llama-server` build with the model and multimodal projector:

```bash
llama-server \
  --model Qwen3.6-27B-UD-Q4_K_XL.gguf \
  --mmproj mmproj-F16.gguf \
  --host 127.0.0.1 --port 8080 \
  --ctx-size 8192 --n-gpu-layers all \
  --jinja --flash-attn on \
  --spec-type draft-mtp --spec-draft-n-max 2
```

Images require the vision projector. Without `--mmproj`, use pasted text. The
Space performs no OCR and does not send input to any separate OCR service.

Run `python app.py --test-endpoint` before opening the UI. The test sends a
synthetic suspicious Pakistan Post message and validates all output fields.

## Demo mode

Unset `MODEL_BASE_URL` or `MODEL_NAME` to use local rule-based checks:

```powershell
Remove-Item Env:MODEL_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:MODEL_NAME -ErrorAction SilentlyContinue
python app.py
```

Image-only analysis is unavailable in demo mode because the app intentionally
does not include OCR. Paste visible text to run the local checks.

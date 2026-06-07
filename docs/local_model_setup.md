# Local model setup

Pakistan Notice Helper currently defaults to its deployed Modal model. The
OpenAI Python SDK is used only as a client for that OpenAI-compatible server.

## Environment

```powershell
$env:MODEL_BASE_URL = "http://127.0.0.1:8080"
$env:MODEL_NAME = "qwen3.5-4b-q8"
$env:MODEL_API_KEY = ""
python app.py
```

`MODEL_BASE_URL` may include `/v1`; the app adds it when absent. An API key is
optional for local servers. `MODEL_TIMEOUT_SECONDS` defaults to 180 seconds.

## llama.cpp example

Start a recent `llama-server` build with the model and multimodal projector:

```bash
llama-server \
  --model Qwen3.5-4B-Q8_0.gguf \
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

These variables override the permanent Modal defaults, making the later switch
to a local server possible without changing application code. There is no
rule-based fallback: when the selected model is unavailable, the UI reports
the error and does not return an assessment.

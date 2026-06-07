---
title: Pakistan Notice Helper
emoji: 🛡️
colorFrom: green
colorTo: green
sdk: gradio
sdk_version: 6.15.1
app_file: app.py
pinned: false
license: mit
---

# Pakistan Notice Helper

Pakistan Notice Helper is a model-powered safety assistant for confusing or
suspicious Pakistani notices, bills, SMS messages, bank alerts, FBR-style
messages, challans, and courier/customs messages. It accepts pasted text and
screenshots, then returns:

- **Risk label:** Looks normal, Verify first, Suspicious, or Likely scam
- A simple English explanation
- Red flags found
- Safe next steps
- A polite reply draft

The interface is a custom mobile-first frontend served by
[`gradio.Server`](https://www.gradio.app/main/guides/server-mode). Gradio
provides queueing, API routes, and Hugging Face Spaces hosting without exposing
a default Gradio UI.

> **Pakistan Notice Helper does not provide official verification. It checks
> common scam signals and gives safe next steps. Always verify through official
> websites or helplines before making payments or sharing personal
> information.**

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:7860`. Local runs bind to localhost by default. On
Hugging Face Spaces, the app automatically binds to `0.0.0.0`.

Useful checks:

```bash
python -m py_compile app.py
python app.py --self-test
python app.py --test-endpoint
```

The last command requires Modal proxy credentials.

## Model configuration

The app uses the standard OpenAI Python SDK as a client for an
OpenAI-compatible endpoint. It does not call OpenAI cloud APIs by default.

| Variable | Purpose |
| --- | --- |
| `MODEL_BASE_URL` | Optional override for the built-in Modal endpoint |
| `MODEL_NAME` | Optional override for the built-in model ID |
| `MODEL_API_KEY` | Optional endpoint API key |
| `MODEL_TIMEOUT_SECONDS` | Optional request timeout; default is 180 seconds |
| `MODAL_PROXY_KEY` | Optional Modal proxy authentication key |
| `MODAL_PROXY_SECRET` | Optional Modal proxy authentication secret |

The current defaults are:

```text
MODEL_BASE_URL=https://abidali899--pakistan-scam-checker-qwen36-mtp-serve.modal.run
MODEL_NAME=qwen3.6-27b-mtp
```

See [local model setup](docs/local_model_setup.md) and
[endpoint testing](docs/model_endpoint_testing.md).

## Model behavior

The app sends text and optional image data to the configured multimodal
OpenAI-compatible endpoint and validates its structured response.

The six built-in text and screenshot examples use precomputed assessments.
Trying those examples does not call or wake the Modal endpoint. Editing an
example or uploading a different image switches back to normal model analysis.

There is no rule-based or sample fallback for user-submitted input. If
credentials are missing, the endpoint is unavailable, or the model returns
invalid output, the app displays a clear error and does not manufacture an
assessment.

## Architecture

```text
Custom HTML/CSS/JavaScript frontend
        |
        | Gradio POST + SSE protocol
        v
Queued gradio.Server backend
        |
        | OpenAI Python SDK
        v
Deployed/local OpenAI-compatible endpoint
        |
        v
unsloth/Qwen3.6-27B-MTP-GGUF
```

All frontend assets are local. The app has no runtime CDN, analytics, OCR, MCP,
or OpenAI Agents SDK. Analysis currently depends on the deployed Modal model.

## Hugging Face Spaces

Push this repository to a new Gradio Space. The metadata at the top of this
README pins Gradio and launches `app.py`. Add `MODAL_PROXY_KEY` and
`MODAL_PROXY_SECRET` under **Space Settings → Secrets**. The endpoint URL and
model name are built into the app; `MODEL_BASE_URL` and `MODEL_NAME` remain
available as overrides for a future local deployment.

## Privacy and limitations

- Submitted text and images are sent to the configured Modal endpoint and are
  not saved by this app.
- The `traces/` directory contains only a placeholder; runtime tracing is off.
- Do not upload private personal data unless you trust the Modal deployment.
- No automated result proves that a notice is genuine or fraudulent.
- Image analysis requires a multimodal endpoint with its vision projector.

## Project structure

```text
app.py
requirements.txt
README.md
FIELD_NOTES.md
docs/
  local_model_setup.md
  model_endpoint_testing.md
  research_notes.md
  model_experiment_notes.md
data/
  examples.jsonl
sample_inputs/
traces/
static/
  index.html
  styles.css
  app.js
experiments/
  modal_qwen36_mtp/
```

Existing public and synthetic examples in `data/examples.jsonl` cover courier,
traffic challan, bank, FBR, wallet, job, utility, WhatsApp, and education scam
patterns. Source screenshots are stored under `sample_inputs/`.

## Official reporting channels

Use contact details that you navigate to independently:

- [PTA Complaint Management System](https://complaint.pta.gov.pk/)
- [FIA Complaint Portal](https://complaint.fia.gov.pk/)
- [State Bank of Pakistan](https://www.sbp.org.pk/)
- [Federal Board of Revenue](https://www.fbr.gov.pk/)
- The official bank, courier, utility, traffic authority, or government website
  relevant to the notice

Never call a number or open a link merely because it appears inside the message
being checked.

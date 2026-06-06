---
title: Pakistan Notice Helper
emoji: 🇵🇰
colorFrom: green
colorTo: emerald
sdk: gradio
sdk_version: 6.15.1
app_file: app.py
pinned: false
license: mit
---

# Pakistan Notice Helper

Pakistan Notice Helper is a local-first safety assistant for confusing or
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

Open `http://127.0.0.1:7860`. No secret or model server is required for demo
mode.

Useful checks:

```bash
python -m py_compile app.py
python app.py --self-test
python app.py --test-endpoint
```

The last command requires a configured endpoint.

## Model configuration

The app uses the standard OpenAI Python SDK as a client for an
OpenAI-compatible endpoint. It does not call OpenAI cloud APIs by default.

| Variable | Purpose |
| --- | --- |
| `MODEL_BASE_URL` | Deployed or local endpoint root, with or without `/v1` |
| `MODEL_NAME` | Model name or server model ID |
| `MODEL_API_KEY` | Optional endpoint API key |
| `MODEL_TIMEOUT_SECONDS` | Optional request timeout; default is 180 seconds |
| `MODAL_PROXY_KEY` | Optional Modal proxy authentication key |
| `MODAL_PROXY_SECRET` | Optional Modal proxy authentication secret |

Example:

```powershell
$env:MODEL_BASE_URL = "http://127.0.0.1:8080"
$env:MODEL_NAME = "qwen3.6-27b-mtp"
$env:MODEL_API_KEY = ""
python app.py
```

See [local model setup](docs/local_model_setup.md) and
[endpoint testing](docs/model_endpoint_testing.md).

## Operating modes

**Connected model mode:** sends text and optional image data to the configured
multimodal OpenAI-compatible endpoint and validates its structured response.

**Rule-based fallback:** checks pasted text locally for credential requests,
urgency, threats, suspicious links, personal mobile numbers, impersonation,
prizes/refunds, unusual payments, and advance fees.

**Demo/sample mode:** loads without endpoint configuration. Example cards and
text checks remain usable. Image-only analysis asks the user to paste visible
text because the Space intentionally does not include OCR.

If a configured endpoint is unavailable or returns invalid output, the app
shows **Model server not connected** and falls back without crashing.

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

All frontend assets are local. The app has no runtime CDN, analytics, web API,
OCR, MCP, OpenAI Agents SDK, or mandatory cloud dependency.

## Hugging Face Spaces

Push this repository to a new Gradio Space. The metadata at the top of this
README pins Gradio and launches `app.py`. Add endpoint settings under **Space
Settings → Variables and secrets** only when model-backed analysis is needed:

- Variables: `MODEL_BASE_URL`, `MODEL_NAME`
- Secret: `MODEL_API_KEY` when required
- Secrets: `MODAL_PROXY_KEY`, `MODAL_PROXY_SECRET` for the current private
  Modal experiment

The Space remains functional without any of these values.

## Privacy and limitations

- Submitted text and images are processed in memory and are not saved by this
  app.
- The `traces/` directory contains only a placeholder; runtime tracing is off.
- A configured remote endpoint receives the submitted content. Review that
  endpoint's privacy policy before using it with sensitive notices.
- Do not upload private personal data unless you trust the configured endpoint.
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

## License

MIT. See [LICENSE](LICENSE).

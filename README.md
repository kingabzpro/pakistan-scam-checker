# Pakistan Notice Helper

Pakistan Notice Helper is a Qwen3.6-powered safety assistant for confusing or
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

## Build Small Hackathon

This is a **Backyard AI** project built for the
[Build Small Hackathon](https://huggingface.co/build-small-hackathon). It
addresses a common local problem: people receive convincing payment notices,
bank alerts, courier messages, challans, and government impersonation scams
but may not know which details are unsafe.

- **Space:** [build-small-hackathon/pakistan-notice-helper](https://huggingface.co/spaces/build-small-hackathon/pakistan-notice-helper)
- **Source:** [kingabzpro/pakistan-notice-helper](https://github.com/kingabzpro/pakistan-notice-helper)
- **Model:** `unsloth/Qwen3.6-27B-MTP-GGUF` (27B parameters)
- **Inference:** CUDA-enabled `llama.cpp` on a Modal L40S
- **Interface:** custom mobile-first frontend on `gradio.Server`
- **Open traces:** [privacy-safe trace dataset](https://huggingface.co/datasets/build-small-hackathon/pakistan-notice-helper-traces)
- **Build report:** [field notes](FIELD_NOTES.md)

The project targets the Backyard AI main track, OpenAI Codex Track, Modal
Awards, and the Llama Champion, Off-Brand, Sharing is Caring, and Field Notes
bonus quests.

### Why it qualifies

| Requirement or category | Project evidence |
| --- | --- |
| **Small Models Only** | Uses Qwen3.6 27B MTP, below the 32B parameter limit. |
| **Built on Gradio** | Runs as a Gradio Space under the hackathon organization using `gradio.Server`. |
| **Backyard AI: specific problem** | Helps people in Pakistan assess suspicious local notices, payment demands, courier messages, challans, and government impersonation scams. |
| **Backyard AI: small-model fit** | A quantized 27B GGUF handles text, screenshots, Roman Urdu, and structured safety guidance through `llama.cpp`. |
| **Backyard AI: polished app** | Provides a custom responsive interface, bundled examples, clear failures, safety disclaimers, and structured results. |
| **Modal Awards** | The live model endpoint runs on a Modal L40S with persistent model storage and proxy authentication. |
| **OpenAI Codex Track** | The public GitHub repository contains Codex-attributed commits and is linked from this Space. |
| **Llama Champion** | Model inference runs through a pinned CUDA-enabled `llama.cpp` build. |
| **Off-Brand** | Uses a custom HTML, CSS, and JavaScript frontend instead of the default Gradio interface. |
| **Sharing is Caring** | Publishes opt-out, privacy-safe traces as a public Hugging Face dataset. |
| **Field Notes** | Documents design decisions, measured performance, failed approaches, privacy tradeoffs, and limitations. |

The final submission must also include a short demo video, a social-media post,
and evidence that a target user tried the app. These are submission and
Backyard AI judging requirements, not features that repository metadata can
prove.

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
| `HF_TOKEN` | Scoped Hugging Face token used by the background trace uploader |
| `HF_TRACE_DATASET_REPO` | Trace dataset repo; defaults to `build-small-hackathon/pakistan-notice-helper-traces` |
| `TRACE_BATCH_SIZE` | Trace records per shard; default is 20 |
| `TRACE_FLUSH_SECONDS` | Maximum batching delay; default is 60 seconds |

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

The six built-in text and screenshot examples use assessments generated by the
same deployed Qwen model and stored in `data/example_assessments.json`. Trying
those examples does not call or wake the Modal endpoint, and the UI labels them
as **Cached Modal result**. Editing an example or uploading a different image
switches back to normal model analysis.

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
        | Modal L40S + CUDA llama-server
        v
llama.cpp runtime
        |
        v
unsloth/Qwen3.6-27B-MTP-GGUF
```

All frontend assets are local. The app has no runtime CDN, analytics, OCR, MCP,
or OpenAI Agents SDK. The OpenAI Python package is only an HTTP client for the
OpenAI-compatible `llama-server` endpoint; requests are not sent to OpenAI.
Analysis currently depends on the deployed Modal model.

## Sharing is Caring: Open Traces

The app publishes optional privacy-safe backend traces to
[`build-small-hackathon/pakistan-notice-helper-traces`](https://huggingface.co/datasets/build-small-hackathon/pakistan-notice-helper-traces).
The checkbox is visible and enabled by default on each request, and users can
turn it off before submitting.

Trace creation is deterministic Python logic and makes no additional model
request. Text inputs are aggressively redacted and capped at 500 characters;
images use a fixed `image: ...` description without OCR or image storage. The
trace also records category, urgency, fixed signals, result counts, and a
deterministic `result_summary` explaining the scam pattern and risk label.
All trace columns are flat scalar values; no dataset cell contains a nested
dictionary. Detected signals are combined into the readable `scam_tactics`
column.
It never stores raw messages, screenshots, links, detected identifiers, model
explanations, reply text, exceptions, or credentials.

Safe records are queued without blocking the response, written in batches of
20 or after 60 seconds, and uploaded as unique JSONL shards. Hub failures leave
the shard pending for a later retry and do not affect scam analysis.

Operator commands:

```bash
python -m traces.scripts.seed_trace_dataset
python -m traces.scripts.validate_traces
python -m traces.scripts.create_trace_dataset --dry-run
python -m traces.scripts.create_trace_dataset
python -m traces.scripts.create_trace_dataset --replace-data
python -m traces.scripts.export_pending_traces --dry-run
python -m traces.scripts.upload_trace_shards --dry-run
```

See [the dataset card](traces/dataset_card.md) for the schema, privacy
policy, provenance, and limitations.

## Deployment

The app is deployed as a Gradio Space under the Build Small Hackathon
organization. The metadata at the top of this README pins Gradio, identifies
the Backyard AI track, and launches `app.py`.

Add `MODAL_PROXY_KEY` and `MODAL_PROXY_SECRET` under
**Space Settings → Secrets**. The endpoint URL and model name are built into
the app; `MODEL_BASE_URL` and `MODEL_NAME` remain available as overrides for a
future local deployment.

## Privacy and limitations

- Submitted text and images are sent to the configured Modal endpoint and are
  not saved by this app.
- Public traces contain only allow-listed metadata, buckets, booleans, counts,
  and fixed summaries. Tracing can be disabled per request.
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
  example_assessments.json
traces/
  runtime.py
  dataset_card.md
  data/
    trace_samples.jsonl
  scripts/
    create_trace_dataset.py
    seed_trace_dataset.py
    validate_traces.py
    export_pending_traces.py
    upload_trace_shards.py
static/
  index.html
  styles.css
  app.js
experiments/
  modal_qwen36_mtp/
```

The six bundled examples have cached Modal assessments and deterministic seed
traces. Runtime trace shards are kept out of Git and uploaded separately.

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

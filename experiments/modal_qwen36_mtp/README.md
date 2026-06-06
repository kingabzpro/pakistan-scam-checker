# Qwen3.6 27B MTP Modal experiment

This experiment runs
[`unsloth/Qwen3.6-27B-MTP-GGUF`](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
with CUDA-enabled `llama-server` on one Modal L40S. It exposes llama.cpp's
OpenAI-compatible `/v1/chat/completions` route without calling OpenAI or any
cloud LLM API.

This deployment is only an infrastructure and model-compatibility experiment.
The hackathon application remains local-first and offline-capable. A Hugging
Face Space may be offered as a fallback, but Modal is not the intended primary
application backend.

## Configuration

- Model: `unsloth/Qwen3.6-27B-MTP-GGUF`
- Quant: `Qwen3.6-27B-UD-Q4_K_XL.gguf` (about 17.9 GB)
- llama.cpp commit: `5a69c974392020e514c3b2b2910bb92f847cb4c9`
- GPU: one L40S with 48 GB VRAM
- Context: 8,192 tokens
- KV cache: Q8 for keys and values
- MTP: `--spec-type draft-mtp --spec-draft-n-max 2`
- Endpoint: proxy-authenticated `/v1/chat/completions`

An L40S provides useful headroom for model weights, CUDA buffers, and the KV
cache. A 24 GB GPU is expected to be tight and may need a shorter context,
lower-precision KV cache, or partial CPU offload.

## Prerequisites

Install and authenticate Modal, plus install the OpenAI Python SDK for the test
client:

```powershell
python -m pip install "modal==1.3.5" "openai==2.33.0"
modal setup
```

No Hugging Face token is required while the repository remains public.
The OpenAI SDK is configured with the Modal URL as its `base_url`; it sends no
request to OpenAI and uses no OpenAI API key.

## Download and deploy

The model is downloaded once into a persistent Modal Volume:

```powershell
modal run experiments/modal_qwen36_mtp/modal_app.py::download_model
modal run experiments/modal_qwen36_mtp/modal_app.py::model_status
modal deploy experiments/modal_qwen36_mtp/modal_app.py
```

The deploy command prints a URL similar to:

```text
https://WORKSPACE--pakistan-scam-checker-qwen36-mtp-serve.modal.run
```

Create a Modal proxy-auth token in the Modal dashboard, then set:

```powershell
$env:QWEN_ENDPOINT_URL = "https://WORKSPACE--pakistan-scam-checker-qwen36-mtp-serve.modal.run"
$env:MODAL_PROXY_KEY = "wk-..."
$env:MODAL_PROXY_SECRET = "ws-..."
python experiments/modal_qwen36_mtp/test_request.py
```

The client uses `OpenAI(..., base_url="$QWEN_ENDPOINT_URL/v1")`, retries `503
Service Unavailable` during a cold start, validates the OpenAI-compatible
envelope, parses the assistant's JSON, and requires:

- `risk_label`
- `simple_explanation`
- `red_flags`
- `safe_next_steps`
- `reply_draft`

Run local validation without contacting Modal:

```powershell
python experiments/modal_qwen36_mtp/test_request.py --self-test
```

## Direct request

```bash
curl "$QWEN_ENDPOINT_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Modal-Key: $MODAL_PROXY_KEY" \
  -H "Modal-Secret: $MODAL_PROXY_SECRET" \
  -d '{
    "model": "qwen3.6-27b-mtp",
    "messages": [{"role": "user", "content": "Is an urgent parcel fee link suspicious?"}],
    "max_tokens": 200
  }'
```

## Local llama-server equivalent

With a recent CUDA-enabled llama.cpp build and the GGUF downloaded locally:

```bash
llama-server \
  -m Qwen3.6-27B-UD-Q4_K_XL.gguf \
  --host 127.0.0.1 --port 8080 \
  -ngl all -c 8192 -np 1 -fa on \
  -ctk q8_0 -ctv q8_0 \
  --spec-type draft-mtp --spec-draft-n-max 2 \
  --jinja
```

Point `QWEN_ENDPOINT_URL` at `http://127.0.0.1:8080` and omit the Modal headers
when adapting the SDK client for a purely local run. The placeholder SDK API
key is ignored by llama-server.

## Operations and troubleshooting

- Inspect logs with `modal app logs pakistan-scam-checker-qwen36-mtp`.
- A first download can take several minutes. Later replicas read the GGUF from
  the persistent Volume.
- A `503` normally means no replica is ready yet; the provided client retries.
- A `401` means the `Modal-Key` or `Modal-Secret` header is missing or invalid.
- An MTP argument error means the llama.cpp commit/build does not include the
  expected `draft-mtp` support. Confirm the pinned commit and image build logs.
- CUDA out-of-memory errors can be investigated by reducing context or changing
  KV cache types before considering partial CPU offload.
- JSON validation failures are model-output failures, not successful smoke
  tests. Keep the schema constraint enabled.

Stop the deployed app when the experiment is complete:

```powershell
modal app stop pakistan-scam-checker-qwen36-mtp
```

The Volume is intentionally retained to avoid another 17.9 GB download. Delete
it separately only when the cached model is no longer needed:

```powershell
modal volume delete pakistan-scam-checker-qwen36-models
```

## References

- [Unsloth Qwen3.6 guide](https://unsloth.ai/docs/models/qwen3.6)
- [Unsloth model repository](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
- [llama-server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
- [Modal web server documentation](https://modal.com/docs/guide/webhooks)

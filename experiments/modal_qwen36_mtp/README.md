# Qwen3.6 27B MTP Modal experiment

This experiment runs
[`unsloth/Qwen3.6-27B-MTP-GGUF`](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
with CUDA-enabled `llama-server` on one Modal L40S. It exposes llama.cpp's
OpenAI-compatible `/v1/chat/completions` route without calling OpenAI or any
cloud LLM API.

This deployment is the hackathon application's primary inference backend. The
Hugging Face Space sends text and screenshots to this proxy-authenticated
endpoint, while the same application code can target a local `llama-server`
through environment-variable overrides.

## Configuration

- Model: `unsloth/Qwen3.6-27B-MTP-GGUF`
- Quant: `Qwen3.6-27B-UD-Q4_K_XL.gguf` (about 17.9 GB)
- Vision projector: `mmproj-F16.gguf` (about 0.93 GB)
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
modal run experiments/modal_qwen36_mtp/modal_app.py::smoke_test_images
modal deploy experiments/modal_qwen36_mtp/modal_app.py
```

The deploy command prints a URL similar to:

```text
https://WORKSPACE--pakistan-scam-checker-qwen36-mtp-serve.modal.run
```

## Configure proxy authentication

Modal account/CLI tokens (`ak-`/`as-`) are not valid for Web Function proxy
authentication. The endpoint requires a dedicated Proxy Auth Token whose ID
starts with `wk-` and whose secret starts with `ws-`.

1. Sign in and open
   [Modal Settings → Proxy Auth Tokens](https://modal.com/settings/proxy-auth-tokens).
2. Select **New Token** and give it a descriptive name such as
   `pakistan-scam-checker-local-test`.
3. If Modal asks for environments, select the environment containing the
   `pakistan-scam-checker-qwen36-mtp` deployment (currently `main`).
4. Copy both values immediately. Modal shows the token secret only once.
5. Set them in the same PowerShell session used to run the test:

```powershell
$env:QWEN_ENDPOINT_URL = "https://abidali899--pakistan-scam-checker-qwen36-mtp-serve.modal.run"
$env:MODAL_PROXY_KEY = "wk-..."
$env:MODAL_PROXY_SECRET = "ws-..."
python experiments/modal_qwen36_mtp/test_request.py
```

Do not use `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`, or values printed by
`modal token info`; those authenticate the Modal CLI/API and return HTTP 401
when used as proxy credentials.

To persist the values for future terminals on Windows:

```powershell
setx QWEN_ENDPOINT_URL "https://abidali899--pakistan-scam-checker-qwen36-mtp-serve.modal.run"
setx MODAL_PROXY_KEY "wk-..."
setx MODAL_PROXY_SECRET "ws-..."
```

`setx` affects newly opened terminals, not the current one. Close and reopen
PowerShell before testing, or also set the `$env:` values above.

The client uses `OpenAI(..., base_url="$QWEN_ENDPOINT_URL/v1")`, retries `503
Service Unavailable` during a cold start, validates the OpenAI-compatible
envelope, parses the assistant's JSON, and requires:

- `risk_label`
- `simple_explanation`
- `red_flags`
- `safe_next_steps`
- `reply_draft`

### Verified HTTP endpoint

The proxy-authenticated production URL was tested successfully on June 6, 2026:

```text
https://abidali899--pakistan-scam-checker-qwen36-mtp-serve.modal.run
```

The tests used `test_request.py`, the OpenAI Python SDK, and actual
`Modal-Key`/`Modal-Secret` headers. They did not call the internal Modal smoke
functions.

| Input | Risk | HTTP time | Prompt tokens | Completion tokens |
| --- | --- | ---: | ---: | ---: |
| Text parcel scam | High | 5.83 s | 148 | 226 |
| `scam_1.png` | High | 7.80 s | 1,033 | 233 |
| `scam_2.png` | High | 9.44 s | 403 | 385 |

Image requests allow up to 750 completion tokens because the denser Roman Urdu
screenshot produced truncated JSON with the original 500-token limit. The
system prompt also requires a polite reply draft that does not repeat abusive
language visible in screenshots.

Run local validation without contacting Modal:

```powershell
python experiments/modal_qwen36_mtp/test_request.py --self-test
```

## Vision test

The experiment includes two screenshots:

- `images/scam_1.png`: fake Pakistan Post failed-delivery link
- `images/scam_2.png`: Roman Urdu prize message redirecting to WhatsApp

Run both through the deployed OpenAI-compatible HTTP endpoint:

```powershell
python experiments/modal_qwen36_mtp/test_request.py --images
```

The test base64-encodes each PNG, sends it as an OpenAI SDK `image_url` content
part, and requests the same structured scam-assessment JSON used by the text
test. It verifies that llama.cpp can run vision and MTP together.

The first result identified the suspicious delivery link, urgency, and missing
parcel details. The second read the Roman Urdu text, detected the iPhone/gift
lure and WhatsApp redirection, and extracted the visible phone numbers. Treat
all extracted phone numbers, URLs, and contact details as untrusted input.

Equivalent OpenAI SDK image content:

```python
import base64
import os
from pathlib import Path

from openai import OpenAI

image_bytes = Path(
    "experiments/modal_qwen36_mtp/images/scam_1.png"
).read_bytes()
image_url = "data:image/png;base64," + base64.b64encode(image_bytes).decode()

client = OpenAI(
    api_key="not-used-by-llama-server",
    base_url=f"{os.environ['QWEN_ENDPOINT_URL'].rstrip('/')}/v1",
    default_headers={
        "Modal-Key": os.environ["MODAL_PROXY_KEY"],
        "Modal-Secret": os.environ["MODAL_PROXY_SECRET"],
    },
)

completion = client.chat.completions.create(
    model="qwen3.6-27b-mtp",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Assess this screenshot for scam risk."},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ],
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)
print(completion.choices[0].message.content)
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
  --mmproj mmproj-F16.gguf \
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
  Confirm that the values begin with `wk-` and `ws-`, and that an RBAC-scoped
  token includes the deployment's environment.
- An MTP argument error means the llama.cpp commit/build does not include the
  expected `draft-mtp` support. Confirm the pinned commit and image build logs.
- Image requests require `mmproj-F16.gguf`; without `--mmproj`, the text model
  cannot inspect screenshots even if the request uses OpenAI image syntax.
- The projector reported an estimated worst-case memory requirement of about
  1.16 GiB. The L40S retained ample headroom.
- A Qwen-VL startup warning recommends at least 1,024 image tokens for grounding
  tasks. The screenshots worked with defaults; use `--image-min-tokens 1024`
  if OCR or grounding accuracy is weak on denser notices.
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

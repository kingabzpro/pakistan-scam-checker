# Testing the Qwen Modal endpoint

The expected path is:

```text
Custom frontend
  -> queued Gradio backend
  -> OpenAI Python SDK
  -> deployed/local OpenAI-compatible endpoint
  -> unsloth/Qwen3.5-4B-MTP-GGUF
```

## Modal configuration

The app permanently defaults to the deployed experiment endpoint and model:

```text
https://abidali899--pakistan-scam-checker-qwen35-4b-q8-serve.modal.run
qwen3.5-4b-q8
```

The endpoint uses Modal proxy authentication. Set its dedicated proxy token
values as Space secrets or local environment variables:

```powershell
$env:MODAL_PROXY_KEY = "wk-..."
$env:MODAL_PROXY_SECRET = "ws-..."
```

These are not Modal CLI tokens. Do not commit secrets.

## Contract test

```powershell
python app.py --test-endpoint
```

The command sends a synthetic suspicious parcel message through the configured
endpoint and exits unsuccessfully unless the response includes:

- `risk_label`
- `simple_explanation`
- `red_flags`
- `safe_next_steps`
- `reply_draft`

For vision verification, run the experiment's existing image test:

```powershell
python experiments/modal_qwen35_4b_q8/test_request.py
```

## Troubleshooting

- **Modal credentials required:** set `MODAL_PROXY_KEY` and
  `MODAL_PROXY_SECRET` in the process that launches the app.
- **401:** use Modal Proxy Auth tokens beginning with `wk-` and `ws-`.
- **503 or timeout:** the GPU container may be cold-starting. Increase
  `MODEL_TIMEOUT_SECONDS` if needed.
- **Image is ignored:** confirm `llama-server` loaded `mmproj-F16.gguf`.
- **Invalid JSON or missing final answer:** increase
  `MODEL_REASONING_MAX_TOKENS`, or set `MODEL_ENABLE_REASONING=false` to use the
  lower-latency non-thinking path. The app reports the model failure and does
  not create a fallback assessment.
- **Local URL fails:** ensure the base URL points to the server root or `/v1`,
  not directly to `/chat/completions`.

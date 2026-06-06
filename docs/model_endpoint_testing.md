# Testing the Qwen Modal endpoint

The expected path is:

```text
Custom frontend
  -> queued Gradio backend
  -> OpenAI Python SDK
  -> deployed/local OpenAI-compatible endpoint
  -> unsloth/Qwen3.6-27B-MTP-GGUF
```

## Modal configuration

Deploy the experiment in `experiments/modal_qwen36_mtp/` first. Configure the
Space or local terminal with the resulting base URL:

```powershell
$env:MODEL_BASE_URL = "https://YOUR-WORKSPACE--pakistan-scam-checker-qwen36-mtp-serve.modal.run"
$env:MODEL_NAME = "qwen3.6-27b-mtp"
$env:MODEL_API_KEY = ""
```

The existing experiment uses Modal proxy authentication. Set its dedicated
proxy token values as Space secrets or local environment variables:

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
python experiments/modal_qwen36_mtp/test_request.py --images
```

## Troubleshooting

- **Model server not connected:** confirm both `MODEL_BASE_URL` and
  `MODEL_NAME` are set in the same process that launches the app.
- **401:** use Modal Proxy Auth tokens beginning with `wk-` and `ws-`.
- **503 or timeout:** the GPU container may be cold-starting. Increase
  `MODEL_TIMEOUT_SECONDS` if needed.
- **Image is ignored:** confirm `llama-server` loaded `mmproj-F16.gguf`.
- **Invalid JSON:** retain JSON-schema response formatting and disable model
  thinking. The app falls back to demo checks instead of exposing the failure.
- **Local URL fails:** ensure the base URL points to the server root or `/v1`,
  not directly to `/chat/completions`.

# MiniCPM-V 4.6 Q8 Modal experiment

This experiment serves the official `openbmb/MiniCPM-V-4.6-gguf` Q8 model
through a private OpenAI-compatible `llama-server` endpoint on Modal.

## Model files

- `MiniCPM-V-4_6-Q8_0.gguf`
- `mmproj-model-f16.gguf`

## Deploy

```powershell
modal run experiments/modal_minicpm_v46_q8/modal_app.py::download_model
modal deploy experiments/modal_minicpm_v46_q8/modal_app.py
```

The endpoint scales to zero after five idle minutes and requires Modal proxy
authentication.

## Evaluate

Set `MODAL_PROXY_KEY` and `MODAL_PROXY_SECRET`, then run:

```powershell
python experiments/modal_minicpm_v46_q8/test_request.py
```

The evaluator uses the production prompt and JSON schema. MiniCPM generates
each assessment, then the deployed Qwen3.6 model independently judges risk-label
correctness, evidence grounding, safety guidance, and contract validity.
Results are saved to `latest_results.json`.

## Measured result

The Qwen LLM judge passed 2 of 10 cases, with an average score of 20/100.
MiniCPM correctly handled harmless weather and courier-update inputs, but
failed phishing, abusive input, OTP theft, FBR credential theft, prize scams,
and both scam screenshots. Several failures incorrectly returned
`Looks normal`, which is release-blocking for a safety application.

This experiment was rejected. The production app later moved to the evaluated
Qwen3.5 4B Q8 endpoint.

The deployed experiment endpoint is:

```text
https://abidali899--pakistan-scam-checker-minicpm-v46-q8-serve.modal.run
```

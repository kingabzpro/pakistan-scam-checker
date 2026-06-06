# Qwen3.6 MTP model experiment notes

## Experiment

The experiment serves `unsloth/Qwen3.6-27B-MTP-GGUF` using the
`UD-Q4_K_XL` GGUF and a pinned CUDA-enabled llama.cpp build. Modal supplies one
L40S GPU and forwards a private, proxy-authenticated OpenAI-compatible endpoint.
No OpenAI API or cloud-hosted LLM API is involved.

The source model file is approximately 17.9 GB. A 24 GB GPU leaves little room
for the KV cache, CUDA allocations, and runtime overhead. The selected L40S has
48 GB VRAM, providing comfortable headroom for an 8K context and Q8 KV cache.
Memory requirements rise with context length and concurrency.

## Measured results

Status: successful L40S model load and schema-constrained smoke request.

| Measurement | Result |
| --- | --- |
| Model download | 17,909,097,600-byte GGUF cached in a Modal Volume |
| Container/image build | CUDA llama.cpp image built in about 112 seconds |
| llama-server model load | 12.03 seconds on the measured warm-volume run |
| Initial workflow | About 334 seconds including first image builds and download; exact download-only timing was not emitted |
| OpenAI SDK inference | 5.27 seconds for 59 prompt and 233 completion tokens |
| GPU/VRAM observation | L40S 46,068 MiB total; 17,909 MiB used after load |
| OpenAI response envelope | Confirmed via OpenAI Python SDK and `/v1/chat/completions` |
| Required output fields | All five fields returned as valid JSON |
| MTP initialization | Confirmed; 127/212 draft tokens accepted (59.9%) |
| Vision projector | `mmproj-F16.gguf`, 927,607,360 bytes |
| `scam_1.png` | High risk; 8.94 seconds; 1,019 prompt and 397 completion tokens |
| `scam_2.png` | High risk; 9.07 seconds; 389 prompt and 500 completion tokens |

## Output contract

The smoke test requests schema-constrained JSON with:

- `risk_label`
- `simple_explanation`
- `red_flags`
- `safe_next_steps`
- `reply_draft`

Success requires both a valid OpenAI-compatible chat completion envelope and a
validated assessment object containing exactly those fields.

Both the successful in-container request and the external test client use the
OpenAI Python SDK with a custom llama-server `base_url`. The SDK is only an
OpenAI-compatible HTTP client in this experiment: the placeholder API key is
ignored by llama-server and no request is sent to OpenAI.

## Expected startup behavior

The first setup includes three expensive operations: building llama.cpp,
downloading the approximately 17.9 GB GGUF, and loading it into GPU memory.
The GGUF is stored in a persistent Modal Volume so later cold starts avoid the
Hugging Face download, although loading weights from the Volume still takes
time. The endpoint scales to zero after five idle minutes to limit cost.

MTP is explicitly requested with:

```text
--spec-type draft-mtp --spec-draft-n-max 2
```

Successful model loading alone does not prove MTP is active. The deployment
logs must show that these arguments were accepted and that the MTP draft path
initialized without falling back or exiting.

The final SDK run logged `draft-mtp` initialization with `n_max=2`, generated
212 draft tokens, and accepted 127. An initial request left thinking enabled
and exhausted its 500-token budget without final content. Passing
`chat_template_kwargs.enable_thinking=false` produced the valid structured
response recorded above.

The deployed endpoint is intentionally left active and protected by Modal proxy
authentication. It scales to zero after five idle minutes, so the URL remains
available while idle GPU cost stops. A dashboard-created proxy token is
required for external SDK calls; the ordinary Modal CLI token was correctly
rejected with HTTP 401.

The assessment quality was useful for scam triage, but one run suggested
`pakpost.com.pk` as an official site instead of the expected government domain.
The app must not trust generated contact details or URLs; safe-next-step links
should come from curated local data or verified official sources.

## Image test

The projector-enabled server successfully processed both screenshots through
OpenAI SDK `image_url` messages while MTP remained active.

- `scam_1.png`: recognized the fake failed-delivery message and highlighted the
  suspicious link, urgency, and missing parcel details.
- `scam_2.png`: read the Roman Urdu prize message, identified the iPhone/gift
  lure and WhatsApp redirection, and extracted the visible phone numbers.

The second response reached the configured 500-token completion limit even
though llama-server reported `finish_reason=stop`. Production prompts should be
shorter or the output budget should be increased slightly. Phone numbers and
contact details extracted from screenshots must be treated as untrusted input.

## Product boundary

Modal is used only to test containerization, GPU fit, llama.cpp compatibility,
MTP, and the endpoint contract. The hackathon application should remain
local-first and usable offline. Hugging Face Spaces can provide a hosted
fallback where local hardware is insufficient; this Modal experiment should
not become an implicit production dependency.

## References

- [Unsloth Qwen3.6 guide](https://unsloth.ai/docs/models/qwen3.6)
- [Qwen3.6 27B MTP GGUF repository](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
- [llama-server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
- [Modal web servers](https://modal.com/docs/guide/webhooks)

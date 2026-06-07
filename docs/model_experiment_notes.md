# Qwen3.5 4B Q8 MTP model experiment notes

## Experiment

The production experiment serves `unsloth/Qwen3.5-4B-MTP-GGUF` with
`Qwen3.5-4B-Q8_0.gguf`, `mmproj-F16.gguf`, and a pinned CUDA-enabled
`llama.cpp` build. Modal supplies one L4 GPU and exposes a private,
proxy-authenticated OpenAI-compatible endpoint.

The server enables model-native speculative decoding:

```text
--spec-type draft-mtp --spec-draft-n-max 2
```

## Measured results

The in-container MTP smoke test generated 440 draft tokens, accepted 222, and
reported a 50.5% acceptance rate. The projector-enabled endpoint also read the
courier screenshot successfully.

The original ten-case evaluation produced:

| Measurement | Result |
| --- | --- |
| Strict passes | 9/10 |
| Average judge score | 89.5/100 |
| High-risk scam cases | All passed |
| Screenshot cases | Both passed |
| Mean case time | 9.46 seconds |
| Median case time | 6.17 seconds |

The only strict failure was a harmless appointment reminder. The model selected
the correct `Looks normal` label, but described it as irrelevant input. The
production system prompt now explicitly states that appointment reminders,
shipment updates, bills, and alerts must be assessed as notices.

Case time includes both candidate generation and the independent judge request,
so it is not a standalone inference benchmark.

After adding explicit risk-label thresholds, evidence rules, and bounded output
lengths, the same evaluation passed 10/10 cases with an average judge score of
100/100. Excluding the first cold-start case, the nine warm candidate-plus-judge
cases averaged about 8.5 seconds. The first case took about 95 seconds because
both Modal endpoints had scaled to zero.

## Output contract

The app requests and validates schema-constrained JSON containing:

- `risk_label`
- `simple_explanation`
- `red_flags`
- `safe_next_steps`
- `reply_draft`

Thinking is enabled for production requests. Text requests receive a 2,048-token
budget and image requests receive a 3,072-token budget so the model has room for
both its private `<think>` block and the final structured response. The app
discards the thinking block and validates only the final JSON. Reasoning can be
disabled with `MODEL_ENABLE_REASONING=false` if a deployment needs the earlier,
lower-latency behavior.

## Product boundary

The Modal deployment is the application's primary inference backend. It does
not produce a rule-based assessment when the endpoint fails. A local endpoint
can replace Modal through `MODEL_BASE_URL` and `MODEL_NAME`.

## References

- [Qwen3.5 4B MTP GGUF repository](https://huggingface.co/unsloth/Qwen3.5-4B-MTP-GGUF)
- [llama-server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
- [Modal web servers](https://modal.com/docs/guide/webhooks)

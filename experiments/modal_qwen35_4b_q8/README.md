# Qwen3.5 4B Q8 Modal experiment

This experiment serves `unsloth/Qwen3.5-4B-MTP-GGUF` using:

- `Qwen3.5-4B-Q8_0.gguf`
- `mmproj-F16.gguf`

The endpoint runs on a Modal L4 and is evaluated by the existing Qwen3.6 27B
endpoint acting as an independent structured LLM judge.

The server requests model-native MTP speculative decoding with:

```text
--spec-type draft-mtp --spec-draft-n-max 2
```

## MTP verification

An in-container 442-token smoke generation confirmed:

- The earlier run initialized `draft-mtp` with `n_max=2`
- 440 draft tokens generated
- 222 draft tokens accepted
- 50.5% draft acceptance
- 220 draft-generation calls

The MTP-enabled deployed endpoint also processed the courier screenshot through
`mmproj-F16.gguf` and correctly read the visible clickable delivery link.

The initial Qwen LLM-judge evaluation passed 9 of 10 cases with an average
score of 89.5/100. The only failed case was a harmless appointment reminder
that received the correct risk label but an irrelevant-input explanation.
After this evaluation, this endpoint became the production backend.

With the stricter production prompt, bounded output lengths, and deterministic
decoding, the same suite passed 10/10 with an average judge score of 100/100.
The nine warm candidate-plus-judge cases averaged about 8.5 seconds. A
scaled-to-zero cold start took about 95 seconds.

## Comparison with Qwen3.6 27B

Both models were run through the same ten cases and judged by the deployed
Qwen3.6 endpoint.

| Model | Strict passes | Average score | Mean case time | Median case time |
| --- | ---: | ---: | ---: | ---: |
| Qwen3.5 4B Q8 | 9/10 | 89.5 | 9.46 s | 6.17 s |
| Qwen3.6 27B | 8/10 | 88.0 | 9.24 s | 6.86 s |

The strict count understates Qwen3.6 quality. Its two failures had correct,
grounded, safe assessments but returned empty `red_flags` arrays, so they
failed the application contract. Qwen3.5's one failure had the correct
`Looks normal` label but incorrectly claimed that an appointment reminder was
not a notice.

Semantically, Qwen3.6 handled all ten cases correctly. Qwen3.5 handled all
high-risk scam cases and both screenshots correctly, but was weaker on the
harmless appointment reminder. The Qwen3.6 score may also be optimistic because
the same model acted as judge.

Case time includes both candidate generation and the Qwen3.6 judge request, so
it is not a standalone inference benchmark.

## Deploy

```powershell
modal run experiments/modal_qwen35_4b_q8/modal_app.py::download_model
modal deploy experiments/modal_qwen35_4b_q8/modal_app.py
python experiments/modal_qwen35_4b_q8/test_request.py
```

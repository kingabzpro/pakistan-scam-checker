---
license: cc-by-4.0
pretty_name: Pakistan Notice Helper Privacy-Safe Traces
task_categories:
  - text-classification
language:
  - en
  - ur
tags:
  - safety
  - scams
  - pakistan
  - deterministic-traces
  - privacy
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/**/*.jsonl
---

# Pakistan Notice Helper Privacy-Safe Traces

## Purpose

This dataset contains compact, deterministic metadata about Pakistan Notice
Helper scam-check requests. It does not contain hidden model reasoning or
autonomous-agent trajectories.

The application uses a Modal-hosted Qwen model for normal assessments. Creating
a trace never calls an AI model. Traces only observe the existing request path
and convert it into allow-listed categories, booleans, buckets, and counts.

## Fields

- Trace identity: random trace ID and UTC timestamp
- `input`: either `text` or a fixed-template `image (...)` description
- `input_category`: deterministic category such as courier, bank, or FBR
- `urgency`: deterministic boolean urgency signal
- Size buckets and script/language hint
- Deterministic signals: OTP, CNIC, credentials, link, payment,
  refund/prize, courier, challan, and account threat
- Modal-call metadata
- Final risk label and output item counts
- Explicit privacy flags

Records do not contain pipeline steps, cache fields, app commits, failure
details, request source, or schema-version columns.

## Privacy

The dataset never stores:

- Raw or redacted message text
- Screenshots, image bytes, or base64
- URLs, phone numbers, CNICs, names, addresses, account/card numbers, or
  tracking numbers
- Model explanations, red flags, safe-step text, reply drafts, or raw model
  output
- Exceptions, credentials, tokens, or endpoint headers

Summaries use fixed templates. Regex detection happens transiently in memory.
Users see a checked trace disclosure in the app and may opt out before each
request.

## Provenance

Seed traces represent the six public examples bundled with Pakistan Notice
Helper. Runtime traces may represent successful, rejected, or failed requests.
A trace reports whether the existing Modal request occurred, but trace
generation itself does not invoke the model.

## Limitations

- Regex signals and category detection are approximate.
- Duration and input sizes are deliberately bucketed.
- The dataset cannot reproduce original messages or screenshots.
- A risk label is safety guidance, not official verification.

## Links

- App: https://huggingface.co/spaces/build-small-hackathon/pakistan-notice-helper
- Source: https://github.com/kingabzpro/pakistan-notice-helper

## License

CC BY 4.0.

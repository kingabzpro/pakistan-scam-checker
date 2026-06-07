---
license: cc-by-4.0
pretty_name: Pakistan Notice Helper Privacy-Safe Pipeline Traces
task_categories:
  - text-classification
language:
  - en
  - ur
tags:
  - safety
  - scams
  - pakistan
  - pipeline-traces
  - privacy
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/**/*.jsonl
---

# Pakistan Notice Helper Privacy-Safe Pipeline Traces

## Purpose

This dataset shows how Pakistan Notice Helper processes scam-check requests.
It contains deterministic application-pipeline traces, not hidden model
reasoning and not autonomous-agent trajectories.

The application uses a Modal-hosted Qwen model for normal assessments. Creating
a trace never calls an AI model. Traces only observe the existing request path
and convert it into allow-listed categories, booleans, buckets, and counts.

## Pipeline

Each record follows these ordered stages:

1. `receive`
2. `validate`
3. `cache_lookup`
4. `modal_request`
5. `parse_json`
6. `normalize_result`
7. `reply_filter`
8. `response`

Stages may be completed, skipped, rejected, failed, hit, or miss.

## Fields

- Trace identity: schema version, random trace ID, UTC timestamp, app commit
- Input profile: type, size buckets, category, script/language hint
- Deterministic signals: OTP, CNIC, credentials, link, urgency, payment,
  refund/prize, courier, challan, and account threat
- Fixed-template safe summary
- Cache and Modal-call metadata
- Pipeline status and duration buckets
- Final risk label and output item counts
- Sanitized failure category and stage
- Explicit privacy flags

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
Helper. Runtime traces may represent successful, cached, rejected, or failed
requests. A trace reports whether the existing Modal request occurred, but
trace generation itself does not invoke the model.

## Limitations

- Regex signals and category detection are approximate.
- Duration and input sizes are deliberately bucketed.
- The dataset cannot reproduce original messages or screenshots.
- A risk label is safety guidance, not official verification.
- Records with `app_commit: unknown` were generated where commit metadata was
  unavailable.

## Links

- App: https://huggingface.co/spaces/build-small-hackathon/pakistan-notice-helper
- Source: https://github.com/kingabzpro/pakistan-notice-helper

## License

CC BY 4.0.

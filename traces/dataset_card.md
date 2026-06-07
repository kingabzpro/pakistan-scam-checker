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
- `input`: aggressively redacted, length-limited text for text submissions, or
  a fixed-template `image: ...` description
- `input_category`: deterministic category such as courier, bank, or FBR
- `urgency`: deterministic boolean urgency signal
- `result_summary`: deterministic summary of the mapped pattern, whether it is
  known or unclassified, and why the risk label matters
- `scam_tactics`: readable comma-separated tactics
- Flat result columns such as `risk_label` and `reply_draft_policy`

Every dataset cell is a scalar string, number, or boolean. No column contains a
dictionary or nested object, which keeps the Hugging Face table easy to read.
`trace_id` is the first serialized column, and all detected boolean signals are
combined into the single `scam_tactics` category column.

Records do not contain pipeline steps, cache fields, app commits, failure
details, request source, schema versions, size buckets, language hints, or
Modal metadata.

## Privacy

The dataset never stores:

- Raw message text
- Screenshots, image bytes, or base64
- URLs, phone numbers, CNICs, names, addresses, account/card numbers, or
  tracking numbers
- Model explanations, red flags, safe-step text, reply drafts, or raw model
  output
- Exceptions, credentials, tokens, or endpoint headers

Text traces store an aggressively redacted form capped at 500 characters.
Regexes remove common URLs, emails, phones, CNICs, card/account numbers,
credentials, addresses, tracking IDs, long numbers, and title-case names or
entities. Regex redaction cannot guarantee removal of every possible
identifier, so users should opt out when submitting sensitive content.

Images store only fixed descriptions; screenshots and OCR text are not stored.
Users see a checked trace disclosure in the app and may opt out before each
request.

## Provenance

Seed traces represent the six public examples bundled with Pakistan Notice
Helper. Runtime traces may represent successful, rejected, or failed requests.
Trace generation itself does not invoke the model.

## Limitations

- Regex signals and category detection are approximate.
- Regex redaction may miss unusual personal or confidential information.
- Novelty is not researched against external threat-intelligence sources.
- The dataset cannot reproduce original messages or screenshots.
- A risk label is safety guidance, not official verification.

## Links

- App: https://huggingface.co/spaces/build-small-hackathon/pakistan-notice-helper
- Source: https://github.com/kingabzpro/pakistan-notice-helper

## License

CC BY 4.0.

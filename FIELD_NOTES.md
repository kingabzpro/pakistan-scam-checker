# Field Notes

## Problem and scope

People in Pakistan regularly receive messages that imitate banks, couriers,
tax authorities, traffic police, utilities, and mobile operators. The difficult
part is often not reading the message but deciding what to do next without
opening an unsafe link, calling an untrusted number, or sharing an OTP.

Pakistan Notice Helper is therefore a triage tool, not an authenticity checker.
It accepts text or a screenshot and returns a risk label, a short explanation,
visible red flags, and safe next steps. The wording deliberately avoids claims
that a message is officially genuine or fraudulent.

This scope fits the **Backyard AI** track: it addresses a specific local safety
problem with a model small enough to run through `llama.cpp`.

## Why I built it this way

I wanted to build with a model I already understood instead of spending most
of the hackathon comparing unfamiliar models. I use Qwen3.6 27B locally for
coding and other everyday tasks, so I already trusted its instruction
following, output quality, and speed. That familiarity made it the practical
choice for this project: I knew how it behaved, what hardware it needed, and
where its limitations were.

The MTP variant was especially appealing because speculative multi-token
prediction can improve generation speed when the draft tokens are accepted. In
my own local workloads, quantized Qwen builds have been practical on an RTX
3090. With lighter quantizations and suitable settings, I have seen some
workloads use roughly 16 GB of VRAM and approach 150 tokens per second. Those
personal observations are not presented as a universal benchmark: context
length, quantization, GPU offload, prompt shape, and output length all change
VRAM use and tokens per second. The repository uses the larger 17.9 GB
`Q4_K_XL` file, and its reproducible measurements are the Modal L40S results
recorded below.

I chose Modal because it provides a serverless GPU endpoint that scales to zero
after inactivity and starts again on demand. That is a strong cost model for a
demo with irregular traffic because compute is paid for when the deployment is
actually used instead of keeping a GPU running continuously. Persistent
Volumes avoid downloading the 17.9 GB model on every cold start, and the
measured warm-volume load was about 12 seconds.

Control was another reason for using Modal. I build and pin the `llama.cpp`
runtime, choose the model and quantization, manage the endpoint, and protect it
with proxy authentication. Inputs are not sent to a third-party hosted LLM
API. Modal still processes the request on its infrastructure, so this is
self-managed inference rather than fully local inference, but the model-serving
stack and API behavior remain under my control.

## Product decisions

- Use simple English rather than legal or security terminology.
- Support screenshots because many suspicious messages arrive through SMS,
  WhatsApp, and social media.
- Treat every URL, phone number, and contact instruction in the submitted
  message as untrusted data.
- Never invent an assessment when inference fails. The interface shows an
  explicit error instead of falling back to rules or cached samples.
- Keep built-in examples fast with model-generated cached results, while any
  edited or new input always uses the live model.
- Show a reply draft only for uncertain cases where clarification may be safe.
  Likely scams do not encourage further engagement.

## Small-model stack

The primary model is `unsloth/Qwen3.6-27B-MTP-GGUF`, using the
`Qwen3.6-27B-UD-Q4_K_XL.gguf` quantization and `mmproj-F16.gguf` vision
projector. At 27B parameters it stays below the hackathon's 32B limit.

Modal supplies an L40S GPU and persistent model storage. A pinned,
CUDA-enabled `llama.cpp` build runs `llama-server` and exposes an
OpenAI-compatible endpoint. The OpenAI Python package is used only as an HTTP
client with a custom `base_url`; no request is sent to OpenAI.

Key measured results:

| Measurement | Result |
| --- | --- |
| Model file | 17,909,097,600 bytes |
| Vision projector | 927,607,360 bytes |
| Warm-volume model load | 12.03 seconds |
| GPU memory after load | 17,909 MiB of 46,068 MiB |
| Structured text inference | 5.27 seconds |
| Screenshot tests | 8.94 and 9.07 seconds |
| MTP draft acceptance | 127 of 212 tokens (59.9%) |

The full setup and measurements are documented in
[the model experiment notes](docs/model_experiment_notes.md).

## Building with Codex

Codex helped build most of the project, especially the custom frontend,
Gradio Server integration, tests, trace pipeline, documentation, and repeated
UI refinements. I was surprised by how quickly a fully custom HTML, CSS, and
JavaScript interface could be connected to Gradio's queue and SSE protocol.
This let me keep Hugging Face Spaces compatibility without settling for the
default Gradio component layout.

I used Codex as an engineering collaborator rather than only a code generator.
It inspected the existing repository, implemented changes, ran tests, checked
the live Space metadata, and helped keep the Modal and `llama.cpp`
documentation consistent with the deployed system. The public Git history
includes Codex co-author attribution for that work.

## Gradio and Space architecture

`gradio.Server` provides queued API routes and Hugging Face Spaces hosting
without imposing the default Gradio interface. A local HTML, CSS, and
JavaScript frontend calls the Gradio POST and SSE protocol:

```text
Browser
  -> custom mobile-first frontend
  -> queued gradio.Server endpoint
  -> OpenAI-compatible client
  -> Modal proxy-authenticated web server
  -> CUDA llama.cpp
  -> Qwen3.6 27B MTP GGUF + vision projector
```

The verified Server mode routes are `/gradio_api/call/{api_name}` and
`/gradio_api/call/{api_name}/{event_id}`. The Space README pins the Gradio
version and names `app.py` as its entry point.

## What failed and changed

- Thinking mode initially consumed the 500-token output budget without
  returning final JSON. Disabling thinking produced reliable structured
  responses.
- A dense Roman Urdu screenshot reached the original completion limit. Image
  requests now receive a larger token budget.
- One model response suggested an unverified official-looking domain. The
  system prompt now forbids invented URLs, phone numbers, organizations, and
  facts.
- Modal CLI credentials returned HTTP 401 at the web endpoint. External calls
  require dedicated Modal Proxy Auth credentials.
- Model availability cannot be hidden behind a rule-based fallback without
  making the product misleading. Failed requests therefore remain visible.

## Privacy-safe traces

The optional public trace feature is enabled in the interface but can be
disabled before each request. It records only allow-listed scalar metadata and
deterministic summaries.

Text is redacted and capped at 500 characters. Images are represented by a
fixed description and are never stored. Public traces exclude raw screenshots,
links, identifiers, generated explanations, reply text, errors, and
credentials. Upload failures do not block the user response; pending JSONL
shards remain available for retry.

I designed the trace format this way because personal information can leak
from more than the original input. A model explanation, reply draft, extracted
phone number, URL, or exception can repeat private details even when the raw
message is omitted. The trace serializer therefore does not publish the user's
input, the model's free-form reasoning, the generated reply, or the final
response text. It derives a limited set of redacted categories, booleans,
counts, and fixed summaries instead.

This minimizes what the application publishes, but it is not a claim that
model inference itself is anonymous. Live text and images still travel to the
private Modal endpoint for analysis. Users are warned not to submit sensitive
personal data, and public trace sharing can be disabled before a request.

The dataset and schema are published at
[build-small-hackathon/pakistan-notice-helper-traces](https://huggingface.co/datasets/build-small-hackathon/pakistan-notice-helper-traces).

## Pakistan safety patterns

The product focuses on patterns repeatedly present in Pakistani scam
advisories and reported examples:

- urgency, threats, suspension, arrest, disconnection, or parcel loss;
- requests for OTPs, PINs, passwords, CVVs, CNIC details, or card data;
- payment through message links, personal mobile numbers, wallets, or unusual
  channels;
- impersonation of tax, telecom, banking, traffic, customs, and courier bodies;
- prizes, refunds, jobs, rewards, or benefits requiring an advance fee.

These signals are warnings, not proof. A familiar logo, sender name, or
accurate personal detail does not establish authenticity.

## Remaining limitations

- The live Space depends on the Modal endpoint and its cold-start behavior.
- Screenshot quality and dense Roman Urdu text can affect visual recognition.
- The model can still miss subtle scams or flag legitimate notices.
- The app does not query government, bank, courier, or telecom databases.
- A result must always be confirmed through independently located official
  channels before payment or disclosure of personal information.

## Future direction

The next major feature would be an agentic verification workflow. After
understanding the submitted text or screenshot, the agent could search the web
for current scam warnings, identify the organization being impersonated, and
compare claims against independently discovered official sources. It could
then present the evidence it found alongside the model's assessment.

That workflow needs strict boundaries. It must never follow links or call
numbers supplied by the suspicious message as if they were trusted. Search
results would need source ranking, domain verification, citations, and a clear
distinction between evidence and inference. The current project stops at
triage because adding web access without those controls could make a safety
tool less safe.

## References

- [Build Small Hackathon](https://huggingface.co/build-small-hackathon)
- [Gradio Server mode](https://www.gradio.app/main/guides/server-mode)
- [Gradio curl and SSE protocol](https://www.gradio.app/main/guides/querying-gradio-apps-with-curl)
- [Hugging Face Spaces configuration](https://huggingface.co/docs/hub/spaces-config-reference)
- [Qwen3.6 27B MTP GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
- [llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)
- [Modal web servers](https://modal.com/docs/guide/webhooks)
- [FBR fraudulent SMS warning](https://www.fbr.gov.pk/beware-fradulant-sms/152600)
- [PTA Complaint Management System](https://complaint.pta.gov.pk/RegisterComplaint.aspx)
- [State Bank of Pakistan](https://www.sbp.org.pk/)
- [FIA complaint portal](https://complaint.fia.gov.pk/)

Research and deployment results were reviewed on June 7, 2026.

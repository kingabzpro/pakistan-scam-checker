# Field notes

## Architecture findings

- Gradio 6 Server mode provides a FastAPI-compatible `Server`, queued
  `@app.api` endpoints, SSE results, and `launch()`. This enables a custom
  frontend without rendering a default Gradio interface.
- Gradio's documented protocol posts `{"data": [...]}` and then reads an SSE
  result using the returned event ID. In Server mode the verified routes are
  `/gradio_api/call/{api_name}` and
  `/gradio_api/call/{api_name}/{event_id}`.
- Hugging Face Gradio Spaces launch the file named by `app_file` and honor
  `sdk_version` from README metadata.
- The OpenAI Python SDK accepts a custom `base_url`, so it can call llama.cpp
  and Modal-hosted OpenAI-compatible endpoints without using OpenAI cloud.
- The experimental Qwen deployment includes `mmproj-F16.gguf`; image analysis
  depends on that projector. This application intentionally adds no OCR.

## Pakistan safety patterns

Local checks focus on signals repeatedly present in Pakistani scam advisories
and reported examples:

- urgency, threats, account suspension, arrest, disconnection, or parcel loss;
- requests for OTPs, PINs, passwords, CVVs, CNIC details, or card data;
- payment through message links, personal mobile numbers, wallets, or unusual
  channels;
- impersonation of tax, telecom, banking, traffic, customs, and courier bodies;
- prizes, refunds, rewards, jobs, or benefits requiring an advance fee.

Signals are not proof. A familiar logo, sender name, or accurate personal detail
also does not prove authenticity.

## Official references

- [Gradio Server mode](https://www.gradio.app/main/guides/server-mode)
- [Gradio curl and SSE protocol](https://www.gradio.app/main/guides/querying-gradio-apps-with-curl)
- [Hugging Face Spaces configuration](https://huggingface.co/docs/hub/spaces-config-reference)
- [Unsloth Qwen3.6 model](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
- [FBR fraudulent SMS warning](https://www.fbr.gov.pk/beware-fradulant-sms/152600)
- [PTA Complaint Management System](https://complaint.pta.gov.pk/RegisterComplaint.aspx)
- [State Bank of Pakistan](https://www.sbp.org.pk/)
- [FIA complaint portal](https://complaint.fia.gov.pk/)

Research was reviewed on June 6, 2026.

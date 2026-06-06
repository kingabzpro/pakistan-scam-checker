# Pakistan Notice Helper

A local-first AI app that helps people in Pakistan identify suspicious messages, scam emails, fake notices, and phishing attempts. Accepts both **images** (screenshots) and **text** (pasted messages or emails).

## Problem

Millions of Pakistanis receive confusing or fraudulent messages daily:

**SMS & WhatsApp Scams**
- Fake FBR tax refund SMS
- Counterfeit e-challan traffic fines
- Phishing courier delivery notifications (Pakistan Post, TCS, Leopards)
- Bank fraud alerts and fake reward points
- Easypaisa / JazzCash wallet scams
- WhatsApp account hijacking attempts

**Email Scams**
- Fake FBR tax assessment emails with malicious attachments
- Bank phishing emails asking to "verify account"
- Prize/lottery winner notification emails
- Job offer emails requesting upfront fees
- Fake university admission or scholarship emails
- Customs/duty payment emails with phishing links

**Text-Based Fraud**
- Job scams via WhatsApp/Telegram (task-based scams)
- Romance and investment scams on social media
- Fake customer support messages
- SIM swap and OTP phishing attempts

Most people cannot tell real from fake. This tool helps them decide.

## How It Works

```
User pastes text / uploads screenshot / forwards email
        |
        v
   Small multimodal model (local, no cloud)
        |
        v
   Returns:
   - Risk label (Likely scam / Verify first / Looks normal)
   - Red flags found
   - Simple explanation in English + Urdu
   - Safe next steps
   - Draft reply
```

### Supported Input Types

| Input Type | Examples |
|---|---|
| **Image** | SMS screenshots, email screenshots, WhatsApp screenshots, fake website screenshots |
| **Text** | Pasted SMS text, email body, WhatsApp message, job offer, any suspicious message |

## Project Structure

```
pakistan-scam-checker/
├── data/
│   └── examples.jsonl          # Labeled scam examples (images + text)
├── sample_inputs/              # Real scam message screenshots (public sources)
├── docs/
│   ├── research_notes.md       # Scam pattern research & official advisories
│   └── model_experiment_notes.md
├── experiments/
│   └── modal_qwen36_mtp/      # Qwen3.6 MTP model experiments on Modal
└── README.md
```

## Dataset

`data/examples.jsonl` contains labeled examples sourced from public posts on Reddit, PTA advisories, security research reports, and user-reported scams.

Each entry includes:
| Field | Description |
|---|---|
| `image` | Path to screenshot in `sample_inputs/` (for image examples) |
| `text` | Raw message text (for text examples) |
| `input_type` | `image` or `text` |
| `category` | FBR, bank, wallet, courier, traffic_challan, email, job, unknown |
| `risk_label` | Likely scam / Suspicious / Verify first / Looks normal |
| `source_type` | reddit / official_advisory / synthetic / other |
| `source_url` | Public URL where the example was found |
| `description` | What the message or screenshot shows |
| `red_flags` | Array of warning signs |
| `simple_explanation` | Plain language explanation of the scam |
| `safe_next_steps` | What the user should do |
| `reply_draft` | Suggested reply if needed |

### Categories Covered

| Category | Input Types | Examples |
|---|---|---|
| Courier scams | image, text | Fake Pakistan Post, TCS delivery SMS |
| E-Challan scams | image, text | Fake traffic fine from non-9915 numbers |
| Bank scams | image, text | HBL/UBL fraud alerts, smishing |
| FBR tax scams | image, text | Fake tax refund messages and emails |
| Email phishing | text | Fake bank emails, prize notifications |
| Job scams | text | WhatsApp/Telegram task scams, fake offers |
| Wallet scams | text | Easypaisa / JazzCash fraud |
| WhatsApp scams | image, text | Verification code hijacking |
| Utility scams | text | K-Electric, SNGC disconnection threats |
| University scams | text | Fake HEC scholarship announcements |

## Getting Started

```bash
git clone https://github.com/kingabzpro/pakistan-scam-checker.git
cd pakistan-scam-checker
```

### Prerequisites

- Python 3.10+
- llama.cpp (for local model inference)
- A multimodal GGUF model (e.g., Qwen3.6-27B-MTP)

### Quick Test

```python
import json

with open("data/examples.jsonl") as f:
    for line in f:
        example = json.loads(line)
        input_type = example.get("input_type", "image")
        label = example["risk_label"]
        cat = example["category"]
        desc = example.get("description", example.get("text", ""))[:80]
        print(f"[{input_type}] [{label}] {cat}: {desc}...")
```

## Model Experiments

See `docs/model_experiment_notes.md` for details on running Qwen3.6-27B-MTP on Modal with an L40S GPU.

Key findings:
- Model loads in ~12 seconds on L40S (48GB VRAM)
- Inference in ~5 seconds for structured JSON output
- MTP draft token acceptance: ~60%
- Vision projector included for image understanding
- Text-only inputs are faster (no image processing)

## Official Reporting Channels

If you receive a suspicious message in Pakistan:

| Organization | Contact | For |
|---|---|---|
| PTA (Telecom) | complaints.pta.gov.pk | SMS/WhatsApp scams |
| FIA Cyber Crime | Helpline 1991 | Online fraud, phishing |
| SBP (Banking) | 021-111-727-727 | Bank fraud |
| FBR (Tax) | fbr.gov.pk | Tax-related scams |
| National CERT | pkcert.gov.pk | Cybersecurity incidents |
| HEC | hec.gov.pk | Fake education scams |

## Contributing

This is a hackathon project. Contributions welcome:

1. Add more scam examples (screenshots or text) to `data/examples.jsonl`
2. Add corresponding screenshots to `sample_inputs/`
3. Improve model prompts and detection accuracy
4. Add Urdu language support
5. Add more email scam examples

**Important:** Do not upload private personal data. All examples must be from public sources or anonymized recreations.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Acknowledgments

- PTA, FIA, FBR, PSCA for public scam advisories
- Reddit r/pakistan and r/PakistaniTech communities
- NCERT Pakistan for cybersecurity advisories
- Security researchers at Resecurity and Group-IB

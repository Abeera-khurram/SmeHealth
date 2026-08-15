# SmeHealth — AI-Powered Healthcare Workflow Automation

Agentic AI prototype for small-to-medium healthcare facilities, built to automate two
high-friction manual workflows: **sonography reporting** and **pre-operative clinical
safety checks**. Built entirely on free, open-weight tools — no paid APIs required.

> ⚠️ **Prototype / research project.** Every output is explicitly labeled
> `requires_physician_approval: true`. Nothing here diagnoses, prescribes, or clears a
> patient on its own — it drafts and flags for a licensed clinician to review. Not
> intended for real clinical use without full validation, regulatory review, and
> integration with certified data sources.

---

## What it does

### 1. Sonography Reporting Automation (`sonography_reporting/`)

Replaces the manual dictate-then-type workflow radiologists use after a scan.

```
machine screenshot ──▶ screenshot_reader.py   (Groq vision LLM reads on-screen measurements)
radiologist voice   ──▶ transcribe.py          (local faster-whisper, fully offline)
                              │
                              ▼
                    report_generator.py
              merges both inputs into one structured report
```

- **`model_selection.py`** — a lightweight evaluation harness that runs the same
  screenshot + voice input through multiple free Groq models (Llama 3.3 70B, Llama 3.1
  8B, Gemma2 9B) and scores each output against a human-written reference report, so the
  best-performing model can be selected on real data.
- Accepts any `.png` screenshot and `.wav` voice annotation.

### 2. Agentic Pre-Op Safety Layer (`agentic_layer/`)

An autonomous LangGraph workflow that reasons over a patient record before surgery and
produces a single **physician review packet** — it never approves anything itself.

```
ehr_mock.py  (synthetic EHR, built to mirror a real FHIR-style schema)
       │
       ├──▶ dosage_agent.py       age/weight/renal-function-based dosing suggestion,
       │                          cross-checked against a renal-dosing reference table
       │
       ├──▶ process_guardian.py   audits anticoagulation pause timing and pre-op
       │                          hemoglobin/potassium against safe ranges
       │
       └──▶ timeline_sync.py      real-time OR/equipment resource log, detects
                                   allocation conflicts
                │
                ▼
        orchestrator.py (LangGraph) ──▶ one physician review packet
```

Every packet includes `final_approval_required_from: "attending physician"` — the agent
suggests and flags, a clinician decides.

---

## Tech stack

| Component | Tool | Why |
|---|---|---|
| LLM reasoning + vision | [Groq](https://groq.com) (free tier, open-weight models) | No cost, fast inference |
| Speech-to-text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Runs fully local/offline, no audio leaves the machine |
| Agent orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) | Explicit, auditable multi-step workflow graph |
| Drug reference | Static renal-dosing table (illustrative) | Placeholder for a future [openFDA](https://open.fda.gov/) integration |

---

## Getting started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com/keys)

### Setup

```bash
git clone https://github.com/Abeera-khurram/SmeHealth.git
cd SmeHealth
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your GROQ_API_KEY
```

### Run the agentic pre-op demo (no files needed)

```bash
python demo_agentic_layer.py
```

This generates a synthetic patient record on the fly and prints a full physician review
packet as JSON.

### Run the sonography reporting pipeline

Requires a real sonography machine screenshot (`.png`) and a voice annotation (`.wav`):

```bash
python -c "
from sonography_reporting.report_generator import generate_report
import json
print(json.dumps(generate_report('screenshot.png', 'annotation.wav'), indent=2))
"
```

### Run the web dashboard

A small FastAPI layer (`api.py`) exposes both workflows over HTTP and serves the
dashboard in `frontend/`.

```bash
uvicorn api:app --reload
```

Then open **http://127.0.0.1:8000** in a browser. The dashboard has two tabs:

- **Pre-Op Safety Check** — enter a patient ID and drug name, get back a full
  physician review packet (dosage suggestion, risk flags, surgical readiness, resource
  conflicts).
- **Sonography Report** — upload a machine screenshot and a voice annotation, get back
  a structured report.

Every result panel shows a **CLEAR / FLAGGED** status pill and states who final approval
is required from — the dashboard never lets a result look "approved."

API docs (interactive, auto-generated) are available at `http://127.0.0.1:8000/docs`.

---

## Example output

```json
{
  "patient_id": "PT-1042",
  "dosage_suggestion": "Reduce enoxaparin dose to 50% of standard due to renal impairment",
  "dosage_risk_flags": [
    "Increased risk of bleeding with reduced renal clearance"
  ],
  "surgery_clear": false,
  "surgery_flags": [
    "Hemoglobin 8.8 g/dL is outside safe range (10.0-17.0)."
  ],
  "resource_conflicts": [],
  "final_approval_required_from": "attending physician"
}
```

---

## Project structure

```
smehealth/
├── agentic_layer/
│   ├── dosage_agent.py       # renal-adjusted dosing suggestions
│   ├── drug_reference.py     # local renal-dosing reference table
│   ├── ehr_mock.py           # synthetic EHR data generator
│   ├── orchestrator.py       # LangGraph workflow tying agents together
│   ├── process_guardian.py   # pre-op safety audit
│   └── timeline_sync.py      # resource allocation / conflict log
├── sonography_reporting/
│   ├── model_selection.py    # multi-model evaluation harness
│   ├── report_generator.py   # merges screenshot + voice into a report
│   ├── screenshot_reader.py  # Groq vision screenshot reader
│   └── transcribe.py         # local Whisper transcription
├── frontend/
│   └── index.html             # web dashboard (pre-op + sonography console)
├── api.py                     # FastAPI layer wrapping both workflows for the dashboard
├── llm_client.py              # shared Groq client (text + vision)
├── demo_agentic_layer.py      # zero-file demo entry point
├── requirements.txt
└── .env.example
```

---

## Known limitations

- No real hospital data was available for this prototype. `sonography_reporting/` needs
  real screenshot/audio pairs to properly evaluate; `agentic_layer/` uses a synthetic EHR
  generator built to mirror a realistic schema so it can be swapped for a real EHR/FHIR
  feed later.
- The drug reference table is a small illustrative subset, not a full clinical database —
  production use would call the free [openFDA](https://open.fda.gov/) API.
- This is a backend/agent logic layer only; no UI is included yet.

## License

Not yet licensed — add a LICENSE file before accepting external contributions or public
reuse.

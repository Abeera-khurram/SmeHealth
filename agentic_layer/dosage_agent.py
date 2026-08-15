"""
Dosage Reasoning Agent
------------------------
Autonomous reasoning layer: pulls real-time EHR data (age, weight, renal
function), looks up renal-adjusted dosing, and produces a personalized
regimen suggestion for FINAL PHYSICIAN APPROVAL (never auto-administered -
the description is explicit that AI suggests, physician approves).
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import call_llm_json
from agentic_layer.ehr_mock import get_patient_record
from agentic_layer.drug_reference import lookup_renal_dosing

DOSAGE_SYSTEM_PROMPT = """You are a clinical dosing assistant. Given a patient's demographic and
renal function data plus a renal-dosing reference lookup, produce a personalized dosage
recommendation. This is a SUGGESTION for physician review only - always state this explicitly.

Respond ONLY in JSON:
{
  "recommended_action": "<dose recommendation in plain clinical language>",
  "rationale": "<why, referencing the specific age/weight/renal values>",
  "risk_flags": ["any safety concern, or empty list"],
  "requires_physician_approval": true
}
"""


def suggest_dosage(patient_id: str, drug_name: str) -> dict:
    patient = get_patient_record(patient_id)
    egfr = patient["renal_function"]["egfr"]
    reference = lookup_renal_dosing(drug_name, egfr)

    prompt = (
        f"Patient: age {patient['age']}, weight {patient['weight_kg']}kg, "
        f"eGFR {egfr} mL/min/1.73m2, creatinine {patient['renal_function']['creatinine_mg_dl']} mg/dL.\n"
        f"Drug: {drug_name}\n"
        f"Renal dosing reference lookup: {reference}"
    )
    result = call_llm_json(DOSAGE_SYSTEM_PROMPT, prompt)
    result["_patient_snapshot"] = patient
    result["_reference_lookup"] = reference
    return result

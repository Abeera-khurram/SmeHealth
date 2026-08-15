"""
Surgical Process Guardian
----------------------------
Autonomously audits a patient record BEFORE surgery to verify:
  1. Anticoagulation therapy was paused for a clinically safe interval
  2. Pre-operative hemoglobin and potassium fall within safe ranges
Flags discrepancies for physician review rather than blocking the surgery
outright - matches the description's "flagging discrepancies... for final
physician approval."
"""
import sys, os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentic_layer.ehr_mock import get_patient_record

# Simplified safe-range reference (illustrative, not clinical guidance)
SAFE_RANGES = {
    "hemoglobin_g_dl": (10.0, 17.0),
    "potassium_mmol_l": (3.5, 5.0),
}
MIN_ANTICOAG_PAUSE_HOURS = {
    "Warfarin": 48,
}


def audit_surgical_readiness(patient_id: str) -> dict:
    patient = get_patient_record(patient_id)

    surgery_time = datetime.fromisoformat(patient["surgery_scheduled_time"])
    last_dose_time = datetime.fromisoformat(patient["anticoagulation"]["last_dose_time"])
    pause_hours = (surgery_time - last_dose_time).total_seconds() / 3600
    drug = patient["anticoagulation"]["drug"]
    required_pause = MIN_ANTICOAG_PAUSE_HOURS.get(drug, 24)

    hb = patient["preop_labs"]["hemoglobin_g_dl"]
    k = patient["preop_labs"]["potassium_mmol_l"]
    hb_lo, hb_hi = SAFE_RANGES["hemoglobin_g_dl"]
    k_lo, k_hi = SAFE_RANGES["potassium_mmol_l"]

    flags = []
    if pause_hours < required_pause:
        flags.append(
            f"Anticoagulation ({drug}) paused only {pause_hours:.1f}h before surgery; "
            f"minimum required is {required_pause}h."
        )
    if not (hb_lo <= hb <= hb_hi):
        flags.append(f"Hemoglobin {hb} g/dL is outside safe range ({hb_lo}-{hb_hi}).")
    if not (k_lo <= k <= k_hi):
        flags.append(f"Potassium {k} mmol/L is outside safe range ({k_lo}-{k_hi}).")

    return {
        "patient_id": patient_id,
        "anticoag_pause_hours": round(pause_hours, 1),
        "hemoglobin_g_dl": hb,
        "potassium_mmol_l": k,
        "clear_for_surgery": len(flags) == 0,
        "flags": flags,
        "requires_physician_approval": True,
        "_patient_snapshot": patient,
    }

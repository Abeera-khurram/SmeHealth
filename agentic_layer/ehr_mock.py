"""
Synthetic EHR Simulator
-------------------------
Real hospital EHR data is not available for this prototype, so this module
simulates the fields the agentic layer needs to pull: age, weight, renal
function (eGFR/creatinine), anticoagulation therapy timing, and
pre-operative labs (hemoglobin, potassium). Built to mirror a realistic EHR
schema so it can be swapped for a real EHR API/FHIR feed later.
"""
import random
from datetime import datetime, timedelta


def get_patient_record(patient_id: str) -> dict:
    """Simulates pulling a patient's real-time EHR data."""
    random.seed(hash(patient_id) % (2**32))
    surgery_time = datetime.now() + timedelta(hours=6)
    anticoag_last_dose = surgery_time - timedelta(hours=random.choice([12, 24, 36, 48, 72]))

    return {
        "patient_id": patient_id,
        "age": random.randint(35, 85),
        "weight_kg": round(random.uniform(50, 100), 1),
        "renal_function": {
            "egfr": round(random.uniform(15, 110), 1),  # mL/min/1.73m2
            "creatinine_mg_dl": round(random.uniform(0.6, 3.5), 2),
        },
        "anticoagulation": {
            "drug": "Warfarin",
            "last_dose_time": anticoag_last_dose.isoformat(),
        },
        "surgery_scheduled_time": surgery_time.isoformat(),
        "preop_labs": {
            "hemoglobin_g_dl": round(random.uniform(8.5, 15.5), 1),
            "potassium_mmol_l": round(random.uniform(3.0, 5.8), 2),
        },
    }

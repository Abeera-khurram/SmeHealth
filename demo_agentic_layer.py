"""
Quick demo of Subproject 2 (Agentic Layer) - runs without needing any
screenshot/audio files, since it uses the synthetic EHR simulator.

Run: python demo_agentic_layer.py
"""
import json
from agentic_layer.orchestrator import run_preop_workflow

if __name__ == "__main__":
    result = run_preop_workflow(patient_id="PT-1042", drug_name="enoxaparin")
    print(json.dumps(result["physician_packet"], indent=2))

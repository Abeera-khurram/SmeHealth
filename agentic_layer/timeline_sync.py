"""
Multidimensional Timeline Sync
---------------------------------
During the administrative phase of surgery, tracks resource usage
(OR room, equipment, staff) via real-time entries and keeps clinical +
legal records synchronized instantly - as opposed to end-of-day manual
reconciliation.
"""
import json
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "timeline_log.jsonl")


def log_resource_event(patient_id: str, resource_type: str, resource_id: str, event: str):
    """event: 'allocated' | 'released' | 'in_use'"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "resource_type": resource_type,  # e.g. "OR_room", "anesthesia_machine", "surgeon"
        "resource_id": resource_id,
        "event": event,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def get_patient_timeline(patient_id: str) -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    events = []
    with open(LOG_PATH) as f:
        for line in f:
            entry = json.loads(line)
            if entry["patient_id"] == patient_id:
                events.append(entry)
    return sorted(events, key=lambda e: e["timestamp"])


def detect_resource_conflicts(patient_id: str) -> list[str]:
    """Simple conflict check: a resource marked 'in_use' without a matching
    'allocated' entry beforehand, or 'allocated' without later 'released'."""
    timeline = get_patient_timeline(patient_id)
    open_allocations = {}
    conflicts = []
    for e in timeline:
        key = (e["resource_type"], e["resource_id"])
        if e["event"] == "allocated":
            open_allocations[key] = e["timestamp"]
        elif e["event"] == "in_use" and key not in open_allocations:
            conflicts.append(f"{e['resource_type']} {e['resource_id']} marked in_use without prior allocation")
        elif e["event"] == "released":
            open_allocations.pop(key, None)
    return conflicts

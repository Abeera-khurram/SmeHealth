"""
Drug Reference Table (illustrative subset)
---------------------------------------------
Description mentions "browsing national health databases like the FDA's
Orange Book." Orange Book itself lists approved drug products, not renal
dosing tables - the actual renal-adjustment data typically comes from
prescribing information / FDA label data. For this free prototype we use a
small, illustrative static reference table (public prescribing-info style
renal dosing bands) instead of a paid clinical database. In production this
module would call the free FDA openFDA API (api.fda.gov, no key required
for low volume) to pull real drug label data.
"""

# Illustrative renal dosing adjustment bands (simplified, NOT clinical advice)
RENAL_DOSING_TABLE = {
    "metformin": [
        {"egfr_min": 45, "egfr_max": 999, "dose_pct": 100, "note": "Normal dose"},
        {"egfr_min": 30, "egfr_max": 44, "dose_pct": 50, "note": "Reduce dose by half"},
        {"egfr_min": 0, "egfr_max": 29, "dose_pct": 0, "note": "Contraindicated"},
    ],
    "enoxaparin": [
        {"egfr_min": 30, "egfr_max": 999, "dose_pct": 100, "note": "Normal dose"},
        {"egfr_min": 0, "egfr_max": 29, "dose_pct": 50, "note": "Reduce dose, renal impairment"},
    ],
    "gabapentin": [
        {"egfr_min": 60, "egfr_max": 999, "dose_pct": 100, "note": "Normal dose"},
        {"egfr_min": 30, "egfr_max": 59, "dose_pct": 66, "note": "Reduce dose"},
        {"egfr_min": 0, "egfr_max": 29, "dose_pct": 33, "note": "Significant reduction required"},
    ],
}


def lookup_renal_dosing(drug_name: str, egfr: float) -> dict:
    drug_name = drug_name.lower()
    table = RENAL_DOSING_TABLE.get(drug_name)
    if not table:
        return {"found": False, "note": f"No local reference entry for '{drug_name}' - would query openFDA API in production."}
    for band in table:
        if band["egfr_min"] <= egfr <= band["egfr_max"]:
            return {"found": True, "drug": drug_name, "egfr": egfr, **band}
    return {"found": False, "note": "eGFR out of known bands"}

"""
Agentic Layer Orchestrator (LangGraph)
------------------------------------------
Ties dosage reasoning + surgical process guardian + timeline sync into one
autonomous pre-operative workflow, ending in a single "physician review
packet" - the AI never approves anything itself, it only flags and
suggests, per the description.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, END

from agentic_layer.dosage_agent import suggest_dosage
from agentic_layer.process_guardian import audit_surgical_readiness
from agentic_layer.timeline_sync import log_resource_event, detect_resource_conflicts


class PreOpState(TypedDict, total=False):
    patient_id: str
    drug_name: str
    dosage_suggestion: dict
    readiness_audit: dict
    resource_conflicts: list
    physician_packet: dict


def node_dosage(state: PreOpState) -> PreOpState:
    state["dosage_suggestion"] = suggest_dosage(state["patient_id"], state["drug_name"])
    return state


def node_readiness(state: PreOpState) -> PreOpState:
    state["readiness_audit"] = audit_surgical_readiness(state["patient_id"])
    return state


def node_timeline(state: PreOpState) -> PreOpState:
    # Example real-time resource entries for this pre-op workflow
    log_resource_event(state["patient_id"], "OR_room", "OR-3", "allocated")
    log_resource_event(state["patient_id"], "anesthesia_machine", "AM-2", "allocated")
    state["resource_conflicts"] = detect_resource_conflicts(state["patient_id"])
    return state


def node_build_packet(state: PreOpState) -> PreOpState:
    """Final packet a physician reviews and approves/rejects in one glance."""
    state["physician_packet"] = {
        "patient_id": state["patient_id"],
        "dosage_suggestion": state["dosage_suggestion"].get("recommended_action"),
        "dosage_risk_flags": state["dosage_suggestion"].get("risk_flags", []),
        "surgery_clear": state["readiness_audit"]["clear_for_surgery"],
        "surgery_flags": state["readiness_audit"]["flags"],
        "resource_conflicts": state["resource_conflicts"],
        "final_approval_required_from": "attending physician",
    }
    return state


def build_graph():
    graph = StateGraph(PreOpState)
    graph.add_node("dosage", node_dosage)
    graph.add_node("readiness", node_readiness)
    graph.add_node("timeline", node_timeline)
    graph.add_node("build_packet", node_build_packet)

    graph.set_entry_point("dosage")
    graph.add_edge("dosage", "readiness")
    graph.add_edge("readiness", "timeline")
    graph.add_edge("timeline", "build_packet")
    graph.add_edge("build_packet", END)
    return graph.compile()


def run_preop_workflow(patient_id: str, drug_name: str) -> PreOpState:
    app = build_graph()
    return app.invoke({"patient_id": patient_id, "drug_name": drug_name})

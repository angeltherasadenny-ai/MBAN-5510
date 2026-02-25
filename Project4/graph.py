# graph.py
# Builds the LangGraph stateful workflow.
# Wires all nodes together with routing logic.
#
# Flow:
#   intake
#     ├─(flagged)──────────────► escalate → END
#     └─(clean)──► classify
#                    ├─(EMERGENCY)──► escalate → END
#                    ├─(UNCLEAR)────► needs_info → END
#                    └─(normal)─────► draft → END
#
# HITL is NOT a graph node — the Streamlit UI handles it
# between the draft output and the final response.

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from nodes import (
    intake_node,
    classify_node,
    draft_response_node,
    escalate_node,
    needs_info_node,
)


# ── State schema ──────────────────────────────────────────────────
# Shared memory that flows through every node.
class AppointmentState(TypedDict):
    patient_message:    str
    run_id:             Optional[str]
    timestamp:          Optional[str]
    sanitized_message:  Optional[str]
    moderation_flagged: Optional[bool]
    moderation_cats:    Optional[List[str]]
    intent:             Optional[str]
    draft_response:     Optional[str]
    final_response:     Optional[str]
    review_action:      Optional[str]
    status:             Optional[str]
    escalation_reason:  Optional[str]
    path_taken:         Optional[List[str]]


# ── Routing functions ─────────────────────────────────────────────
def route_after_intake(state: dict) -> str:
    if state.get("moderation_flagged"):
        print("[Router] Moderation flagged → ESCALATE")
        return "escalate"
    return "classify"


def route_after_classify(state: dict) -> str:
    intent = state.get("intent", "UNCLEAR")
    if intent == "EMERGENCY":
        print("[Router] Emergency → ESCALATE")
        return "escalate"
    elif intent == "UNCLEAR":
        print("[Router] Unclear → NEEDS_INFO")
        return "needs_info"
    else:
        print(f"[Router] {intent} → DRAFT")
        return "draft"


# ── Build graph ───────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AppointmentState)

    graph.add_node("intake",     intake_node)
    graph.add_node("classify",   classify_node)
    graph.add_node("draft",      draft_response_node)
    graph.add_node("escalate",   escalate_node)
    graph.add_node("needs_info", needs_info_node)

    graph.set_entry_point("intake")

    graph.add_conditional_edges(
        "intake",
        route_after_intake,
        {"escalate": "escalate", "classify": "classify"}
    )

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"escalate": "escalate", "needs_info": "needs_info", "draft": "draft"}
    )

    # draft goes to END — Streamlit handles HITL externally
    graph.add_edge("draft",      END)
    graph.add_edge("escalate",   END)
    graph.add_edge("needs_info", END)

    return graph.compile()


appointment_graph = build_graph()

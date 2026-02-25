# main.py
# CLI entry point — run this to use the system without the web UI.
# Usage: python main.py

from graph import appointment_graph


def print_summary(state: dict):
    print("\n" + "=" * 60)
    print("  EXECUTION SUMMARY")
    print("=" * 60)
    print(f"  Run ID         : {state.get('run_id', 'N/A')}")
    print(f"  Timestamp      : {state.get('timestamp', 'N/A')}")
    print(f"  Intent         : {state.get('intent', 'N/A')}")
    print(f"  Terminal Status: {state.get('status', 'N/A')}")
    print(f"  Review Action  : {state.get('review_action', 'N/A')}")
    print(f"  Path Taken     : {' -> '.join(state.get('path_taken', []))}")
    if state.get("escalation_reason"):
        print(f"  Escalation     : {state.get('escalation_reason')}")
    print("\n  FINAL PATIENT-FACING RESPONSE:")
    print("-" * 60)
    print(f"  {state.get('final_response', 'No response generated.')}")
    print("=" * 60 + "\n")


def main():
    print("\n" + "=" * 60)
    print("  MBAN 5510 — Appointment Assistant (CLI)")
    print("=" * 60)
    print("\nEnter the patient's message:\n")
    patient_message = input("Patient: ").strip()

    if not patient_message:
        print("No message entered. Exiting.")
        return

    initial_state = {
        "patient_message":    patient_message,
        "run_id":             None,
        "timestamp":          None,
        "sanitized_message":  None,
        "moderation_flagged": None,
        "moderation_cats":    None,
        "intent":             None,
        "draft_response":     None,
        "final_response":     None,
        "review_action":      None,
        "status":             None,
        "escalation_reason":  None,
        "path_taken":         [],
    }

    print("\n[System] Processing...\n")
    result = appointment_graph.invoke(initial_state)

    # ── HITL for CLI ──────────────────────────────────────────────
    if result.get("draft_response") and not result.get("final_response"):
        print("\n" + "=" * 60)
        print("  HUMAN REVIEW REQUIRED — HITL CHECKPOINT")
        print("=" * 60)
        print(f"\n  Draft:\n\n  {result['draft_response']}\n")
        print("  [A] Approve    [E] Edit    [R] Reject")

        while True:
            choice = input("\n  Your choice: ").strip().upper()
            if choice == "A":
                result["final_response"] = result["draft_response"]
                result["review_action"]  = "APPROVED"
                result["status"]         = "READY"
                result["path_taken"].append("human_review")
                break
            elif choice == "E":
                edited = input("  Enter edited response: ").strip()
                result["final_response"] = edited
                result["review_action"]  = "EDITED"
                result["status"]         = "READY"
                result["path_taken"].append("human_review")
                break
            elif choice == "R":
                result["final_response"] = "Your request has been noted. A staff member will follow up with you shortly."
                result["review_action"]  = "REJECTED"
                result["status"]         = "READY"
                result["path_taken"].append("human_review")
                break
            else:
                print("  Please enter A, E, or R.")

    print_summary(result)


if __name__ == "__main__":
    main()

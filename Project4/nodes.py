# nodes.py
# Each function is one step (node) in the LangGraph workflow.
# Nodes receive the shared state dict and return updates to it.

import os
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from middleware import PIIMiddleware, OpenAIModerationMiddleware, ModelRetryMiddleware, get_fresh_limiter
from dotenv import load_dotenv

load_dotenv()

# ── Shared middleware instances ───────────────────────────────────
pii_middleware        = PIIMiddleware()
moderation_middleware = OpenAIModerationMiddleware()
retry_middleware      = ModelRetryMiddleware(max_retries=2, wait_seconds=1)

# ── LLM setup ────────────────────────────────────────────────────
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=300,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


# ── NODE 1: intake ────────────────────────────────────────────────
# First node — masks PII and runs moderation on the patient message.
# Assigns a unique run ID and timestamp for every run.
def intake_node(state: dict) -> dict:
    print("\n[Node: intake] Running PII masking and moderation check...")

    raw_message = state["patient_message"]
    sanitized   = pii_middleware.run(raw_message)
    mod_result  = moderation_middleware.run(sanitized)
    run_id      = str(uuid.uuid4())[:8].upper()
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[Node: intake] Run ID: {run_id} | Flagged: {mod_result['flagged']}")

    return {
        "run_id":             run_id,
        "timestamp":          timestamp,
        "sanitized_message":  sanitized,
        "moderation_flagged": mod_result["flagged"],
        "moderation_cats":    mod_result["categories"],
        "path_taken":         ["intake"],
    }


# ── NODE 2: classify ──────────────────────────────────────────────
# Uses GPT-4o-mini to classify intent into one of 5 categories.
# A fresh limiter is created each call — no carry-over between runs.
def classify_node(state: dict) -> dict:
    print("\n[Node: classify] Classifying patient intent...")

    limiter = get_fresh_limiter()
    limiter.check()

    system_prompt = """You are a medical appointment triage assistant.
Classify the patient message into EXACTLY one of these labels:
  RESCHEDULE        - patient wants to change appointment date/time
  CANCEL            - patient wants to cancel their appointment
  PREP_INSTRUCTIONS - patient wants to know how to prepare for a procedure
  EMERGENCY         - patient describes urgent symptoms or an emergency
  UNCLEAR           - intent cannot be determined

Reply with ONLY the label. No explanation. No punctuation."""

    def call():
        return llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["sanitized_message"])
        ])

    response = retry_middleware.run(call)
    intent   = response.content.strip().upper()

    valid = {"RESCHEDULE", "CANCEL", "PREP_INSTRUCTIONS", "EMERGENCY", "UNCLEAR"}
    if intent not in valid:
        intent = "UNCLEAR"

    print(f"[Node: classify] Intent: {intent}")

    return {
        "intent":     intent,
        "path_taken": state["path_taken"] + ["classify"],
    }


# ── NODE 3: draft ─────────────────────────────────────────────────
# Generates a polished draft patient-facing response using GPT.
# This draft goes to human review — it is NOT sent automatically.
def draft_response_node(state: dict) -> dict:
    print("\n[Node: draft] Generating draft response...")

    limiter = get_fresh_limiter()
    limiter.check()

    intent = state["intent"]

    instructions = {
        "RESCHEDULE": (
            "The patient wants to reschedule. Acknowledge warmly, confirm you will help, "
            "ask for their preferred new date/time and appointment reference if they have it."
        ),
        "CANCEL": (
            "The patient wants to cancel. Acknowledge empathetically, confirm it will be processed, "
            "and ask if they would like to reschedule in the future."
        ),
        "PREP_INSTRUCTIONS": (
            "The patient wants preparation instructions. Provide general guidance only "
            "(fasting, clothing, medications). Remind them to follow their doctor's specific "
            "instructions. Do NOT give clinical advice."
        ),
    }

    instruction = instructions.get(intent, "Respond helpfully and professionally.")

    system_prompt = f"""You are a professional medical appointment assistant.
{instruction}
Keep the response under 100 words. Warm, clear, professional tone.
Do NOT provide any clinical diagnosis or medical advice."""

    def call():
        return llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["sanitized_message"])
        ])

    response = retry_middleware.run(call)
    draft    = response.content.strip()

    print(f"[Node: draft] Draft generated.")

    return {
        "draft_response": draft,
        "path_taken":     state["path_taken"] + ["draft_response"],
    }


# ── NODE 4: escalate ──────────────────────────────────────────────
# Safety node — handles emergencies and flagged content.
# No LLM call here. Directs patient to seek immediate care.
def escalate_node(state: dict) -> dict:
    print("\n[Node: escalate] ESCALATION TRIGGERED.")

    reason = (
        "Emergency symptoms detected"
        if state.get("intent") == "EMERGENCY"
        else "Content flagged by moderation system"
    )

    final_response = (
        "We've received your message and it requires immediate attention. "
        "If you are experiencing a medical emergency, please call 911 or go to your "
        "nearest emergency room right away. A staff member will follow up with you "
        "as soon as possible. Please do not delay seeking care if you feel unwell."
    )

    return {
        "final_response":    final_response,
        "review_action":     "ESCALATED",
        "status":            "ESCALATE",
        "escalation_reason": reason,
        "path_taken":        state["path_taken"] + ["escalate"],
    }


# ── NODE 5: needs_info ────────────────────────────────────────────
# Called when intent is UNCLEAR. No LLM call — hardcoded for reliability.
def needs_info_node(state: dict) -> dict:
    print("\n[Node: needs_info] Intent unclear — requesting clarification.")

    final_response = (
        "Thank you for reaching out! We want to make sure we help you correctly, "
        "but we weren't quite sure what you needed. Could you please clarify whether "
        "you'd like to reschedule, cancel an appointment, or get preparation instructions "
        "for a procedure? We're happy to assist!"
    )

    return {
        "final_response": final_response,
        "review_action":  "NEEDS_INFO",
        "status":         "NEED_INFO",
        "path_taken":     state["path_taken"] + ["needs_info"],
    }

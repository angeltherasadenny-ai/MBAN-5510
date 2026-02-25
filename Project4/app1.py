# app.py
# Professional Chatbot-style Streamlit UI for the Appointment Assistant System.
# Run with: python -m streamlit run app.py

import streamlit as st
from dotenv import load_dotenv
from graph import appointment_graph
from datetime import datetime
import pandas as pd
import os

load_dotenv()

st.set_page_config(page_title="MediAssist", page_icon="🏥", layout="centered")

DATA_PATH = "appointments.csv"

# ─────────────────────────────
# UI: minimal styling
# ─────────────────────────────
st.markdown(
    """
    <style>
      /* ========= Bright Fresh Medical Theme ========= */
      :root{
        --bg1: #f0fffb;
        --bg2: #e6f9ff;

        --ink: #063b3b;
        --muted: rgba(6,59,59,.65);

        --card: rgba(255,255,255,.85);
        --card-strong: rgba(255,255,255,.95);
        --line: rgba(6,59,59,.12);

        --accent: #14b8a6;      /* bright teal */
        --accent2: #38bdf8;     /* sky blue */
        --accent3: #22c55e;     /* mint green */

        --shadow: 0 16px 60px rgba(6,59,59,.10);
        --shadow2: 0 10px 30px rgba(6,59,59,.08);
      }

      /* ========= Background ========= */
      .stApp{
        background:
          radial-gradient(800px 500px at 8% 8%, rgba(56,189,248,.20), transparent 60%),
          radial-gradient(800px 500px at 92% 12%, rgba(20,184,166,.18), transparent 55%),
          linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: var(--ink);
      }

      .block-container{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
      }

      /* ========= Sidebar ========= */
      section[data-testid="stSidebar"]{
        background: linear-gradient(180deg, rgba(255,255,255,.75), rgba(255,255,255,.55));
        border-right: 1px solid var(--line);
        backdrop-filter: blur(14px);
      }

      /* ========= Cards ========= */
      .card{
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 16px;
        background: var(--card);
        box-shadow: var(--shadow2);
        backdrop-filter: blur(14px);
      }

      .card h3{
        margin: 0 0 8px 0;
        font-size: 1rem;
        color: var(--ink);
      }

      .muted{
        color: var(--muted);
        font-size: 0.88rem;
      }

      .pill{
        display:inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        border: 1px solid rgba(20,184,166,.25);
        background: linear-gradient(90deg, rgba(20,184,166,.20), rgba(56,189,248,.20));
        font-size: 0.85rem;
        color: var(--ink);
      }

      /* ========= Chat Bubbles ========= */
      [data-testid="stChatMessage"]{
        padding: 0.25rem 0.25rem;
      }

      /* Assistant bubble */
      [data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] > div{
        background: var(--card-strong);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: var(--shadow2);
      }

      /* User bubble */
      [data-testid="stChatMessage"][data-testid="stChatMessage-user"] > div{
        background: linear-gradient(135deg, rgba(20,184,166,.25), rgba(56,189,248,.20));
        border: 1px solid rgba(20,184,166,.30);
        border-radius: 22px;
      }

      /* ========= Buttons ========= */
      div.stButton > button{
        border-radius: 18px !important;
        border: 1px solid var(--line) !important;
        box-shadow: 0 10px 30px rgba(6,59,59,.10) !important;
        padding: 0.7rem 1rem !important;
        transition: all .15s ease;
      }

      div.stButton > button:hover{
        transform: translateY(-2px);
        box-shadow: 0 16px 40px rgba(6,59,59,.15) !important;
        border-color: rgba(20,184,166,.35) !important;
      }

      /* Primary button */
      button[kind="primary"]{
        background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
        color: white !important;
        border: none !important;
      }

      /* ========= Progress Bar ========= */
      [data-testid="stProgress"] > div > div{
        background: linear-gradient(90deg, var(--accent), var(--accent3)) !important;
      }

      /* ========= DataFrame ========= */
      [data-testid="stDataFrame"]{
        border-radius: 20px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: var(--shadow2);
        background: var(--card-strong);
      }

      /* ========= Headings ========= */
      h1, h2, h3{
        letter-spacing: -0.02em;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Small UI helpers ──────────────────────────────────────────────
PHASE_LABELS = {
    "greeting": "Start",
    "collect_id": "Appointment Lookup",
    "collect_datetime": "New Date/Time",
    "collect_procedure": "Procedure",
    "hitl": "Staff Review",
    "edit": "Edit Response",
    "done": "Summary",
}
PHASE_ORDER = ["greeting", "collect_id", "collect_datetime", "collect_procedure", "hitl", "edit", "done"]


def phase_progress(phase: str) -> float:
    if phase not in PHASE_ORDER:
        return 0.0
    return (PHASE_ORDER.index(phase) + 1) / len(PHASE_ORDER)


def bot_say(text: str):
    st.session_state.chat_history.append({"role": "bot", "text": text, "ts": datetime.now().isoformat()})


def user_say(text: str):
    st.session_state.chat_history.append({"role": "user", "text": text, "ts": datetime.now().isoformat()})


def reset():
    for k in ["chat_history", "phase", "intent", "details", "result", "final_response", "run_id", "df"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def run_graph(msg: str):
    return appointment_graph.invoke(
        {
            "patient_message": msg,
            "run_id": None,
            "timestamp": None,
            "sanitized_message": None,
            "moderation_flagged": None,
            "moderation_cats": None,
            "intent": None,
            "draft_response": None,
            "final_response": None,
            "review_action": None,
            "status": None,
            "escalation_reason": None,
            "path_taken": [],
        }
    )


def prettify_datetime_suggestions():
    return [
        "2026-03-20 09:00",
        "2026-03-20 14:00",
        "2026-03-24 10:00",
        "2026-03-24 15:00",
        "2026-03-27 11:00",
        "2026-03-27 16:00",
    ]


# ── Dataset helpers (CSV-backed) ───────────────────────────────────
REQUIRED_COLS = [
    "appointment_id",
    "patient_name",
    "doctor_name",
    "appointment_date",
    "appointment_time",
    "status",
]


def load_dataset() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=REQUIRED_COLS)

    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""

    df["appointment_id"] = df["appointment_id"].astype(str)
    df["status"] = df["status"].astype(str).replace("", "Scheduled")
    return df[REQUIRED_COLS]


def save_dataset(df: pd.DataFrame) -> None:
    df.to_csv(DATA_PATH, index=False)


def get_df() -> pd.DataFrame:
    if "df" not in st.session_state:
        st.session_state.df = load_dataset()
    return st.session_state.df


def upsert_if_needed(appt_key: str) -> str:
    df = get_df()
    raw = (appt_key or "").strip()
    if not raw:
        return ""

    # looks like an ID
    if raw.upper().startswith("APT-"):
        appt_id = raw.upper()
        if not (df["appointment_id"].str.upper() == appt_id).any():
            new_row = {
                "appointment_id": appt_id,
                "patient_name": "",
                "doctor_name": "Dr. Patel",
                "appointment_date": "2026-03-12",
                "appointment_time": "10:30",
                "status": "Scheduled",
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.df = df
            save_dataset(df)
        return appt_id

    # name lookup
    name = raw.lower()
    matches = df[df["patient_name"].str.lower().str.contains(name, na=False)]
    if len(matches) > 0:
        return str(matches.iloc[0]["appointment_id"]).upper()

    return raw


def apply_cancel(appt_key: str):
    df = get_df()
    appt_id = upsert_if_needed(appt_key)
    if not appt_id:
        return

    mask = df["appointment_id"].str.upper() == appt_id.upper()
    if mask.any():
        df.loc[mask, "status"] = "Cancelled"
        st.session_state.df = df
        save_dataset(df)


def apply_reschedule(appt_key: str, new_datetime_text: str):
    df = get_df()
    appt_id = upsert_if_needed(appt_key)
    if not appt_id:
        return

    date_val, time_val = "", ""
    txt = (new_datetime_text or "").strip()
    parts = txt.split()

    # expected: YYYY-MM-DD HH:MM
    if len(parts) >= 2 and len(parts[0]) == 10 and "-" in parts[0] and ":" in parts[1]:
        date_val = parts[0]
        time_val = parts[1]
    else:
        date_val = txt
        time_val = ""

    mask = df["appointment_id"].str.upper() == appt_id.upper()
    if mask.any():
        df.loc[mask, "appointment_date"] = date_val
        df.loc[mask, "appointment_time"] = time_val
        df.loc[mask, "status"] = "Rescheduled"
        st.session_state.df = df
        save_dataset(df)


# ── Session state init ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "phase" not in st.session_state:
    st.session_state.phase = "greeting"
if "intent" not in st.session_state:
    st.session_state.intent = None
if "details" not in st.session_state:
    st.session_state.details = {}
if "result" not in st.session_state:
    st.session_state.result = None
if "final_response" not in st.session_state:
    st.session_state.final_response = None
if "run_id" not in st.session_state:
    st.session_state.run_id = None

df = get_df()

# ─────────────────────────────
# Sidebar: Dashboard panel
# ─────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div class="card">
          <h3>📊 Appointment Dashboard</h3>
          <div class="muted">Live view from <code>{DATA_PATH}</code></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    if len(df) == 0:
        view = pd.DataFrame([{"Appointment ID": "—", "Date": "—", "Time": "—", "Doctor": "—", "Status": "No records"}])
        st.dataframe(view, use_container_width=True, hide_index=True, height=240)
    else:
        view = df.rename(
            columns={
                "appointment_id": "Appointment ID",
                "appointment_date": "Date",
                "appointment_time": "Time",
                "doctor_name": "Doctor",
                "status": "Status",
            }
        )[["Appointment ID", "Date", "Time", "Doctor", "Status"]]
        st.dataframe(view, use_container_width=True, hide_index=True, height=240)

    st.write("")
    st.markdown("---")
    st.markdown(f"**Progress**")
    st.progress(phase_progress(st.session_state.phase))
    st.markdown(f"<span class='pill'>Step: {PHASE_LABELS.get(st.session_state.phase, st.session_state.phase)}</span>", unsafe_allow_html=True)

    if st.session_state.intent:
        st.markdown(f"**Intent:** `{st.session_state.intent}`")

    if st.session_state.details:
        with st.expander("Details captured"):
            st.json(st.session_state.details)

    st.write("")
    if st.button("🔄 Reset", use_container_width=True):
        reset()

# ─────────────────────────────
# Main header
# ─────────────────────────────
st.markdown("## 🏥 MediAssist")
st.caption("Appointment Assistant · MBAN 5510")
st.divider()

# First greeting
if st.session_state.phase == "greeting" and not st.session_state.chat_history:
    bot_say("👋 Hi! I’m **MediAssist**. How can I help with your appointment today?")

# Chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "bot":
        with st.chat_message("assistant", avatar="🏥"):
            st.write(msg["text"])
    else:
        with st.chat_message("user", avatar="🙋"):
            st.write(msg["text"])

# ─────────────────────────────
# PHASE: greeting
# ─────────────────────────────
if st.session_state.phase == "greeting":
    st.markdown("### Choose an action")
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("📅 Reschedule", use_container_width=True, type="primary"):
            user_say("I want to reschedule my appointment")
            bot_say(
                "Sure — I can help.\n\n"
                "**Please enter your appointment ID** (e.g., `APT-001`).\n\n"
                "If you don’t know it, type your **name** (must exist in the dataset)."
            )
            st.session_state.intent = "RESCHEDULE"
            st.session_state.phase = "collect_id"
            st.toast("Reschedule started ✅")
            st.rerun()

    with c2:
        if st.button("❌ Cancel", use_container_width=True):
            user_say("I want to cancel my appointment")
            bot_say(
                "No problem.\n\n"
                "**Please enter your appointment ID** (e.g., `APT-001`).\n\n"
                "If you don’t know it, type your **name** (must exist in the dataset)."
            )
            st.session_state.intent = "CANCEL"
            st.session_state.phase = "collect_id"
            st.toast("Cancel started ✅")
            st.rerun()

    with c3:
        if st.button("📋 Prep Instructions", use_container_width=True):
            user_say("I need preparation instructions")
            bot_say("Sure. **Which procedure** are you preparing for?")
            st.session_state.intent = "PREP_INSTRUCTIONS"
            st.session_state.phase = "collect_procedure"
            st.toast("Prep flow started ✅")
            st.rerun()

    st.write("")
    st.markdown("**Or type your request**")
    if prompt := st.chat_input("Example: “Reschedule APT-001 to 2026-03-20 14:00”"):
        user_say(prompt)
        with st.spinner("Processing..."):
            result = run_graph(prompt)
            st.session_state.result = result

        status = result.get("status")
        if status == "ESCALATE":
            bot_say("🚨 " + (result.get("final_response") or "A staff member will follow up shortly."))
            st.session_state.phase = "done"
            st.session_state.final_response = result.get("final_response")
            st.session_state.run_id = result.get("run_id")
            st.toast("Escalated 🚨")
        elif status == "NEED_INFO":
            bot_say("To help you correctly, do you want to **reschedule**, **cancel**, or get **prep instructions**?")
            st.session_state.phase = "greeting"
            st.toast("Need more info ℹ️")
        else:
            bot_say("Draft prepared for staff review.")
            st.session_state.phase = "hitl"
            st.session_state.run_id = result.get("run_id")
            st.toast("Draft ready ✍️")

        st.rerun()

# ─────────────────────────────
# PHASE: collect_id
# ─────────────────────────────
elif st.session_state.phase == "collect_id":
    st.markdown("### Appointment lookup")
    st.info("Tip: Use an appointment ID like `APT-001`. If using a name, it must exist in the dataset.")

    chips = ["APT-001", "APT-014", "Jane Doe", "John Smith"]
    cc = st.columns(4)
    for i, chip in enumerate(chips):
        with cc[i]:
            if st.button(chip, use_container_width=True):
                user_say(chip)
                st.session_state.details["appointment_id"] = chip
                mapped = upsert_if_needed(chip)
                st.session_state.details["mapped_appointment_id"] = mapped

                if st.session_state.intent == "RESCHEDULE":
                    bot_say("Great. Enter the **new date/time** in this format: `YYYY-MM-DD HH:MM`.")
                    st.session_state.phase = "collect_datetime"
                else:
                    apply_cancel(mapped)
                    msg = f"I want to cancel appointment {mapped}"
                    with st.spinner("Processing..."):
                        result = run_graph(msg)
                        st.session_state.result = result
                        st.session_state.run_id = result.get("run_id")
                    bot_say("Draft prepared for staff review.")
                    st.session_state.phase = "hitl"
                st.rerun()

    if appt_id := st.chat_input("Enter appointment ID (APT-001) or patient name..."):
        user_say(appt_id)
        st.session_state.details["appointment_id"] = appt_id
        mapped = upsert_if_needed(appt_id)
        st.session_state.details["mapped_appointment_id"] = mapped

        if st.session_state.intent == "RESCHEDULE":
            bot_say("Perfect. Enter the **new date/time** in this format: `YYYY-MM-DD HH:MM`.")
            st.session_state.phase = "collect_datetime"
        else:
            apply_cancel(mapped)
            msg = f"I want to cancel appointment {mapped}"
            with st.spinner("Processing..."):
                result = run_graph(msg)
                st.session_state.result = result
                st.session_state.run_id = result.get("run_id")
            bot_say("Draft prepared for staff review.")
            st.session_state.phase = "hitl"

        st.rerun()

# ─────────────────────────────
# PHASE: collect_datetime
# ─────────────────────────────
elif st.session_state.phase == "collect_datetime":
    st.markdown("### New appointment date & time")
    st.caption("Recommended format: `YYYY-MM-DD HH:MM` (24-hour time).")

    suggestions = prettify_datetime_suggestions()
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(s, use_container_width=True):
                user_say(s)
                st.session_state.details["new_datetime"] = s
                appt_id = st.session_state.details.get("mapped_appointment_id") or st.session_state.details.get("appointment_id", "")
                apply_reschedule(appt_id, s)

                msg = f"I want to reschedule appointment {appt_id} to {s}"
                with st.spinner("Processing..."):
                    result = run_graph(msg)
                    st.session_state.result = result
                    st.session_state.run_id = result.get("run_id")

                bot_say("Draft prepared for staff review.")
                st.session_state.phase = "hitl"
                st.rerun()

    if new_datetime := st.chat_input("Enter new date/time (YYYY-MM-DD HH:MM)..."):
        user_say(new_datetime)
        st.session_state.details["new_datetime"] = new_datetime
        appt_id = st.session_state.details.get("mapped_appointment_id") or st.session_state.details.get("appointment_id", "")
        apply_reschedule(appt_id, new_datetime)

        msg = f"I want to reschedule appointment {appt_id} to {new_datetime}"
        with st.spinner("Processing..."):
            result = run_graph(msg)
            st.session_state.result = result
            st.session_state.run_id = result.get("run_id")

        bot_say("Draft prepared for staff review.")
        st.session_state.phase = "hitl"
        st.rerun()

# ─────────────────────────────
# PHASE: collect_procedure
# ─────────────────────────────
elif st.session_state.phase == "collect_procedure":
    st.markdown("### Procedure selection")
    procedures = ["MRI Imaging", "Ultrasound", "CT Scan", "Blood Test", "General Checkup"]
    cols = st.columns(3)

    for i, proc in enumerate(procedures):
        with cols[i % 3]:
            if st.button(proc, use_container_width=True):
                user_say(proc)
                msg = f"What do I need to do to prepare for my {proc}?"
                with st.spinner("Processing..."):
                    result = run_graph(msg)
                    st.session_state.result = result
                    st.session_state.run_id = result.get("run_id")
                bot_say("Draft prepared for staff review.")
                st.session_state.phase = "hitl"
                st.rerun()

    if other := st.chat_input("Or type your procedure here..."):
        user_say(other)
        msg = f"What do I need to do to prepare for my {other}?"
        with st.spinner("Processing..."):
            result = run_graph(msg)
            st.session_state.result = result
            st.session_state.run_id = result.get("run_id")
        bot_say("Draft prepared for staff review.")
        st.session_state.phase = "hitl"
        st.rerun()

# ─────────────────────────────
# PHASE: hitl
# ─────────────────────────────
elif st.session_state.phase == "hitl":
    result = st.session_state.result or {}
    with st.chat_message("assistant", avatar="🏥"):
        st.write("**👩‍⚕️ Staff Review — Approval Required**")
        draft = result.get("draft_response") or "_(No draft response was generated.)_"
        st.info(draft)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Approve & Send", type="primary", use_container_width=True):
                final = result.get("draft_response") or "Your request has been received. A staff member will follow up shortly."
                result.setdefault("path_taken", []).append("human_review")
                result["status"] = "READY"
                st.session_state.final_response = final
                bot_say(f"✅ **Approved message sent:**\n\n_{final}_")
                st.session_state.phase = "done"
                st.rerun()

        with col2:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.phase = "edit"
                st.rerun()

        with col3:
            if st.button("❌ Reject", use_container_width=True):
                fallback = "Your request has been received. A staff member will follow up with you shortly."
                result.setdefault("path_taken", []).append("human_review")
                result["status"] = "READY"
                st.session_state.final_response = fallback
                bot_say(f"❌ **Draft rejected.** Sent fallback:\n\n_{fallback}_")
                st.session_state.phase = "done"
                st.rerun()

# ─────────────────────────────
# PHASE: edit
# ─────────────────────────────
elif st.session_state.phase == "edit":
    result = st.session_state.result or {}
    with st.chat_message("assistant", avatar="🏥"):
        st.write("**✏️ Edit response**")
        edited = st.text_area("Edit draft:", value=result.get("draft_response", ""), height=160, key="edit_draft")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📤 Send", type="primary", use_container_width=True):
                if edited.strip():
                    result.setdefault("path_taken", []).append("human_review")
                    result["status"] = "READY"
                    st.session_state.final_response = edited.strip()
                    bot_say(f"✏️ **Edited message sent:**\n\n_{edited.strip()}_")
                    st.session_state.phase = "done"
                    st.rerun()
                else:
                    st.warning("Response cannot be empty.")
        with c2:
            if st.button("↩️ Back", use_container_width=True):
                st.session_state.phase = "hitl"
                st.rerun()

# ─────────────────────────────
# PHASE: done
# ─────────────────────────────
elif st.session_state.phase == "done":
    result = st.session_state.result or {}

    with st.chat_message("assistant", avatar="🏥"):
        st.divider()
        st.write("**📋 Summary**")

        status = result.get("status", "READY")
        path = result.get("path_taken", [])
        run_id = result.get("run_id", "N/A")
        timestamp = result.get("timestamp", "N/A")
        intent = result.get("intent", st.session_state.intent or "N/A")
        esc_reason = result.get("escalation_reason", "")

        m1, m2, m3 = st.columns(3)
        m1.metric("Run ID", run_id)
        m2.metric("Status", status)
        m3.metric("Intent", intent)

        st.write(f"**Path:** `{' → '.join(path) if path else 'N/A'}`")
        st.write(f"**Timestamp:** {timestamp}")
        if esc_reason:
            st.warning(f"**Escalation reason:** {esc_reason}")

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 New request", type="primary", use_container_width=True):
            reset()
    with c2:
        if st.button("🧹 Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
"""
ARIA — Cybercrime Reporting Chatbot
Streamlit frontend connecting to FastAPI backend (main.py).

The LLM reads the full conversation history and decides what to ask next —
no hardcoded questions ever.

Run:
    uvicorn main:app --host 0.0.0.0 --port 8000   # Terminal 1
    streamlit run streamlit_app.py                  # Terminal 2
"""

import streamlit as st
import requests
import json
import time
from groq import Groq
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

CRIME_SCHEMAS = {
    "phishing":       ["victim_email","sender_email","email_subject","link_clicked",
                       "credentials_entered","credentials_lost","date_received",
                       "financial_loss","action_taken"],
    "ransomware":     ["affected_systems","ransom_amount","currency","ransom_note",
                       "file_extensions_encrypted","date_infection","ransomware_name",
                       "data_exfiltration","backups_available","contact_made_attacker"],
    "data_breach":    ["organization_name","data_types","records_affected",
                       "discovery_date","attack_vector","notification_status",
                       "estimated_damage"],
    "identity_theft": ["victim_name","date_discovered","fraudulent_accounts",
                       "credit_inquiries","financial_loss","credit_freeze",
                       "fraud_alert_filed"],
    "fraud":          ["fraud_type","victim_name","amount","payment_method",
                       "fraud_date","detection_method","suspect_info",
                       "bank_name","transaction_id"],
    "malware":        ["affected_systems","malware_type","detection_date","symptoms",
                       "malicious_activity","antivirus_product","quarantine_status",
                       "data_accessed"],
    "ddos":           ["target_url","attack_start_time","attack_duration_minutes",
                       "attack_type","peak_traffic","downtime",
                       "financial_impact","mitigation_steps"],
    "hacking":        ["entry_point","compromised_systems","discovery_date",
                       "unauthorized_actions","data_stolen","access_duration",
                       "persistence_methods"],
    "extortion":      ["extortion_method","threat_content","demanded_amount",
                       "payment_method_requested","deadline","evidence_claimed",
                       "contact_made","amount_paid"],
    "spam":           ["message_type","sender_address","message_content","frequency",
                       "first_received","credentials_requested",
                       "financial_requests","actions_taken"],
}

CRIME_EMOJI = {
    "phishing":"🎣","ransomware":"🔒","data_breach":"💾","identity_theft":"👤",
    "fraud":"💰","malware":"🦠","ddos":"⚡","hacking":"💻","extortion":"⚠️","spam":"📧",
}

# ── Groq LLM — one function that does everything ──────────────────────────────

def _get_secret(key: str) -> str:
    """Safely read from st.secrets — returns empty string if no secrets file exists."""
    try:
        return st.secrets.get(key, "")
    except Exception:
        return ""

def get_groq_client() -> Optional[Groq]:
    # Session state (typed in sidebar) takes priority over secrets file
    key = st.session_state.get("groq_key", "").strip() or _get_secret("GROQ_API_KEY").strip()
    if not key:
        return None
    return Groq(api_key=key)


def llm_next_turn(history: list, phase: str,
                  crime_type: Optional[str], filled: dict,
                  schema_fields: list) -> dict:
    """
    Send the full conversation to Groq.
    Returns:
        message        — what ARIA says next
        intent_locked  — crime type string once confident, else None
        extracted      — {field: value} pulled from latest user message
        complete       — True when all critical fields are collected
        confidence     — float 0–1
    """
    client = get_groq_client()
    if not client:
        return {
            "message": "⚠️ Please enter your Groq API key in the sidebar to continue.",
            "intent_locked": None, "extracted": {}, "complete": False, "confidence": 0
        }

    missing = [f for f in schema_fields if f not in filled]

    if phase == "probing":
        system = """You are ARIA, a professional and empathetic cybercrime reporting AI officer.

TASK — PROBING PHASE:
Read the full conversation carefully. The user is describing a cybercrime incident.
Your job is to ask ONE smart, specific follow-up question to learn more.

Rules:
- Read everything already said. Do NOT repeat anything already answered.
- Ask only ONE question. Make it specific to what the user just told you.
- Be empathetic and professional, like a detective — not a form-filler.
- If you are ≥80% confident about the crime type, set intent_locked to the crime type.

Crime types: phishing, ransomware, data_breach, identity_theft, fraud, malware, ddos, hacking, extortion, spam

Respond ONLY with this exact JSON (no extra text, no markdown):
{
  "message": "<your specific follow-up question or empathetic acknowledgement + question>",
  "intent_locked": null,
  "confidence": 0.0,
  "extracted": {}
}"""
    else:
        missing_str = ", ".join(missing) if missing else "none — all done!"
        filled_json = json.dumps(filled, indent=2)
        system = f"""You are ARIA, a professional cybercrime reporting AI officer.

TASK — SLOT FILLING PHASE:
Crime type is locked: {crime_type}

Already collected:
{filled_json}

Still missing: {missing_str}

Read the ENTIRE conversation carefully.
1. From the user's LATEST message, silently extract any values for missing fields.
2. Ask ONE natural conversational question to get the next most important missing field.
   — Be specific, empathetic, and acknowledge what they just said.
   — Do NOT ask about fields already filled.
   — Do NOT list multiple questions.
3. If missing = "none — all done!" or all critical fields are filled, set complete=true
   and write a warm closing message instead of a question.

Respond ONLY with this exact JSON (no extra text, no markdown):
{{
  "message": "<specific question based on conversation, or closing message>",
  "intent_locked": "{crime_type}",
  "extracted": {{"<field_name>": "<value from user's latest message>"}},
  "complete": false,
  "confidence": 0.9
}}"""

    # Build message list for Groq (only role + content, no internal meta)
    groq_msgs = [{"role": m["role"], "content": m["content"]} for m in history]

    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system}] + groq_msgs,
            max_tokens=500,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content.strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)
        return {
            "message":       parsed.get("message", "Could you share more details?"),
            "intent_locked": parsed.get("intent_locked"),
            "extracted":     parsed.get("extracted", {}),
            "complete":      bool(parsed.get("complete", False)),
            "confidence":    float(parsed.get("confidence", 0.5)),
        }
    except json.JSONDecodeError as e:
        # LLM returned something but not valid JSON — extract the message at least
        try:
            # Try to grab just the message field with a simple heuristic
            import re
            m = re.search(r'"message"\s*:\s*"([^"]+)"', raw)
            msg = m.group(1) if m else raw[:300]
        except Exception:
            msg = "Could you describe what happened in a bit more detail?"
        return {
            "message": msg,
            "intent_locked": None, "extracted": {}, "complete": False, "confidence": 0.5
        }
    except Exception as e:
        return {
            "message": f"Sorry, I had a technical issue ({e}). Could you continue?",
            "intent_locked": None, "extracted": {}, "complete": False, "confidence": 0.5
        }


# ── FastAPI helpers ───────────────────────────────────────────────────────────

def api_get(path: str) -> Optional[dict]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=8)
        return r.json() if r.ok else None
    except Exception:
        return None

def api_post(path: str, payload: dict) -> Optional[dict]:
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
        return r.json() if r.ok else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}

def check_backend() -> bool:
    r = api_get("/health")
    return bool(r and r.get("status") == "healthy")

def backend_classify(description: str) -> dict:
    return api_post("/api/v1/classify-crime", {"description": description}) or {}

def backend_report(description: str, crime_type: str, case_id: str, answers: dict) -> dict:
    return api_post("/api/v1/submit-report", {
        "user_input": description,
        "crime_type": crime_type,
        "case_id":    case_id,
        "answers":    answers,
    }) or {}


# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "phase":           "idle",   # idle | probing | filling | done
        "messages":        [],       # {role, content, meta} — full history
        "description":     "",       # cumulative user text
        "case_id":         None,
        "crime_type":      None,
        "confidence":      0.0,
        "pipeline_result": None,
        "filled_schema":   {},       # field → value
        "answers":         {},       # for /submit-report
        "report":          None,
        "backend_ok":      False,
        "groq_key":        "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def add_message(role: str, content: str, meta: dict = None):
    st.session_state.messages.append({
        "role": role, "content": content, "meta": meta or {}
    })

def reset():
    preserve = {"groq_key": st.session_state.get("groq_key", "")}
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()
    for k, v in preserve.items():
        st.session_state[k] = v


# ── Core turn handler ─────────────────────────────────────────────────────────

def handle_user_turn(user_text: str):
    st.session_state.description += " " + user_text
    add_message("user", user_text)

    phase         = st.session_state.phase
    crime_type    = st.session_state.crime_type
    filled        = st.session_state.filled_schema
    schema_fields = CRIME_SCHEMAS.get(crime_type, []) if crime_type else []

    # Build clean history (role + content only) for the LLM
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.messages]

    turn = llm_next_turn(
        history       = history,
        phase         = "probing" if phase in ("idle", "probing") else "filling",
        crime_type    = crime_type,
        filled        = filled,
        schema_fields = schema_fields,
    )

    # ── Persist extracted fields ───────────────────────────────────────────────
    if turn["extracted"]:
        for field, value in turn["extracted"].items():
            # Accept any field that belongs to the locked schema
            if not schema_fields or field in schema_fields:
                st.session_state.filled_schema[field] = value
        st.session_state.answers.update(turn["extracted"])

    # ── Intent lock ────────────────────────────────────────────────────────────
    locked = turn.get("intent_locked")
    if locked and locked != "null" and not crime_type:
        st.session_state.crime_type = locked
        st.session_state.confidence = turn["confidence"]
        st.session_state.case_id    = f"case_{int(time.time())}"
        st.session_state.phase      = "filling"

        # Fire 4-stage pipeline for sidebar details (non-blocking in spirit)
        if st.session_state.backend_ok:
            result = backend_classify(st.session_state.description.strip())
            st.session_state.pipeline_result = result

        add_message("assistant", turn["message"], meta={
            "intent_locked": locked,
            "confidence":    turn["confidence"],
            "extracted":     turn["extracted"],
        })
        return

    # ── Completion ─────────────────────────────────────────────────────────────
    schema_fields = CRIME_SCHEMAS.get(st.session_state.crime_type, [])
    all_filled = schema_fields and all(
        f in st.session_state.filled_schema for f in schema_fields
    )
    if turn.get("complete") or all_filled:
        st.session_state.phase = "done"
        add_message("assistant", turn["message"],
                    meta={"extracted": turn["extracted"]})
        _generate_report()
        return

    # ── Normal reply ───────────────────────────────────────────────────────────
    if turn["confidence"] > st.session_state.confidence:
        st.session_state.confidence = turn["confidence"]
    if phase == "idle":
        st.session_state.phase = "probing"

    add_message("assistant", turn["message"],
                meta={"extracted": turn["extracted"]})


def _generate_report():
    if not st.session_state.backend_ok:
        st.session_state.report = {"report_data": st.session_state.filled_schema,
                                   "status": "local_only"}
        return
    with st.spinner("Generating official report via backend…"):
        result = backend_report(
            st.session_state.description.strip(),
            st.session_state.crime_type,
            st.session_state.case_id,
            st.session_state.answers,
        )
    st.session_state.report = result


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🛡️ ARIA")
        st.caption("Cybercrime Reporting AI")

        if not _get_secret("GROQ_API_KEY"):
            st.text_input(
                "Groq API Key", type="password",
                placeholder="gsk_…",
                key="groq_key",   # binds directly to st.session_state.groq_key
            )

        ok = check_backend()
        st.session_state.backend_ok = ok
        if ok:
            st.success("FastAPI online", icon="✅")
        else:
            st.warning("FastAPI offline", icon="⚠️")
            with st.expander("Start backend"):
                st.code("uvicorn main:app --port 8000", language="bash")

        st.divider()

        label = {
            "idle":    "⬜ Waiting for input",
            "probing": "🔍 Probing — gathering info",
            "filling": "📝 Filling report fields",
            "done":    "✅ Report complete",
        }.get(st.session_state.phase, st.session_state.phase)
        st.markdown(f"**Status:** {label}")

        if st.session_state.confidence > 0:
            st.markdown(f"**Confidence:** {int(st.session_state.confidence * 100)}%")
            st.progress(min(st.session_state.confidence, 1.0))

        ct = st.session_state.crime_type
        if ct:
            st.markdown(f"**Crime:** {CRIME_EMOJI.get(ct,'')} {ct.replace('_',' ').title()}")
            st.divider()
            st.markdown("**Report fields**")
            for field in CRIME_SCHEMAS.get(ct, []):
                val = st.session_state.filled_schema.get(field)
                if val:
                    st.markdown(f"✅ **{field.replace('_',' ')}**  \n`{str(val)[:50]}`")
                else:
                    st.markdown(f"⬜ {field.replace('_',' ')}")

        if st.session_state.pipeline_result:
            st.divider()
            with st.expander("🔬 4-Stage Pipeline"):
                pr = st.session_state.pipeline_result
                for sid, skey, lbl in [
                    (1,"stage1_semantic_router","Semantic Router"),
                    (2,"stage2_hierarchical_classifier","Hierarchical"),
                    (3,"stage3_pattern_matcher","Pattern Match"),
                    (4,"stage4_rag_retriever","RAG Validation"),
                ]:
                    s = pr.get("stages", {}).get(skey)
                    if s:
                        st.caption(f"**S{sid} {lbl}**")
                        if sid == 1:
                            st.caption(f"`{s.get('primary_match')}` — {s.get('primary_score',0):.2f}")
                        elif sid == 2:
                            st.caption(f"`{s.get('crime_type')}` depth {s.get('depth')}")
                        elif sid == 3:
                            st.caption(f"`{s.get('strongest_match')}` {s.get('pattern_strength',0):.2f}")
                        elif sid == 4:
                            st.caption(f"supported={s.get('rag_supported')} conf={s.get('rag_confidence',0):.2f}")

        st.divider()
        if st.button("↺ New report", use_container_width=True):
            reset()
            st.rerun()


# ── Chat + report ─────────────────────────────────────────────────────────────

def render_chat():
    for msg in st.session_state.messages:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])

            meta = msg.get("meta", {})

            if meta.get("intent_locked"):
                ct   = meta["intent_locked"]
                conf = int(meta.get("confidence", 0) * 100)
                emoji = CRIME_EMOJI.get(ct, "🔍")
                st.markdown(
                    f"<span style='background:#1a2744;border:1px solid #3b82f6;"
                    f"border-radius:8px;padding:3px 10px;font-size:12px;color:#60a5fa'>"
                    f"🔒 Intent locked → {emoji} <b>{ct.replace('_',' ').upper()}</b>"
                    f" ({conf}% confidence)</span>",
                    unsafe_allow_html=True,
                )

            extracted = meta.get("extracted", {})
            if extracted:
                def field_badge(f):
                    label = f.replace("_", " ")
                    return (
                        f"<span style='background:#0a2e1a;border:1px solid #16a34a;"
                        f"border-radius:10px;padding:2px 8px;font-size:11px;"
                        f"color:#4ade80;margin:2px'>✓ {label}</span>"
                    )
                badges = " ".join(field_badge(f) for f in extracted)
                st.markdown(badges, unsafe_allow_html=True)


def render_report():
    report = st.session_state.report
    if not report:
        return

    st.divider()
    st.markdown("## 📋 Official Incident Report")

    ct = st.session_state.crime_type or "unknown"
    c1, c2, c3 = st.columns(3)
    c1.metric("Crime Type", f"{CRIME_EMOJI.get(ct,'')} {ct.replace('_',' ').title()}")
    c2.metric("Confidence",  f"{int(st.session_state.confidence * 100)}%")
    schema = CRIME_SCHEMAS.get(ct, [])
    c3.metric("Fields Filled", f"{len(st.session_state.filled_schema)}/{len(schema)}")

    with st.expander("📄 Full Report JSON", expanded=True):
        st.json(report.get("report_data", st.session_state.filled_schema))

    with st.expander("🗂️ Collected Schema Values"):
        st.json(st.session_state.filled_schema)

    corr = report.get("correlation_analysis")
    if corr and isinstance(corr, dict) and corr.get("status") not in (None, "no_correlation"):
        with st.expander("🔗 Correlation Analysis"):
            st.markdown(f"**Status:** {corr.get('status')}  \n**Score:** {corr.get('correlation_score',0):.2f}")
            if corr.get("recommendation"):
                st.info(corr["recommendation"])

    st.download_button(
        "⬇️ Download Report JSON",
        data=json.dumps({
            "case_id":       st.session_state.case_id,
            "crime_type":    ct,
            "confidence":    st.session_state.confidence,
            "filled_schema": st.session_state.filled_schema,
            "full_report":   report.get("report_data", {}),
        }, indent=2),
        file_name=f"aria_report_{st.session_state.case_id}.json",
        mime="application/json",
        use_container_width=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="ARIA — Cybercrime Reporter",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_state()
    render_sidebar()

    st.title("🛡️ ARIA — Cybercrime Reporting AI")
    st.caption(
        "Describe what happened in plain language. "
        "ARIA reads everything you say and asks the right question next — automatically."
    )

    if not st.session_state.messages:
        add_message(
            "assistant",
            "Hello, I'm **ARIA** — your AI cybercrime reporting officer. "
            "Please tell me what happened. Just describe it in your own words "
            "and I'll take it from there."
        )

    render_chat()
    render_report()

    if st.session_state.phase != "done":
        user_input = st.chat_input("Describe what happened…")
        if user_input and user_input.strip():
            with st.spinner("ARIA is reading your message…"):
                handle_user_turn(user_input.strip())
            st.rerun()
    else:
        st.info("✅ Report complete. Use **↺ New report** in the sidebar to start again.")


if __name__ == "__main__":
    main()
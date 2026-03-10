"""
CS3299:Capstone_Project — Cybercrime Reporting Chatbot
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
from validators import FieldValidator
from report_templates import generate_formatted_report

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
                  schema_fields: list, validation_errors: dict = None) -> dict:
    """
    Send the full conversation to Groq.
    Returns:
        message        — what CS3299:Capstone_Project says next
        intent_locked  — crime type string once confident, else None
        extracted      — {field: value} pulled from latest user message
        complete       — True when all critical fields are collected
        confidence     — float 0–1
    """
    client = get_groq_client()
    if not client:
        return {
            "message": "⚠️ System Configuration Required: Groq API Key must be configured in system settings.",
            "intent_locked": None, "extracted": {}, "complete": False, "confidence": 0
        }

    missing = [f for f in schema_fields if f not in filled]
    validation_errors = validation_errors or {}

    if phase == "probing":
        system = """You are a cybercrime reporting system assisting police officers in documenting incidents.

TASK — INCIDENT CLASSIFICATION PHASE:
Analyze the provided incident description to classify the cybercrime type.
Ask ONE specific follow-up question to gather critical information and confirm classification.

Rules:
- Maintain formal, professional tone throughout
- Do NOT use casual language, pleasantries, or personal remarks
- Ask only ONE clarifying question per response
- Question must be specific and relevant to incident details
- If confidence in crime type classification is ≥80%, lock the classification
- All questions must be direct and information-focused

Crime types: phishing, ransomware, data_breach, identity_theft, fraud, malware, ddos, hacking, extortion, spam

Respond ONLY with this exact JSON (no extra text, no markdown):
{
  "message": "<direct, formal clarifying question>",
  "intent_locked": null,
  "confidence": 0.0,
  "extracted": {}
}"""
    else:
        missing_str = ", ".join(missing) if missing else "none — all done!"
        filled_json = json.dumps(filled, indent=2)
        
        # Build validation errors message
        validation_msg = ""
        if validation_errors:
            validation_msg = "\n\nRECENT VALIDATION FAILURES:\n"
            for field, error in validation_errors.items():
                validation_msg += f"- {field}: {error}\n"
            validation_msg += "\nIMPORTANT: Do NOT accept values that failed validation. Ask the user to provide the correct format using the validation rules above."
        
        system = f"""You are a cybercrime report processing system assisting police officers.

TASK — INCIDENT INFORMATION COLLECTION:
Crime type classification: {crime_type}

Information already recorded:
{filled_json}

Information still required: {missing_str}
{validation_msg}

INSTRUCTIONS:
1. Extract any values from the user's latest message that match the required fields
2. Ask ONE specific question to obtain the next critical missing information
   — Questions must be direct and formal
   — Do NOT ask about fields already recorded
   — Do NOT include pleasantries or casual remarks
3. REJECT any values that failed validation. Request the correct format explicitly
4. If all required information is collected, set complete=true and provide a formal completion notice

Response format (JSON only, no additional text):
{{
  "message": "<direct question or completion notice>",
  "intent_locked": "{crime_type}",
  "extracted": {{"<field_name>": "<extracted value>"}},
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
            "message":       parsed.get("message", "Provide additional incident details."),
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
            msg = "Provide detailed information about the incident."
        return {
            "message": msg,
            "intent_locked": None, "extracted": {}, "complete": False, "confidence": 0.5
        }
    except Exception as e:
        return {
            "message": f"System error: {e}. Please retry.",
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

def backend_start_report(description: str) -> dict:
    """Step 1: Start report - Initial crime classification"""
    return api_post("/api/v1/start-report", {"description": description}) or {}

def backend_classify(description: str) -> dict:
    """Step 1b: Full 4-stage classification with Self-RAG and Expert Analyzer"""
    return api_post("/api/v1/classify-crime", {"description": description}) or {}

def backend_get_questions(description: str, crime_type: str, case_id: str) -> dict:
    """Step 2: Get crime-type-specific questions from backend"""
    return api_post("/api/v1/get-questions", {
        "description": description,
        "crime_type": crime_type,
        "case_id": case_id,
    }) or {"questions": []}

def backend_report(description: str, crime_type: str, case_id: str, answers: dict) -> dict:
    """Step 3-6: Generate report with correlation analysis and case registration"""
    return api_post("/api/v1/submit-report", {
        "user_input": description,
        "crime_type": crime_type,
        "case_id":    case_id,
        "answers":    answers,
    }) or {}


# ── Session state ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "phase":              "idle",   # idle | probing | filling | done
        "messages":           [],       # {role, content, meta} — full history
        "description":        "",       # cumulative user text
        "case_id":            None,
        "crime_type":         None,
        "confidence":         0.0,
        
        # Pipeline results from backend
        "start_report_result":None,    # Step 1: Initial classification
        "pipeline_result":    None,    # Step 1b: Full 4-stage pipeline
        "questions":          [],      # Step 2: Backend-provided questions
        
        "filled_schema":      {},       # field → value
        "answers":            {},       # for /submit-report
        "report":             None,     # Step 3-6: Final report with correlation
        "backend_ok":         False,
        "groq_key":           "",
        "validation_errors":  {},       # field → error message (cleared after each turn)
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
    """
    Refactored to follow the complete 6-step backend workflow:
    1. Start Report (initial classification)
    2. Get Questions (from backend)
    3. Fill Schema
    4. Submit Report (generate report + correlation analysis)
    """
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
        history            = history,
        phase              = "probing" if phase in ("idle", "probing") else "filling",
        crime_type         = crime_type,
        filled             = filled,
        schema_fields      = schema_fields,
        validation_errors  = st.session_state.validation_errors,
    )

    # ── Validate and persist extracted fields ──────────────────────────────────
    validation_errors = {}  # Track new validation errors for this turn
    
    if turn["extracted"]:
        for field, value in turn["extracted"].items():
            if not schema_fields or field in schema_fields:
                # Validate the field
                is_valid, error_msg = FieldValidator.validate_field(field, value)
                
                if is_valid:
                    # Field is valid — store it
                    st.session_state.filled_schema[field] = value
                    st.session_state.answers[field] = value
                else:
                    # Field is invalid — track the error and don't store it
                    validation_errors[field] = error_msg
                    
                    # Add a note to the conversation about the validation error
                    error_note = f"⚠️ Invalid {field.replace('_', ' ')}: {error_msg}"
                    st.session_state.messages[-1] = {
                        **st.session_state.messages[-1],
                        "meta": {**st.session_state.messages[-1].get("meta", {}), "validation_error": error_note}
                    }
    
    # Store validation errors for next turn (so LLM knows what failed)
    st.session_state.validation_errors = validation_errors

    # ── Intent lock — STEP 1: Start Report & Full Classification ──────────────
    locked = turn.get("intent_locked")
    if locked and locked != "null" and not crime_type:
        st.session_state.crime_type = locked
        st.session_state.confidence = turn["confidence"]
        st.session_state.case_id    = f"case_{int(time.time())}"
        st.session_state.phase      = "filling"

        add_message("assistant", turn["message"], meta={
            "intent_locked": locked,
            "confidence":    turn["confidence"],
            "extracted":     turn["extracted"],
        })

        # BACKEND STEP 1: Start report with initial classification
        if st.session_state.backend_ok:
            with st.spinner("🔍 Classifying incident..."):
                start_result = backend_start_report(st.session_state.description.strip())
                st.session_state.start_report_result = start_result
                
                # BACKEND STEP 1b: Run full 4-stage pipeline with Self-RAG & Expert Analyzer
                classify_result = backend_classify(st.session_state.description.strip())
                st.session_state.pipeline_result = classify_result
        return

    # ── Completion — STEP 3-6: Submit Report ───────────────────────────────────
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
    
    # Clear validation errors after handling (fresh state for next turn)
    st.session_state.validation_errors = {}


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
        st.markdown("### 🛡️ SYSTEM INFORMATION")
        st.caption("Cybercrime Report Generation and Filing")

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

        # Display validation errors if any
        if st.session_state.validation_errors:
            st.divider()
            st.warning("⚠️ **Validation Issues**", icon="⚠️")
            for field, error in st.session_state.validation_errors.items():
                st.caption(f"**{field}**: {error}")

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
            pr = st.session_state.pipeline_result
            
            # Display 4-stage pipeline
            with st.expander("🔬 4-Stage Pipeline"):
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
            
            # Display Self-RAG Validation
            self_rag = pr.get("self_rag_validation", {})
            if self_rag:
                with st.expander("✅ Self-RAG Validation"):
                    passed = self_rag.get("checkpoints_passed", 0)
                    total = self_rag.get("total_checkpoints", 5)
                    st.progress(passed / total if total > 0 else 0)
                    st.caption(f"Checkpoints: {passed}/{total}")
                    if self_rag.get("checkpoint_details"):
                        for detail in self_rag["checkpoint_details"]:
                            st.caption(f"• {detail}")
                    if self_rag.get("adjusted_confidence"):
                        st.metric("Adjusted Confidence", f"{self_rag['adjusted_confidence']:.1%}")
                    if self_rag.get("recommendation"):
                        st.info(f"Recommendation: {self_rag['recommendation']}")
            
            # Display Expert Flagging
            expert = pr.get("expert_flagging", {})
            if expert and expert.get("flagged"):
                with st.expander("⚠️ Expert Flagging"):
                    st.warning(f"Flagged: {expert.get('flag_reason')}")
                    st.caption(f"Severity: {expert.get('severity')}")

        st.divider()
        if st.button("🔄 START NEW CASE", use_container_width=True):
            reset()
            st.rerun()


# ── Chat + report ─────────────────────────────────────────────────────────────

def render_chat():
    for msg in st.session_state.messages:
        with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
            st.markdown(msg["content"])

            meta = msg.get("meta", {})

            # Display validation error if present
            if meta.get("validation_error"):
                st.warning(meta["validation_error"], icon="⚠️")

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
    st.markdown("## 📋 Incident Report")

    ct = st.session_state.crime_type or "unknown"
    c1, c2, c3 = st.columns(3)
    c1.metric("Crime Type", f"{CRIME_EMOJI.get(ct,'')} {ct.replace('_',' ').title()}")
    c2.metric("Confidence",  f"{int(st.session_state.confidence * 100)}%")
    schema = CRIME_SCHEMAS.get(ct, [])
    c3.metric("Fields Filled", f"{len(st.session_state.filled_schema)}/{len(schema)}")

    tabs = st.tabs(["📄 Formatted Report", "🔗 Correlation", "🔬 Pipeline", "📦 Raw Data"])
    
    with tabs[0]:
        st.markdown("### Official Complaint Report")
        
        # Prepare data for template
        report_data = {
            **st.session_state.filled_schema,
            "case_id": st.session_state.case_id,
            "report_date": st.session_state.messages[-1].get("meta", {}).get("timestamp", "N/A") if st.session_state.messages else "N/A",
        }
        
        # Generate formatted report using crime-specific template
        formatted_report = generate_formatted_report(ct, report_data)
        
        # Display the formatted report
        st.markdown(formatted_report)
        
        # Download button for formatted report
        st.download_button(
            "⬇️ Download Formatted Report",
            data=formatted_report,
            file_name=f"Complaint_Report_{st.session_state.case_id}_{ct}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # === CORRELATION ANALYSIS ===
    with tabs[1]:
        st.markdown("### Correlation Analysis")
        corr = report.get("correlation_analysis")
        if corr and isinstance(corr, dict):
            status = corr.get("status", "no_correlation")
            if status != "no_correlation":
                score = corr.get("correlation_score", 0)
                st.metric("Correlation Score", f"{score:.2f}")
                
                if corr.get("related_cases"):
                    st.warning("⚠️ Related Cases Found:")
                    for case in corr["related_cases"]:
                        st.write(f"• Case {case.get('case_id')}: {case.get('description')[:80]}...")
                
                if corr.get("found_contacts"):
                    st.info("🔗 Known Contacts Matched:")
                    for contact in corr["found_contacts"]:
                        st.write(f"• **{contact.get('contact_type')}**: {contact.get('contact_value')}")
                
                if corr.get("pattern_matches"):
                    st.success("📊 Pattern Matches:")
                    for pattern in corr["pattern_matches"]:
                        st.write(f"• Pattern: {pattern.get('pattern_type')} (confidence: {pattern.get('confidence', 0):.2f})")
                
                if corr.get("recommendation"):
                    st.info(f"**Recommendation**: {corr['recommendation']}")
            else:
                st.info("✅ No correlations found with existing cases")
        else:
            st.info("📊 Correlation analysis pending or not available")

    # === PIPELINE DETAILS ===
    with tabs[2]:
        st.markdown("### Classification Pipeline")
        if st.session_state.pipeline_result:
            pr = st.session_state.pipeline_result
            
            # 4-Stage results
            st.markdown("**4-Stage Classification Pipeline**")
            for sid, skey, lbl, color in [
                (1,"stage1_semantic_router","Semantic Router","🟢"),
                (2,"stage2_hierarchical_classifier","Hierarchical Classifier","🔵"),
                (3,"stage3_pattern_matcher","Pattern Matcher","🟡"),
                (4,"stage4_rag_retriever","RAG Retriever","🟣"),
            ]:
                s = pr.get("stages", {}).get(skey, {})
                if s:
                    st.markdown(f"##### {color} Stage {sid}: {lbl}")
                    st.json(s)
            
            # Self-RAG Validation
            if pr.get("self_rag_validation"):
                st.markdown("**Self-RAG Validation**")
                st.json(pr["self_rag_validation"])
            
            # Expert Flagging
            if pr.get("expert_flagging"):
                st.markdown("**Expert Analyzer**")
                st.json(pr["expert_flagging"])
        else:
            st.info("Pipeline results not yet available")

    # === RAW DATA ===
    with tabs[3]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Collected Schema**")
            st.json(st.session_state.filled_schema)
        with c2:
            st.markdown("**Full Report**")
            st.json(report)

    st.divider()
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "⬇️ Download Complete Report (JSON)",
            data=json.dumps({
                "case_id":              st.session_state.case_id,
                "crime_type":           ct,
                "confidence":           st.session_state.confidence,
                "filled_schema":        st.session_state.filled_schema,
                "report":               report.get("report_data", {}),
                "correlation_analysis": report.get("correlation_analysis"),
                "pipeline_result":      st.session_state.pipeline_result,
            }, indent=2, default=str),
            file_name=f"CS3299:Capstone_Project_report_{st.session_state.case_id}.json",
            mime="application/json",
            use_container_width=True,
        )
    
    with col2:
        # Generate formatted report for TXT download
        report_data = {
            **st.session_state.filled_schema,
            "case_id": st.session_state.case_id,
            "report_date": st.session_state.messages[-1].get("meta", {}).get("timestamp", "N/A") if st.session_state.messages else "N/A",
        }
        formatted_report = generate_formatted_report(ct, report_data)
        
        st.download_button(
            "⬇️ Download Official Complaint (TXT)",
            data=formatted_report,
            file_name=f"Complaint_Report_{st.session_state.case_id}_{ct}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="CS3299:Capstone_Project — Cybercrime Reporter",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_state()
    render_sidebar()

    st.title("🛡️ CYBERCRIME REPORT GENERATION SYSTEM")
    st.caption(
        "Automated incident classification and report documentation system. "
        "For official cybercrime complaint filing with law enforcement."
    )

    if not st.session_state.messages:
        add_message(
            "assistant",
            "**CYBERCRIME REPORTING SYSTEM**\n\n"
            "Please provide a detailed description of the cybercrime incident. "
            "Include all relevant information such as dates, times, amounts, individuals involved, "
            "and any communications or evidence you possess."
        )

    render_chat()
    render_report()

    if st.session_state.phase != "done":
        user_input = st.chat_input("Enter incident details or response…")
        if user_input and user_input.strip():
            with st.spinner("Processing report information…"):
                handle_user_turn(user_input.strip())
            st.rerun()
    else:
        st.success("✅ CASE REPORT COMPLETED\n\nThe incident report has been generated and is ready for filing. Use **🔄 START NEW CASE** in the sidebar to process another incident.")


if __name__ == "__main__":
    main()
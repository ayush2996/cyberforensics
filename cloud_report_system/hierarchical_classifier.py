import streamlit as st
import anthropic
import random
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cyber Crime FIR Classifier",
    page_icon="🔵",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Share Tech Mono', 'Courier New', monospace !important;
    background-color: #0a0c10 !important;
    color: #c9d1d9 !important;
}

.stApp { background-color: #0a0c10 !important; }

/* Header banner */
.fir-header {
    background: #0d1117;
    border: 1px solid #1f6feb;
    border-left: 4px solid #1f6feb;
    padding: 14px 20px;
    margin-bottom: 20px;
}
.fir-header h2 { color: #e6edf3; margin: 0; font-size: 15px; letter-spacing: 3px; }
.fir-header p  { color: #484f58; margin: 4px 0 0; font-size: 10px; letter-spacing: 2px; }
.fir-number    { color: #1f6feb; font-size: 12px; }

/* Chat bubbles */
.msg-sys {
    text-align: center;
    font-size: 10px;
    letter-spacing: 2px;
    color: #30363d;
    border-top: 1px solid #161b22;
    border-bottom: 1px solid #161b22;
    padding: 5px 0;
    margin: 6px 0;
}
.msg-ai {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin: 8px 0;
}
.badge-ai {
    background: #1f6feb;
    color: #fff;
    font-size: 9px;
    font-weight: 700;
    padding: 5px 7px;
    min-width: 34px;
    text-align: center;
    flex-shrink: 0;
    letter-spacing: 1px;
    margin-top: 2px;
}
.bubble-ai {
    background: #010409;
    border: 1px solid #21262d;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.75;
    white-space: pre-wrap;
    flex: 1;
    color: #e6edf3;
}
.bubble-ai.final { border-color: #238636; }

.msg-user {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    justify-content: flex-end;
    margin: 8px 0;
}
.badge-ofc {
    background: #161b22;
    color: #8b949e;
    font-size: 9px;
    font-weight: 700;
    padding: 5px 7px;
    min-width: 34px;
    text-align: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.bubble-user {
    background: #0d1117;
    border: 1px solid #1f6feb;
    padding: 10px 14px;
    font-size: 13px;
    line-height: 1.75;
    white-space: pre-wrap;
    max-width: 78%;
    color: #e6edf3;
}

/* Result card */
.result-card {
    background: #0d1117;
    border: 1px solid #238636;
    padding: 20px 24px;
    margin-top: 12px;
}
.result-label { font-size: 10px; color: #484f58; letter-spacing: 2px; margin-bottom: 4px; }
.result-value { font-size: 13px; color: #e6edf3; margin-bottom: 14px; }
.result-crime { font-size: 18px; color: #3fb950; font-weight: 700; letter-spacing: 2px; }
.result-header { font-size: 10px; letter-spacing: 3px; color: #3fb950; margin-bottom: 16px; }

/* Input overrides */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #010409 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 0 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1f6feb !important;
    box-shadow: none !important;
}

/* Label styling */
.stTextInput label, .stTextArea label {
    color: #8b949e !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Buttons */
.stButton > button {
    background-color: #1f6feb !important;
    color: #fff !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    font-weight: 700 !important;
    padding: 10px 22px !important;
}
.stButton > button:hover { background-color: #388bfd !important; }
.stButton > button:disabled {
    background-color: #161b22 !important;
    color: #484f58 !important;
}

/* Divider */
hr { border-color: #21262d !important; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "fir_number" not in st.session_state:
    st.session_state.fir_number = f"CYB/{datetime.now().year}/{random.randint(1000,9999)}"
if "stage" not in st.session_state:
    st.session_state.stage = "form"       # form | chat | result
if "messages" not in st.session_state:
    st.session_state.messages = []        # display messages [{role, text, final}]
if "api_history" not in st.session_state:
    st.session_state.api_history = []     # raw anthropic message list
if "final_crime" not in st.session_state:
    st.session_state.final_crime = None
if "complainant" not in st.session_state:
    st.session_state.complainant = ""
if "incident_date" not in st.session_state:
    st.session_state.incident_date = ""
if "incident_brief" not in st.session_state:
    st.session_state.incident_brief = ""

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a cyber crime classification AI integrated into a Police FIR (First Information Report) system. You are speaking DIRECTLY to a police officer.

TONE RULES — STRICTLY FOLLOW:
- Formal, terse, authoritative. Zero sympathy or emotional language.
- Use terms like: "Noted.", "Recorded.", "Proceeding.", "State the...", "Confirm...", "Classification indicates...", "On record."
- NEVER say "I'm sorry", "unfortunately", "I understand", "I appreciate", or any empathetic phrases.
- Speak like a senior crime analyst briefing an investigating officer.
- Keep responses short and precise — 2 to 4 lines maximum per turn.

YOUR TASK:
Classify the cyber crime by asking the officer short, direct clarifying questions ONE AT A TIME. 
Progress through:
1. Broad category — Financial / Personal-Harassment / Technical-Infrastructure
2. Specific sub-type
3. Final offence determination

When you have sufficient information, end your message with this line EXACTLY:
FINAL_CLASSIFICATION: [OFFENCE TYPE IN CAPS]

Valid offence types include (but not limited to):
FRAUD – INVESTMENT/CRYPTO, FRAUD – WIRE TRANSFER, FRAUD – MERCHANT, PHISHING, IDENTITY THEFT,
HACKING – ACCOUNT TAKEOVER, RANSOMWARE – PERSONAL, RANSOMWARE – BUSINESS, EXTORTION,
DATA BREACH – PERSONAL, DATA BREACH – ORGANISATION, MALWARE, DDoS, CYBERBULLYING, SPAM

Begin by acknowledging the incident and asking your first classification question."""

# ── Anthropic client ──────────────────────────────────────────────────────────
client = anthropic.Anthropic()

def call_claude(api_history):
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=api_history,
    )
    return response.content[0].text.strip()

def extract_final(text):
    import re
    m = re.search(r"FINAL_CLASSIFICATION:\s*(.+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None

def clean_display(text):
    import re
    return re.sub(r"FINAL_CLASSIFICATION:.*", "", text, flags=re.IGNORECASE).strip()

# ── Render chat history ───────────────────────────────────────────────────────
def render_messages():
    for m in st.session_state.messages:
        if m["role"] == "system":
            st.markdown(f'<div class="msg-sys">{m["text"]}</div>', unsafe_allow_html=True)
        elif m["role"] == "assistant":
            cls = "bubble-ai final" if m.get("final") else "bubble-ai"
            st.markdown(f"""
            <div class="msg-ai">
                <div class="badge-ai">SYS</div>
                <div class="{cls}">{m["text"]}</div>
            </div>""", unsafe_allow_html=True)
        elif m["role"] == "user":
            st.markdown(f"""
            <div class="msg-user">
                <div class="bubble-user">{m["text"]}</div>
                <div class="badge-ofc">OFC</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="fir-header">
    <h2>⚑ CYBER CRIME FIR CLASSIFICATION SYSTEM</h2>
    <p>NATIONAL CYBER CRIME REPORTING PORTAL &nbsp;·&nbsp; RESTRICTED ACCESS &nbsp;·&nbsp;
    FIR No: <span class="fir-number">{st.session_state.fir_number}</span> &nbsp;·&nbsp;
    {datetime.now().strftime("%d %b %Y")}</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STAGE: FORM
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "form":
    st.markdown("**◼ ENTER FIR DETAILS**", unsafe_allow_html=False)
    st.markdown("---")

    complainant = st.text_input(
        "Reporting Officer / Designation",
        placeholder="e.g. SI Ramesh Kumar, PS Kotwali",
        key="inp_complainant"
    )
    incident_date = st.text_input(
        "Date of Incident",
        placeholder="DD/MM/YYYY",
        key="inp_date"
    )
    incident_brief = st.text_area(
        "Incident Brief",
        placeholder="State the facts as reported in the FIR...",
        height=140,
        key="inp_brief"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("▶  BEGIN CLASSIFICATION", disabled=not (complainant.strip() and incident_brief.strip())):
        st.session_state.complainant = complainant.strip()
        st.session_state.incident_date = incident_date.strip()
        st.session_state.incident_brief = incident_brief.strip()

        # Build first message
        first_msg = (
            f"Reporting Officer: {st.session_state.complainant}\n"
            f"Date of Incident: {st.session_state.incident_date or 'Not specified'}\n"
            f"Incident Brief: {st.session_state.incident_brief}\n\n"
            "Begin classification."
        )

        st.session_state.api_history = [{"role": "user", "content": first_msg}]
        st.session_state.messages = [
            {"role": "system",    "text": f"FIR No. {st.session_state.fir_number} — Classification Session Initiated"},
            {"role": "user",      "text": st.session_state.incident_brief},
        ]

        with st.spinner(""):
            try:
                reply = call_claude(st.session_state.api_history)
                crime = extract_final(reply)
                display = clean_display(reply)
                st.session_state.api_history.append({"role": "assistant", "content": reply})
                st.session_state.messages.append({
                    "role": "assistant", "text": display, "final": bool(crime)
                })
                if crime:
                    st.session_state.final_crime = crime
                    st.session_state.stage = "result"
                else:
                    st.session_state.stage = "chat"
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "text": f"System error: {e}\nRetry or contact technical support."
                })
                st.session_state.stage = "chat"

        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE: CHAT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "chat":
    render_messages()
    st.markdown("---")

    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Officer Response",
                placeholder="Respond to classification query...",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("SEND")

    if submitted and user_input.strip():
        txt = user_input.strip()
        st.session_state.messages.append({"role": "user", "text": txt})
        st.session_state.api_history.append({"role": "user", "content": txt})

        with st.spinner(""):
            try:
                reply = call_claude(st.session_state.api_history)
                crime = extract_final(reply)
                display = clean_display(reply)
                st.session_state.api_history.append({"role": "assistant", "content": reply})
                st.session_state.messages.append({
                    "role": "assistant", "text": display, "final": bool(crime)
                })
                if crime:
                    st.session_state.final_crime = crime
                    st.session_state.stage = "result"
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "text": f"System error: {e}"
                })

        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE: RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "result":
    render_messages()

    st.markdown(f"""
    <div class="result-card">
        <div class="result-header">◼ CLASSIFICATION RECORD — FIR {st.session_state.fir_number}</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
            <div>
                <div class="result-label">REPORTING OFFICER</div>
                <div class="result-value">{st.session_state.complainant}</div>
            </div>
            <div>
                <div class="result-label">DATE OF INCIDENT</div>
                <div class="result-value">{st.session_state.incident_date or "Not specified"}</div>
            </div>
            <div style="grid-column:span 2">
                <div class="result-label">OFFENCE TYPE — FINAL CLASSIFICATION</div>
                <div class="result-crime">{st.session_state.final_crime}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("◀  FILE NEW FIR"):
        for key in ["stage","messages","api_history","final_crime","complainant","incident_date","incident_brief","fir_number"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
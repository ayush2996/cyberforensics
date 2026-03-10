# 🛡️ CyberGuard AI Frontend - User & Developer Guide

## Overview

**CyberGuard AI** is a modern, ChatGPT-like frontend for the cyber crime reporting system. It provides an intuitive multi-layer interface that guides users through the crime classification and reporting process.

### Key Features

✅ **Chat-Based Interface** - Conversational, user-friendly interaction  
✅ **Intelligent Agent Behavior** - AI guides you through the process  
✅ **Real-Time Classification** - Analyzes incidents on-the-fly  
✅ **Context-Aware Questions** - Asks targeted questions based on crime type  
✅ **Professional Reports** - Generates detailed JSON crime reports  
✅ **Report Export** - Download reports as JSON files  
✅ **Case Management** - Track case IDs and progress  
✅ **Multi-Layer Architecture** - Visual representation of system layers  

---

## Architecture Alignment

The frontend is designed to implement all four layers of the system:

### 1️⃣ **Interaction Layer**
- Chat interface with User/Victim
- Real-time message display
- Case ID tracking
- Session persistence

### 2️⃣ **Cognitive Layer**
- Semantic routing (determines question flow)
- Ambiguity detection & resolution
- Question generation
- Intent locking (prevents mid-process type changes)
- Dynamic schema selection
- Report generation

### 3️⃣ **Guardrails Layer**
- Confidence gates (shows confidence scores)
- Input validation
- Requirement checking

### 4️⃣ **Expert & Learning Loop**
- Report display with recommendations
- Correlation analysis visualization
- Investigation guidance

---

## Installation & Setup

### Prerequisites
```bash
# Python 3.8+
# Backend server running on http://localhost:8000
```

### Installation Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure backend is running
cd cloud_report_system
python main.py
# Should show: "Uvicorn running on http://0.0.0.0:8000"

# 3. In a new terminal, start the frontend
streamlit run ui.py
# Should open browser to http://localhost:8501
```

### Configuration

**API Endpoint** (edit in `ui.py`):
```python
API_BASE_URL = "http://localhost:8000/api/v1"
API_TIMEOUT = 30  # seconds
```

---

## User Workflow

### Step 1: Describe the Incident
```
User: "I received a suspicious email asking me to verify my banking credentials"
```
- Be as detailed as possible
- Include dates, affected systems, financial impact
- Mention any actions already taken

### Step 2: AI Classification
```
Agent: "I detected this as PHISHING (95% confidence)"
- Email-based credential theft
- Suspicious link/attachment present
- Possible multi-factor bypass attempt
```

### Step 3: Answer Clarifying Questions
```
Agent asks:
1. What is your email address?
2. Who was the sender?
3. Did you click any links?
4. Did you enter credentials?
... (5-7 questions total)
```

### Step 4: Review Generated Report
```
Report includes:
- Crime classification details
- All collected information
- Correlation with previous cases
- Investigation recommendations
- Confidence scores
```

### Step 5: Export & Share
```
Options:
- Copy report JSON
- Download as JSON file
- Share case ID with authorities
```

---

## UI Sections

### Main Chat Area (Left)
- **Messages**: Conversation history
- **Input Field**: User responses
- **Dynamic Rendering**: Shows questions/forms based on stage

### Progress Panel (Right)
- **Stage Indicator**: Shows workflow progress
- **Statistics**: Message count, confidence score
- **Quick Actions**: New report, clear chat, home

### Sidebar (Left)
- **API Status**: Check backend connectivity
- **Session Info**: Case ID and current stage
- **Help Section**: Quick reference guide
- **Architecture**: Visual system overview

---

## Message Types

### User Messages
- Initial incident description
- Question responses
- System commands

### Agent Messages
- Classification results
- Question prompts
- Report acknowledgments
- Recommendations

### System Messages
- Success confirmations
- Error notifications
- Status updates

---

## Supported Crime Types

| Crime Type | Description |
|-----------|-------------|
| 🎣 **Phishing** | Deceptive emails/messages to steal credentials |
| 🔐 **Ransomware** | Encryption of data with ransom demand |
| 📊 **Data Breach** | Unauthorized access to confidential data |
| 🆔 **Identity Theft** | Unauthorized use of someone's identity |
| 💰 **Fraud** | Deceptive financial schemes |
| 🦠 **Malware** | Malicious software infections |
| 🌐 **DDoS** | Distributed denial of service attacks |
| 🔓 **Hacking** | Unauthorized access to systems |
| 💣 **Extortion** | Threats demanding payment or action |
| 📧 **Spam** | Unwanted unsolicited messages |

---

## Report Structure

### Generated Report Includes:

1. **Metadata**
   - Case ID
   - Crime Type
   - Timestamp
   - Confidence Score

2. **Incident Details**
   - Crime-type specific fields
   - All user-provided information
   - Temporal data

3. **Analysis Results**
   - Classification reasoning
   - Risk assessment
   - Impact evaluation

4. **Correlations**
   - Linked previous cases
   - Pattern similarity scores
   - Cross-reference data

5. **Recommendations**
   - Investigation steps
   - Preventive measures
   - Authority escalation guidance

---

## Session State Management

### What's Tracked
- `messages`: Full conversation history
- `case_id`: Unique case identifier
- `crime_type`: Detected crime type
- `confidence`: Classification confidence (0-1)
- `current_stage`: Workflow stage
- `report_data`: Generated report JSON
- `messages_count`: Total message count

### Persistence
- Session data stored in Streamlit session state
- Cleared when user clicks "New Report" or "Clear Chat"
- Can be exported via report download

---

## Troubleshooting

### ❌ API Connection Error
```
Problem: "Cannot connect to API"
Solution:
1. Check backend is running: python main.py
2. Verify API URL: http://localhost:8000
3. Example in browser: http://localhost:8000/docs
```

### ❌ Questions Not Generated
```
Problem: "No questions appear after classification"
Solution:
1. Check backend logs for errors
2. Ensure crime type is supported
3. Try different incident description
```

### ❌ Report Generation Fails
```
Problem: "Error generating report"
Solution:
1. Answer all required questions
2. Check question responses are not empty
3. Verify backend database is accessible
```

### 🟡 Slow Performance
```
Solution:
1. Increase API_TIMEOUT in ui.py
2. Check backend server load
3. Clear chat history (older messages)
```

---

## Demo Scenarios

### Scenario 1: Phishing Attack
```
Input: "I got an email from my bank asking to verify my account. 
I clicked the link and entered my password. Now I'm worried."

Expected:
- Classification: PHISHING (95%+)
- Questions about: Email sender, link details, credentials used
- Report: Complete phishing incident with impact assessment
```

### Scenario 2: Ransomware Infection
```
Input: "All my files got encrypted with .locked extension. 
There's a note saying I need to pay $5000 in Bitcoin."

Expected:
- Classification: RANSOMWARE (98%+)
- Questions about: Ransom amount, affected systems, backups
- Report: Ransomware infrastructure & recovery recommendations
```

### Scenario 3: Data Breach
```
Input: "We just discovered that customer data was accessed 
from our database. About 50,000 records with names and emails."

Expected:
- Classification: DATA_BREACH (95%+)
- Questions about: Organization, breach date, notification status
- Report: Breach analysis with regulatory compliance guidance
```

---

## API Integration Details

### Endpoints Used

#### 1. Start Report (Classification)
```
POST /api/v1/start-report
Request: {"description": "incident description"}
Response: {"case_id", "detected_types", "recommendation", "confidence"}
```

#### 2. Get Questions
```
POST /api/v1/get-questions
Request: {"description", "crime_type"}
Response: {"questions": ["Q1", "Q2", ...]}
```

#### 3. Submit Report
```
POST /api/v1/submit-report
Request: {"case_id", "responses": {0: "answer1", 1: "answer2", ...}}
Response: {"report", "correlated_cases", "recommendations"}
```

#### 4. Health Check
```
GET /api/v1/health
Response: {"status": "healthy", "features": [...]}
```

---

## Customization Guide

### Change Color Scheme
Edit the CSS in `render_header()`:
```python
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(90deg, #4f46e5, #6366f1);  # Change these colors
    }
</style>
""")
```

### Modify Message Display
Edit `render_chat_history()`:
```python
def render_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            # Customize display here
```

### Add New Features
- Extend `main()` function
- Add new sidebar sections
- Create new rendering functions
- Call new API endpoints

---

## Performance Tips

1. **Cache API Responses**: Use `@st.cache_data` for static data
2. **Optimize Rendering**: Reuse containers instead of recreating
3. **Lazy Load Reports**: Only render when needed
4. **Clear Old Messages**: Periodically archive old cases

---

## Support & Documentation

- **Backend Docs**: http://localhost:8000/docs
- **Architecture**: See `ARCHITECTURE.md`
- **API Guide**: See `API_TESTING_GUIDE.md`
- **Quick Start**: See `QUICKSTART.md`

---

## Version Info

- **Frontend**: v1.0.0 (Modern Streamlit)
- **Backend**: v2.0.0 (Enhanced Cyber Crime System)
- **Python**: 3.8+
- **Streamlit**: 1.31.0+

---

## Workflow Diagram

```
User Input
    ↓
Classify Crime (Semantic Router)
    ↓
Ask Clarifying Questions (Dynamic Template)
    ↓
Validate Responses (Data Validator)
    ↓
Generate Report (Draft Report Generator)
    ↓
Check Confidence Gate (Guardrails)
    ↓
Correlate with Cases (Expert Loop)
    ↓
Display & Export Report
```

---

**Last Updated**: 2026-03-09  
**Status**: 🟢 Production Ready

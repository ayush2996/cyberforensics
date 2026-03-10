# Enhanced Cyber Crime Reporting System - Implementation Guide

## System Overview

This enhanced system implements a comprehensive cyber crime reporting platform with the following capabilities:

### ✨ Key Features

1. **Crime Type Selection & Classification**
   - AI-powered automatic detection of 10 different cyber crime types
   - User-friendly selection interface
   - Confidence scoring for classifications

2. **Interactive Questioning System**
   - Crime-type-specific clarifying questions
   - Intelligent conversation flow
   - Tailored prompts for each crime category

3. **JSON Schema-Based Reporting**
   - Structured reports for each crime type
   - Professional report generation
   - Validated data fields

4. **Correlation Detection & Analysis**
   - Automatic correlation with previous cases
   - Pattern matching (crime patterns, caller numbers, contact info)
   - Investigation recommendations
   - Case linking for organized crime networks

---

## Architecture Overview

### Supported Crime Types

```
1. PHISHING - Email/message credential theft
2. RANSOMWARE - Data encryption attacks  
3. DATA_BREACH - Unauthorized data access
4. IDENTITY_THEFT - Identity misuse
5. FRAUD - Financial deception
6. MALWARE - Malicious software infections
7. DDoS - Service denial attacks
8. HACKING - System intrusion
9. EXTORTION - Blackmail/threats
10. SPAM - Unsolicited messages
```

### File Structure

```
cloud_report_system/
├── models.py                 # Pydantic models & crime schemas
├── prompts.py               # LLM prompts for all operations
├── crime_classifier.py      # Crime type detection engine
├── correlation_engine.py    # Correlation & pattern matching
├── workflow.py              # Main workflow orchestration
├── main.py                  # FastAPI endpoints
├── llm_manager.py          # Groq LLM integration
├── embeddings_manager.py   # Cohere embeddings
├── config.py               # Configuration
└── vector_storage.py       # ChromaDB vector store
```

---

## API Endpoints

### 1. Start Report (Crime Type Classification)

**Endpoint:** `POST /api/v1/start-report`

**Request:**
```json
{
  "description": "I received a suspicious email asking me to click a link and enter my password"
}
```

**Response:**
```json
{
  "status": "crime_type_selected",
  "detected_types": ["phishing"],
  "recommendation": "phishing",
  "confidence": 0.95,
  "message": "Classification based on incident description",
  "case_id": "abc12345"
}
```

---

### 2. Get Clarifying Questions

**Endpoint:** `POST /api/v1/get-questions`

**Query Parameters:**
- `description`: Original incident description
- `crime_type`: Detected crime type (e.g., "phishing")
- `case_id`: Case identifier from start-report

**Response:**
```json
{
  "status": "needs_clarification",
  "questions": [
    "What is your email address?",
    "What is the sender's email address?",
    "What was the subject line of the email?",
    "Did you click any links in the email?",
    "Did you enter any credentials?"
  ],
  "confidence": 0.8,
  "crime_type": "phishing"
}
```

---

### 3. Submit Report & Generate Report

**Endpoint:** `POST /api/v1/submit-report`

**Request:**
```json
{
  "user_input": "I received a suspicious email...",
  "crime_type": "phishing",
  "case_id": "abc12345",
  "answers": {
    "What is your email address?": "john@example.com",
    "What is the sender's email address?": "fake@malicious.com",
    "What was the subject line?": "Urgent: Verify Your Account",
    "Did you click any links?": "Yes, I clicked the verification link",
    "Did you enter credentials?": "Yes, I entered my password"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "report_data": {
    "crime_type": "phishing",
    "victim_email": "john@example.com",
    "sender_email": "fake@malicious.com",
    "email_subject": "Urgent: Verify Your Account",
    "link_clicked": true,
    "credentials_entered": true,
    "date_received": "2024-03-08T10:30:00",
    "action_taken": "Reported to provider and changed password",
    "financial_loss": 0.0
  },
  "crime_type": "phishing",
  "confidence": 0.9,
  "timestamp": "2024-03-08T15:45:30",
  "correlation_analysis": {
    "status": "correlated",
    "similar_cases": [...],
    "matching_patterns": ["same_attack_vector"],
    "matching_callers": ["fake@malicious.com"],
    "correlation_score": 0.75,
    "recommendation": "Similar phishing campaign detected. Recommend coordinated response.",
    "correlated_case_ids": ["case001", "case002"]
  }
}
```

---

### 4. Get Supported Crime Types

**Endpoint:** `GET /api/v1/crime-types`

**Response:**
```json
{
  "status": "success",
  "crime_types": [
    {
      "id": "phishing",
      "name": "Phishing",
      "description": "Deceptive emails or messages to steal credentials"
    },
    {
      "id": "ransomware",
      "name": "Ransomware",
      "description": "Encryption of data with ransom demands"
    }
    // ... more types
  ],
  "total": 10
}
```

---

## Workflow Flow Diagram

```
1. USER SUBMITS INCIDENT
   ↓
2. CRIME CLASSIFICATION
   - LLM analyzes description
   - Detects crime type with confidence score
   - Returns: classification, type, confidence
   ↓
3. INTERACTIVE QUESTIONS
   - System generates crime-type-specific questions
   - 5-7 targeted questions
   - Each question focuses on important details
   ↓
4. USER ANSWERS QUESTIONS
   - User provides detailed responses
   - Answers fill the JSON schema fields
   ↓
5. REPORT GENERATION
   - LLM generates professional JSON report
   - All fields properly filled
   - Formatted per crime type
   ↓
6. CORRELATION ANALYSIS
   - System searches for related cases
   - Matches on:
     * Email addresses / phone numbers
     * Crime patterns & attack vectors
     * Similar timeframes & amounts
     * Geographic/temporal patterns
   ↓
7. CASE REGISTRATION
   - Report indexed in correlation database
   - Available for future pattern matching
   ↓
8. RESPONSE DELIVERED
   - Complete structured report
   - Correlation findings
   - Investigation recommendations
```

---

## Crime Type Specific Schemas

### Example: PhishingReport Schema

```json
{
  "crime_type": "phishing",
  "victim_email": "string",
  "sender_email": "string",
  "email_subject": "string",
  "email_body": "string",
  "link_clicked": boolean,
  "suspicious_links": ["string"],
  "credentials_entered": boolean,
  "credentials_lost": ["string"],
  "date_received": "datetime",
  "action_taken": "string",
  "financial_loss": 0.0
}
```

Each crime type has its own specific schema with relevant fields for that crime category.

---

## Correlation Detection Example

### Pattern Matching Scenarios

**Scenario 1: Matching Email Addresses**
```
Current Case: Phishing attempt from "admin@company.com"
Previous Cases: 3 other phishing cases from same email
Result: HIGH CORRELATION - Same attacker group identified
```

**Scenario 2: Similar Attack Vectors**
```
Current Case: Ransomware attack via spear phishing
Previous Cases: 2 ransomware cases with identical attack method
Result: MODERATE CORRELATION - Same ransomware family likely
```

**Scenario 3: Temporal Pattern**
```
Current Case: Breach on March 7, 2024
Previous Cases: Similar breaches on March 1, March 8
Result: MODERATE CORRELATION - Sustained campaign detected
```

**Scenario 4: No Correlation**
```
Current Case: Unique attack with no matching indicators
Previous Cases: No matching emails, patterns, or timeframes
Result: NO CORRELATION - Standalone incident
```

---

## Configuration

### Environment Variables (.env)

```bash
GROQ_API_KEY=your_groq_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
```

### config.py Settings

```python
LLM_MODEL = "llama-3.1-70b-versatile"  # Groq model
EMBEDDING_MODEL = "embed-english-light-v3.0"  # Cohere model
MAX_INPUT_LENGTH = 5000
MAX_OUTPUT_TOKENS = 2000
TEMPERATURE = 0.7
```

---

## Usage Examples

### Complete Workflow Example

```python
# 1. Start report
response = await workflow.process_incident(
    "I received a suspicious email asking me to verify my account"
)
case_id = response["case_id"]
crime_type = response["recommendation"]

# 2. Get questions
questions = await workflow.generate_questions(
    description,
    CrimeType(crime_type)
)

# 3. Submit answers and get report
report = await workflow.submit_answers_and_generate_report(
    description=description,
    crime_type_str=crime_type,
    answers={
        "What is your email?": "john@example.com",
        "Sender email?": "fake@malicious.com",
        # ... more answers
    },
    case_id=case_id
)

# Report now contains:
# - Structured report data (JSON)
# - Crime type classification
# - Confidence score
# - Correlation analysis with recommendations
```

---

## Running the System

### Start API Server

```bash
cd cloud_report_system
python main.py
```

Output:
```
======================================================================
🚀 ENHANCED CYBER CRIME REPORT SYSTEM
======================================================================

✨ Features:
   ✓ Crime Type Classification
   ✓ Interactive Questioning
   ✓ JSON Schema Reports
   ✓ Correlation Detection
   ✓ AI-Powered Analysis

📍 API Server: http://localhost:8000
📚 Documentation: http://localhost:8000/docs
🔧 Admin: http://localhost:8000/redoc

======================================================================
```

### Access Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Key Improvements & Architecture

### 1. Crime Type Auto-Detection
- Analyzes incident description
- Uses LLM for intelligent classification
- Provides confidence scores
- Fallback keyword-based matching

### 2. Dynamic Question Generation
- Tailored per crime type
- Focuses on critical information
- 5-7 targeted questions
- Guides user through incident details

### 3. Structured Report Generation
- Crime-type-specific JSON schemas
- Professional formatting
- All required fields populated
- Validation before return

### 4. Correlation Engine
- Pattern-based matching
- Contact/email tracking
- Temporal pattern detection
- Case database management
- Investigation recommendations

### 5. Multi-Layer Processing
- LLM for classification & questions
- Embeddings for semantic search
- Vector DB for case storage
- Pattern matching for correlations
- JSON validation for reports

---

## Future Enhancements

1. **Advanced Analytics**
   - Machine learning models for pattern detection
   - Heatmaps of attack patterns
   - Predictive analytics

2. **Integration Capabilities**
   - Database integration for persistent storage
   - API webhooks for external systems
   - Integration with LEA databases

3. **Enhanced Reporting**
   - PDF/Excel export options
   - Multi-language support
   - Custom report templates

4. **Collaboration Features**
   - Team investigation workflows
   - Comment & annotation system
   - Case assignment & tracking

5. **Security Enhancements**
   - End-to-end encryption
   - Role-based access control
   - Audit logging

---

## Troubleshooting

### Issue: "Invalid crime type"
**Solution:** Ensure crime_type parameter matches one of the supported types (phishing, ransomware, etc.)

### Issue: "JSON parse error in report"
**Solution:** LLM may be returning malformed JSON. Try resubmitting or simplifying the incident description.

### Issue: "Correlation analysis timeout"
**Solution:** Database may be large. Consider archiving old cases or running correlation on shorter timeframe.

### Issue: "API rate limit exceeded"
**Solution:** Wait a few minutes before retrying. Consider implementing request queuing.

---

## Contact & Support

For issues, feature requests, or questions about the Enhanced Cyber Crime Reporting System, please contact the development team.

---

**Last Updated:** March 8, 2024  
**Version:** 2.0.0  
**System Status:** Production Ready ✅

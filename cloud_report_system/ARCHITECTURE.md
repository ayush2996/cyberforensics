# System Architecture Diagram - v3.0

## Complete System Overview with Data Validation and Professional Reporting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               STREAMLIT FRONTEND / POLICE INTERFACE                         │
│                           (ui.py)                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Features:                                                            │  │
│  │ • Professional formal interface for law enforcement                  │  │
│  │ • Chat-based incident data collection                               │  │
│  │ • Real-time field validation with error feedback                    │  │
│  │ • Crime-specific formatted report templates                         │  │
│  │ • Dual export (JSON + TXT official complaint form)                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              │ HTTP REST API
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI APPLICATION                                  │
│                           (main.py)                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ Endpoints:                                                           │  │
│  │ • POST /api/v1/start-report         → Crime classification         │  │
│  │ • POST /api/v1/classify-crime       → Direct classification        │  │
│  │ • POST /api/v1/get-questions        → Question generation          │  │
│  │ • POST /api/v1/submit-report        → Report generation            │  │
│  │ • GET  /api/v1/crime-types          → List types                  │  │
│  │ • GET  /api/v1/session/{id}         → Session info                │  │
│  │ • GET  /health                      → Health check                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──┬──────────────────┬──────────────────┬──────────────────┬──────────────┬─┘
   │                  │                  │                  │              │
   ▼                  ▼                  ▼                  ▼              ▼
┌────────────────┐┌──────────────────┐┌────────────────┐┌────────────────┐┌────────────────┐
│CRIME CLASSIFIER││FIELD VALIDATOR   ││ENHANCED        ││CORRELATION    ││REPORT TEMPLATE│
│                ││                  ││WORKFLOW        ││ENGINE         ││GENERATOR      │
├────────────────┤├──────────────────┤├────────────────┤├────────────────┤├────────────────┤
│classify_       ││validate_field()  ││process_        ││analyze_        ││generate_      │
│incident()      ││                  ││incident()      ││correlation()   ││formatted_     │
│                ││get_field_type()  ││                ││                ││report()       │
│crime_types     ││                  ││generate_       ││find_cases_by_  ││                │
│(10 types)      ││validate_email()  ││questions()     ││contact()       ││Templates:     │
│                ││validate_phone()  ││                ││                ││• Phishing     │
│fallback_       ││validate_date()   ││generate_       ││analyze_        ││• Fraud        │
│classification()││validate_amount() ││report()        ││patterns()      ││• Ransomware   │
│                ││validate_url()    ││                ││                ││• Malware      │
│get_crime_model││validate_text()   ││submit_answers_ ││case_database   ││• DDoS         │
│(crime_type)    ││                  ││and_generate    ││                ││• Hacking      │
│                ││VALIDATION        ││_report()       ││known_contacts  ││+ 4 more       │
│                ││RESULTS:          ││                ││                ││                │
│                ││✓ All fields      ││POLICY:         ││CASE STORAGE:   ││OUTPUT FORMATS:│
│                ││✓ Format checked  ││Reject invalid  ││Vector DB       ││• TXT (formal) │
│                ││✓ Type validated  ││Ask for correct ││Pattern DB      ││• JSON (data)  │
│                ││✓ Length limits   ││format again    ││Contact Index   ││• HTML (print) │
└────────────────┘└──────────────────┘└────────────────┘└────────────────┘└────────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │PROMPTS (FORMAL)  │
                  ├──────────────────┤
                  │• Classification  │
                  │  prompt (no chat)│
                  │• 10 Question     │
                  │  sets (direct)   │
                  │• Report gen      │
                  │  prompts         │
                  │• NO casual lang  │
                  │• Police-focused  │
                  └──────────────────┘

---

## Data Flow Sequence

```
┌──────────────┐
│ USER SUBMITS │
│  INCIDENT    │
│ DESCRIPTION  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 1. CRIME CLASSIFICATION                             │
│    → crime_classifier.classify_incident()           │
│    → Uses CRIME_TYPE_DETECTION_PROMPT               │
│    → Calls Groq LLM API                             │
│    ← Returns crime type + confidence score          │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 2. QUESTION GENERATION                              │
│    → workflow.generate_questions()                  │
│    → Select crime-specific prompt template          │
│    → Call Groq LLM with prompt                      │
│    ← Returns 5-7 JSON questions                     │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ USER ANSWERS │
│  QUESTIONS   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 3. REPORT GENERATION                                │
│    → workflow.generate_report()                     │
│    → Build incident summary with answers            │
│    → Call Groq LLM with report prompt               │
│    → Parse JSON response                            │
│    ← Returns structured crime report                │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 4. CORRELATION ANALYSIS                             │
│    → correlation_engine.analyze_correlation()       │
│    → Extract searchable fields:                     │
│       • Emails, phone numbers                       │
│       • IP addresses, amounts                       │
│       • Keywords, attack vectors                    │
│    → Search case database:                          │
│       • Find exact contact matches                  │
│       • Find similar crime types                    │
│       • Find temporal patterns                      │
│    ← Returns correlation results + recommendations  │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 5. CASE REGISTRATION                                │
│    → correlation_engine.add_case_to_database()      │
│    → Store in vector database                       │
│    → Index contacts for future matching             │
│    → Update pattern database                        │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│ 6. RESPONSE DELIVERY                                │
│    Returns to client:                               │
│    • Crime type classification                      │
│    • Confidence score                               │
│    • Structured JSON report                         │
│    • Correlation analysis results                   │
│    • Investigation recommendations                  │
│    • Related case IDs                               │
└─────────────────────────────────────────────────────┘
```

---

## Component Interaction Diagram

```
                    ┌─────────────────┐
                    │   API Handler   │
                    │   (main.py)     │
                    └────────┬────────┘
                             │
                  ┌──────────┼──────────┐
                  ▼          ▼          ▼
            ┌─────────┐ ┌──────────┐ ┌─────────────┐
            │Classifier│ │Workflow  │ │Correlation  │
            │Engine    │ │Engine    │ │Engine       │
            └─────────┘ └──────────┘ └─────────────┘
                  │          │           │
                  └──────────┼───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐  ┌───────────┐
        │LLM       │   │Vector DB │  │ Data      │
        │Manager   │   │(ChromaDB)│  │ Models    │
        │(Groq)    │   │          │  │(Pydantic) │
        └──────────┘   └──────────┘  └───────────┘
              │              │
              └──────────────┼─────────────────┐
                             │                 │
                      ┌──────▼─────┐    ┌────▼──────┐
                      │Embeddings  │    │Vector     │
                      │(Cohere)    │    │Store Files│
                      └────────────┘    └───────────┘
```

---

## Crime Type Classification Decision Tree

```
                    INCIDENT DESCRIPTION
                           │
                           ▼
                    ┌─────────────────┐
                    │  Classify via   │
                    │  LLM (Groq)     │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
         PHISHING    RANSOMWARE     DATA BREACH
         (Email)     (Encryption)   (Unauthorized)
                │            │            │
                ├────────────┼────────────┤
                │            │            │
                ▼            ▼            ▼
         IDENTITY        FRAUD          MALWARE
         THEFT        (Financial)      (Infection)
                │            │            │
                ├────────────┼────────────┤
                │            │            │
                ▼            ▼            ▼
              DDoS         HACKING      EXTORTION
           (Denial)      (Intrusion)   (Threats)
                │            │
                └────────────┼────────────┐
                             │            │
                             ▼            ▼
                           SPAM      CONFIDENCE
                                     SCORE
```

---

## Report Schema Mapping

```
CRIME TYPE → SPECIFIC SCHEMA → JSON REPORT

PhishingReport
├── victim_email
├── sender_email
├── email_subject
├── email_body
├── link_clicked (bool)
├── suspicious_links []
├── credentials_entered (bool)
├── credentials_lost []
├── date_received
├── action_taken
└── financial_loss

RansomwareReport
├── affected_systems []
├── ransom_amount
├── currency
├── ransom_note
├── file_extensions_encrypted []
├── date_infection
├── ransomware_name
├── data_exfiltration (bool)
├── backups_available (bool)
└── ... (10 fields total)

DataBreachReport
├── organization_name
├── data_types []
├── records_affected
├── discovery_date
├── breach_date
├── attack_vector
├── notification_status (bool)
└── ... (9 fields total)

[SIMILAR STRUCTURE FOR 7 OTHER CRIME TYPES]
```

---

## Correlation Matching Algorithm

```
┌──────────────────────┐
│  CURRENT INCIDENT    │
└──────────┬───────────┘
           │
    ┌──────▼──────┐
    │Extract      │
    │Fields       │
    └──────┬──────┘
           │
    ┌──────▼──────────────────────┐
    │• Emails                      │
    │• Phone Numbers               │
    │• IP Addresses                │
    │• Amounts/Payment             │
    │• Attack Vector               │
    │• Timeframe                   │
    │• Crime Type                  │
    └──────┬──────────────────────┘
           │
    ┌──────▼───────────────────┐
    │ SEARCH DATABASE           │
    └──────┬────────────────────┘
           │
      ┌────┴────┬────────┬──────────┐
      ▼         ▼        ▼          ▼
    EMAIL   PHONE    BY TYPE   BY DATE
    MATCH   MATCH    & DATE    RANGE
      │       │        │        │
      └───────┴────────┴────────┘
             │
      ┌──────▼───────────┐
      │MATCHING CASES    │
      │  FOUND           │
      └──────┬───────────┘
             │
      ┌──────▼────────────────┐
      │ANALYZE PATTERNS:       │
      │• Same email = 0.3      │
      │• Same phone = 0.3      │
      │• Similar amount = 0.2  │
      │• Same vector = 0.25    │
      └──────┬────────────────┘
             │
      ┌──────▼─────────────────┐
      │CALCULATE SCORE          │
      │ (sum/case_count)        │
      └──────┬────────────────┘
             │
      ┌──────▼──────────────────┐
      │GENERATE                  │
      │RECOMMENDATION &          │
      │CORRELATED CASE IDS       │
      └──────────────────────────┘
```

---

## Database Schema (In-Memory for Now)

```
┌──────────────────────────────────────────┐
│  CASE DATABASE                            │
│  (In-Memory List)                         │
├──────────────────────────────────────────┤
│ [                                         │
│   {                                       │
│     "case_id": "case_001",               │
│     "date_reported": "2024-03-01T...",  │
│     "crime_type": "phishing",            │
│     "emails": ["attacker@evil.com"],    │
│     "phone_numbers": [],                 │
│     "amount": 0,                         │
│     "attack_vector": "spear_phishing",  │
│     "report_data": {...full report...}  │
│   },                                      │
│   {...more cases...}                     │
│ ]                                         │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  CONTACT INDEX                            │
│  (Hash Map for Quick Lookup)              │
├──────────────────────────────────────────┤
│ {                                         │
│   "attacker@evil.com": [                │
│     "case_001",                         │
│     "case_005",                         │
│     "case_012"                          │
│   ],                                      │
│   "fake-bank@phishing.net": [           │
│     "case_002",                         │
│     "case_007"                          │
│   ],                                      │
│   ...more contacts...                    │
│ }                                         │
└──────────────────────────────────────────┘
```

---

## Technology Stack

```
BACKEND FRAMEWORK
├── FastAPI (REST API)
├── Pydantic (Data Validation)
└── Uvicorn (ASGI Server)

NLP/LLM
├── Groq (LLM Provider - llama-3.1-70b)
├── Cohere (Embeddings API)
└── JSON Parser (Native)

DATABASE
├── ChromaDB (Vector Storage)
├── DuckDB (Embedded Database)
└── In-Memory Case Database

UTILITIES
├── Python 3.10+
├── AyncIO (Async Processing)
├── UUID (Case IDs)
└── DateTime (Timestamps)
```

---

## File Dependencies

```
main.py
├── workflow.py
├── models.py
├── crime_classifier.py
├── correlation_engine.py
├── llm_manager.py
└── config.py

workflow.py
├── crime_classifier.py
├── correlation_engine.py
├── models.py
├── prompts.py
└── llm_manager.py

crime_classifier.py
├── models.py
├── llm_manager.py
└── prompts.py

correlation_engine.py
├── models.py
└── llm_manager.py

llm_manager.py
├── config.py
└── groq (external)

config.py (standalone)

models.py (standalone)

prompts.py (standalone)
```

---

## Performance Considerations

```
OPERATION              COMPLEXITY    TIME ESTIMATE
──────────────────────────────────────────────────
Crime Classification   O(1)          1-2 seconds
Question Generation    O(1)          2-3 seconds
Report Generation      O(n)          3-5 seconds
Correlation Search     O(m)          1-2 seconds
Case Registration      O(1)          <100ms

WHERE:
n = number of fields in report
m = number of cases in database

TOTAL WORKFLOW TIME: 7-13 seconds
(Dominated by LLM API calls)
```

---

**Architecture Status:** ✅ Complete & Optimized  
**Version:** 2.0.0  
**Last Updated:** March 8, 2026

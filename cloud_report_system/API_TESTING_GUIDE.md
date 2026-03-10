# API Testing Guide - Enhanced Cyber Crime Reporting System

## Quick Start Testing

### 1. Test Crime Type Classification

Using `curl`:
```bash
curl -X POST "http://localhost:8000/api/v1/start-report" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I received a suspicious email asking me to click a link and verify my bank account password"
  }'
```

Using Python requests:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/start-report",
    json={
        "description": "I received a suspicious email asking me to click a link and verify my bank account password"
    }
)

print(response.json())
```

Expected Response:
```json
{
  "status": "crime_type_selected",
  "detected_types": ["phishing"],
  "recommendation": "phishing",
  "confidence": 0.95,
  "message": "Classification based on incident description",
  "case_id": "xyz789"
}
```

---

### 2. Get Clarifying Questions

Using the case ID from step 1:

```bash
curl -X POST "http://localhost:8000/api/v1/get-questions?description=I%20received%20a%20suspicious%20email...&crime_type=phishing&case_id=xyz789"
```

Using Python:
```python
response = requests.post(
    "http://localhost:8000/api/v1/get-questions",
    params={
        "description": "I received a suspicious email asking me to click a link and verify my bank account password",
        "crime_type": "phishing",
        "case_id": "xyz789"
    }
)

questions = response.json()["questions"]
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")
```

Expected Response:
```json
{
  "status": "needs_clarification",
  "questions": [
    "What is your email address?",
    "What is the sender's email address?",
    "What was the exact subject line of the email?",
    "Did you click on any links in the email?",
    "What happened after you clicked the link?",
    "Did you enter any credentials or personal information?",
    "When did you receive this email?"
  ],
  "confidence": 0.8,
  "crime_type": "phishing"
}
```

---

### 3. Submit Answers and Generate Report

Using the case ID and crime type:

```bash
curl -X POST "http://localhost:8000/api/v1/submit-report" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "I received a suspicious email asking me to click a link and verify my bank account password",
    "crime_type": "phishing",
    "case_id": "xyz789",
    "answers": {
      "What is your email address?": "john.doe@bank.com",
      "What is the sender'\''s email address?": "noreply@banksecurity.fake.com",
      "What was the exact subject line?": "URGENT: Verify Your Account Immediately",
      "Did you click on any links in the email?": "Yes, I clicked the verification link",
      "What happened after you clicked the link?": "A fake login page appeared",
      "Did you enter any credentials or personal information?": "Yes, I entered my username and password",
      "When did you receive this email?": "March 8, 2024 at 10:30 AM"
    }
  }'
```

Using Python:
```python
response = requests.post(
    "http://localhost:8000/api/v1/submit-report",
    json={
        "user_input": "I received a suspicious email...",
        "crime_type": "phishing",
        "case_id": "xyz789",
        "answers": {
            "What is your email address?": "john.doe@bank.com",
            "What is the sender's email address?": "noreply@banksecurity.fake.com",
            "What was the exact subject line?": "URGENT: Verify Your Account Immediately",
            "Did you click on any links in the email?": "Yes, I clicked the verification link",
            "What happened after you clicked the link?": "A fake login page appeared",
            "Did you enter any credentials or personal information?": "Yes, I entered my username and password",
            "When did you receive this email?": "March 8, 2024 at 10:30 AM"
        }
    }
)

report = response.json()
print(f"Status: {report['status']}")
print(f"Confidence: {report['confidence']}")
print(f"Report Data: {report['report_data']}")

if report['correlation_analysis']['status'] == 'correlated':
    print(f"Correlation Score: {report['correlation_analysis']['correlation_score']}")
    print(f"Recommendation: {report['correlation_analysis']['recommendation']}")
```

Expected Response:
```json
{
  "status": "success",
  "report_data": {
    "crime_type": "phishing",
    "victim_email": "john.doe@bank.com",
    "sender_email": "noreply@banksecurity.fake.com",
    "email_subject": "URGENT: Verify Your Account Immediately",
    "email_body": "[Not provided]",
    "link_clicked": true,
    "suspicious_links": ["https://banksecurity.fake.com/verify"],
    "credentials_entered": true,
    "credentials_lost": ["username", "password"],
    "date_received": "2024-03-08T10:30:00",
    "action_taken": "Reported to bank, changed password, enabled 2FA",
    "financial_loss": 0.0
  },
  "crime_type": "phishing",
  "confidence": 0.9,
  "timestamp": "2024-03-08T15:45:30.123456",
  "correlation_analysis": {
    "status": "correlated",
    "similar_cases": [
      {
        "case_id": "case_001",
        "crime_type": "phishing",
        "sender_email": "noreply@banksecurity.fake.com"
      }
    ],
    "matching_patterns": ["same_attack_vector", "similar_email_domain"],
    "matching_callers": ["noreply@banksecurity.fake.com"],
    "correlation_score": 0.85,
    "recommendation": "HIGH CORRELATION FOUND: Same sender email used in 3 previous phishing campaigns. Recommend immediate alert to financial institution and law enforcement.",
    "correlated_case_ids": ["case_001", "case_003", "case_007"]
  }
}
```

---

## Testing All Crime Types

### Test Ransomware Report

```bash
curl -X POST "http://localhost:8000/api/v1/start-report" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "All my files got encrypted and I see a message demanding money. The files have .locked extension and there is a note saying my data will be deleted in 72 hours if I dont pay $500 in Bitcoin"
  }'
```

### Test Data Breach Report

```bash
curl -X POST "http://localhost:8000/api/v1/start-report" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Our company discovered that someone accessed our customer database containing 50000 customer records. The attacker has demanded $100000 or they will sell the data"
  }'
```

### Test Identity Theft Report

```bash
curl -X POST "http://localhost:8000/api/v1/start-report" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I discovered that someone opened credit card accounts in my name and made purchases. I have $25000 in fraudulent charges"
  }'
```

---

## Testing Correlation Detection

### Scenario 1: Test Matching Email Addresses

Submit two phishing reports with the same sender email:

**Report 1:**
```json
{
  "user_input": "Phishing email from fake@attacker.com",
  "crime_type": "phishing",
  "case_id": "case_A",
  "answers": {
    "What is the sender's email address?": "fake@attacker.com",
    ...
  }
}
```

**Report 2:**
```json
{
  "user_input": "Another phishing from same sender",
  "crime_type": "phishing",
  "case_id": "case_B",
  "answers": {
    "What is the sender's email address?": "fake@attacker.com",
    ...
  }
}
```

**Expected Result:** Case B will show correlation with Case A due to matching email address.

---

## Testing via Swagger UI

1. Open browser: http://localhost:8000/docs
2. Click on `/api/v1/start-report` endpoint
3. Click "Try it out"
4. Enter test description
5. Click "Execute"
6. View response
7. Use the case_id for subsequent endpoints

---

## Complete End-to-End Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    # Step 1: Classify incident
    print("1️⃣ Step 1: Classifying incident...")
    response = requests.post(
        f"{BASE_URL}/api/v1/start-report",
        json={"description": "I received a suspicious email asking me to verify my account"}
    )
    result = response.json()
    case_id = result["case_id"]
    crime_type = result["recommendation"]
    print(f"✓ Detected: {crime_type} (Confidence: {result['confidence']})")
    
    # Step 2: Get questions
    print("\n2️⃣ Step 2: Generating questions...")
    response = requests.post(
        f"{BASE_URL}/api/v1/get-questions",
        params={
            "description": result["message"],
            "crime_type": crime_type,
            "case_id": case_id
        }
    )
    questions = response.json()["questions"]
    print(f"✓ Generated {len(questions)} questions")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    # Step 3: Submit answers
    print("\n3️⃣ Step 3: Submitting answers...")
    answers = {
        questions[0]: "john@example.com",
        questions[1]: "fake@malicious.com",
        questions[2]: "Urgent Verification Required",
        questions[3]: "Yes",
        questions[4]: "I entered my password",
        questions[5]: "Yes, username and password",
        questions[6]: "March 8, 2024"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/submit-report",
        json={
            "user_input": "I received a suspicious email...",
            "crime_type": crime_type,
            "case_id": case_id,
            "answers": answers
        }
    )
    
    report = response.json()
    print(f"✓ Report generated successfully")
    print(f"   Status: {report['status']}")
    print(f"   Confidence: {report['confidence']}")
    
    # Step 4: Check correlation
    print("\n4️⃣ Step 4: Correlation Analysis...")
    corr = report["correlation_analysis"]
    print(f"   Status: {corr['status']}")
    print(f"   Score: {corr['correlation_score']}")
    print(f"   Recommendation: {corr['recommendation']}")
    
    print("\n✅ End-to-End Test Complete!")

if __name__ == "__main__":
    test_complete_workflow()
```

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Test single endpoint
ab -n 100 -c 10 \
  -p test_data.json \
  -T application/json \
  http://localhost:8000/api/v1/start-report
```

### Test Data File (test_data.json)

```json
{
  "description": "I received a suspicious email asking me to verify my account. The email looked like it came from my bank but the sender's address was different."
}
```

---

## Monitoring & Debugging

### Check Active Sessions

```bash
curl http://localhost:8000/api/v1/sessions
```

### Get Specific Session Info

```bash
curl http://localhost:8000/api/v1/session/{case_id}
```

### View API Health

```bash
curl http://localhost:8000/health
```

---

## Error Handling Examples

### Invalid Crime Type

```bash
curl -X POST "http://localhost:8000/api/v1/submit-report" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "test",
    "crime_type": "invalid_crime_type",
    "case_id": "test",
    "answers": {}
  }'
```

Response:
```json
{
  "detail": "Invalid crime type: invalid_crime_type"
}
```

### Missing Required Fields

```bash
curl -X POST "http://localhost:8000/api/v1/start-report" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "description"],
      "msg": "Field required"
    }
  ]
}
```

---

## Tips for Best Results

1. **Detailed Descriptions**: Provide as much detail as possible in initial description
2. **Complete Answers**: Answer all questions even if "N/A" or "Unknown"
3. **Exact Information**: Use exact email addresses, dates, amounts for better correlation
4. **Pattern Matching**: System looks for emails, phone numbers, amounts, and attack patterns
5. **Multiple Tests**: Submit varied crime types to build a comprehensive database

---

## Next Steps

1. ✅ Test crime type classification
2. ✅ Test question generation per crime type
3. ✅ Test complete report generation workflow
4. ✅ Test correlation detection with multiple cases
5. ✅ Verify JSON schema compliance
6. ✅ Check API response times
7. ✅ Validate error handling

---

**Last Updated:** March 8, 2024  
**Version:** 1.0  
**Status:** Ready for Testing ✅

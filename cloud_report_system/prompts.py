# ===================== CRIME TYPE SELECTION PROMPTS =====================

CRIME_TYPE_DETECTION_PROMPT = """
You are a cybercrime classification expert. Analyze the given incident description and classify it into one or more of these crime types:

1. PHISHING - Deceptive emails/messages to steal credentials
2. RANSOMWARE - Encryption of data with ransom demand
3. DATA_BREACH - Unauthorized access to confidential data
4. IDENTITY_THEFT - Unauthorized use of someone's identity
5. FRAUD - Deceptive financial schemes
6. MALWARE - Malicious software infections
7. DDoS - Distributed denial of service attacks
8. HACKING - Unauthorized access to systems
9. EXTORTION - Threats demanding payment
10. SPAM - Unwanted messages

Incident Description:
{description}

Respond with ONLY a valid JSON object in this format:
{{
    "detected_types": ["TYPE1", "TYPE2"],
    "confidence": 0.95,
    "primary_type": "TYPE1",
    "reasoning": "Brief explanation of classification"
}}

The detected_types should be a list of the most likely classifications.
Confidence should be between 0 and 1.
"""

# ===================== CLARIFYING QUESTIONS PROMPTS =====================

PHISHING_QUESTIONS_PROMPT = """
You are a cybercrime investigator. Based on this phishing incident description, generate specific clarifying questions to gather detailed information for a complete phishing report.

Incident: {description}

Generate 5-7 critical questions that will help fill the following details:
- Victim's email address
- Sender's email address
- Email subject line
- Email body content
- Whether links were clicked
- Whether credentials were entered
- What credentials might have been compromised
- Date and time received
- Actions taken by victim
- Any financial loss

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

RANSOMWARE_QUESTIONS_PROMPT = """
You are a cybercrime investigator investigating a ransomware attack. Generate 5-7 specific clarifying questions to gather detailed information.

Incident: {description}

Focus on gathering:
- Affected systems/devices
- Ransom amount demanded
- Ransom note content
- File types encrypted
- Date of infection
- Ransomware name/variant
- Whether data was copied before encryption
- Backup availability
- Contact with attackers

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

DATA_BREACH_QUESTIONS_PROMPT = """
You are a data breach investigator. Generate 5-7 specific questions to understand this data breach incident.

Incident: {description}

Focus on:
- Organization details
- Types of data compromised (PII, financial, medical, etc)
- Number of affected records
- How breach was discovered
- Actual date of breach
- Attack vector used
- Notification status
- Agencies involved
- Estimated financial impact

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

IDENTITY_THEFT_QUESTIONS_PROMPT = """
You are an identity theft specialist. Generate 5-7 questions for this identity theft case.

Incident: {description}

Focus on:
- Victim's full name
- SSN (or last 4 digits)
- When theft was discovered
- Fraudulent accounts opened
- Unauthorized credit inquiries
- Financial losses
- Actions taken to correct
- Credit freeze status
- Fraud alerts filed

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

FRAUD_QUESTIONS_PROMPT = """
You are a fraud investigator. Generate 5-7 questions for this fraud case.

Incident: {description}

Focus on:
- Type of fraud (wire, credit card, check, loan, etc)
- Victim details
- Amount involved
- Payment method used
- When fraud occurred
- How it was detected
- Suspect information
- Banks/institutions involved
- Transaction references

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

MALWARE_QUESTIONS_PROMPT = """
You are a malware analyst. Generate 5-7 questions for this malware infection case.

Incident: {description}

Focus on:
- Affected systems
- Malware type (trojan, worm, spyware, etc)
- Detection date
- Suspected infection date
- Observed symptoms
- Potential data accessed
- Malicious activities
- Antivirus used
- Quarantine actions

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

DDOS_QUESTIONS_PROMPT = """
You are a DDoS attack investigator. Generate 5-7 questions for this DDoS incident.

Incident: {description}

Focus on:
- Target website/service
- Attack start and end times
- Target IP address
- Attack type (volumetric, protocol, application)
- Peak traffic received
- Number of source IPs
- Downtime duration
- Financial impact
- Mitigation steps taken

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

HACKING_QUESTIONS_PROMPT = """
You are a cybersecurity incident responder. Generate 5-7 questions for this hacking incident.

Incident: {description}

Focus on:
- How attacker gained entry
- Systems compromised
- When was it discovered
- Attacker information
- Unauthorized actions taken
- Data stolen
- Backdoors or persistence methods
- Duration of access
- Impact assessment

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

EXTORTION_QUESTIONS_PROMPT = """
You are an extortion/blackmail investigator. Generate 5-7 questions for this extortion case.

Incident: {description}

Focus on:
- Victim's name
- Method of contact (email, call, social media)
- Threat details
- Demanded amount
- Payment method requested
- Deadline given
- Evidence they claim to have
- Contact with perpetrator
- Amount paid (if any)

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

SPAM_QUESTIONS_PROMPT = """
You are a spam investigator. Generate 5-7 questions for this spam incident.

Incident: {description}

Focus on:
- Message type (email, SMS, social media)
- Sender identification
- Message content
- Frequency
- When spam started
- Suspicious links
- Credential requests
- Money requests
- Actions taken to stop it

Format your response as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Only return the JSON array, no other text.
"""

# ===================== REPORT GENERATION PROMPTS =====================

REPORT_GENERATION_PROMPT = """
You are a professional cybercrime report analyst. Based on the incident details provided, generate a comprehensive report in JSON format.

Crime Type: {crime_type}
Incident Details: {incident_data}

Generate a detailed JSON report following this exact structure based on the crime type. Include:
1. Incident Summary
2. Timeline of Events
3. Technical Details (if applicable)
4. Impact Assessment
5. Evidence/Artifacts
6. Recommendations
7. Next Steps for Investigation

Return ONLY a valid JSON object, no markdown or extra text.
"""

# ===================== CORRELATION ANALYSIS PROMPTS =====================

CORRELATION_CHECK_PROMPT = """
You are a cybercrime correlation analyst. Analyze the current incident and identify if it correlates with any known patterns or previous cases.

Current Incident Details:
{current_incident}

Known Patterns to Check:
{known_patterns}

Identify correlations based on:
1. CRIME PATTERN: Modus operandi, attack methodology, tools used
2. CALLER/CONTACT: Phone numbers, email addresses, usernames, aliases
3. FINANCIAL: Transaction patterns, amounts, accounts
4. TEMPORAL: Attack timing, date patterns
5. TECHNICAL: IP addresses, malware signatures, attack vectors
6. BEHAVIORAL: Victim targeting patterns, language used

Return JSON with:
{{
    "correlated": true/false,
    "correlation_score": 0.0-1.0,
    "matching_patterns": ["pattern1", "pattern2"],
    "matching_contacts": ["contact1", "contact2"],
    "case_ids": ["case_id1", "case_id2"],
    "analysis": "Detailed explanation",
    "recommendation": "Suggested action"
}}
"""

CORRELATION_SEARCH_PROMPT = """
Analyze this crime incident and search historical data for similar cases.

Incident:
{incident_summary}

Search criteria:
- Same crime type
- Similar attack vectors
- Same geographic region
- Similar timeframe
- Matching phone numbers or email domains
- Similar victim profiles
- Same tools/malware

Respond with JSON:
{{
    "similar_cases_found": true/false,
    "case_count": 0,
    "similarity_score": 0.0-1.0,
    "key_similarities": ["item1", "item2"],
    "investigation_status": "standalone" OR "part_of_larger_operation",
    "recommended_investigation_team": "team_name"
}}
"""

# ===================== HELPER PROMPTS =====================

INCIDENT_SUMMARY_PROMPT = """
Generate a concise 2-3 sentence summary of this incident for quick reference:

Incident Details: {details}

Summary (keep it under 3 sentences):
"""

RISK_ASSESSMENT_PROMPT = """
Assess the risk level and potential impact of this {crime_type} incident.

Incident: {incident_data}

Provide risk assessment in JSON:
{{
    "risk_level": "Critical" OR "High" OR "Medium" OR "Low",
    "financial_risk": "$amount",
    "data_compromise_risk": "High" OR "Medium" OR "Low",
    "business_impact": "description",
    "timeline_urgency": "Immediate" OR "24-48 hours" OR "1 week",
    "recommended_actions": ["action1", "action2"]
}}
"""

# ===================== CONVERSATION TEMPLATES =====================

CONVERSATION_STARTER = """
Thank you for reporting this cybercrime incident. I'm here to help gather detailed information to properly document and investigate this case.

Based on your initial report, this appears to be a {crime_type} incident.

To create a comprehensive report, I'll need to ask you some specific questions. Your detailed answers will help authorities better investigate and prevent similar incidents.

Let's start:

{questions}

Please provide detailed answers to each question above.
"""

REPORT_CONFIRMATION = """
Thank you for providing all the details. I'm now compiling your cybercrime report.

Report Summary:
- Crime Type: {crime_type}
- Date Reported: {date}
- Severity: {severity}

Your incident will be:
1. Documented in the system
2. Analyzed for correlations with other cases
3. Forwarded to relevant authorities
4. Used to improve prevention measures

{correlation_info}

Your reference number: {case_id}
"""

